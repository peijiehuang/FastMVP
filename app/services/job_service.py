"""APScheduler integration service for scheduled task management."""
import ast
import asyncio
import importlib
import logging
import re
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.session import async_session_factory
from app.models.sys_job_log import SysJobLog

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: AsyncIOScheduler | None = None

# Track running jobs for concurrency control
_running_jobs: set[int] = set()


def _make_job_id(job_id: int) -> str:
    return f"sys_job_{job_id}"


def _parse_invoke_target(invoke_target: str) -> tuple[str, str, list]:
    """Parse 'module.func(args...)' into (module, func, [args])."""
    match = re.match(r"^(\w+)\.(\w+)(?:\((.*)\))?$", invoke_target.strip())
    if not match:
        raise ValueError(f"Invalid invokeTarget: {invoke_target}")
    module_name = match.group(1)
    func_name = match.group(2)
    args_str = match.group(3)
    args = []
    if args_str is not None and args_str.strip():
        # Normalize Python-style booleans: true/false -> True/False
        normalized = args_str.replace("true", "True").replace("false", "False")
        args = list(ast.literal_eval(f"({normalized},)"))
    return module_name, func_name, args


def _cron_to_trigger(cron_expression: str) -> CronTrigger:
    """Convert Quartz 6/7-field cron to APScheduler CronTrigger."""
    parts = cron_expression.split()
    if len(parts) < 6:
        raise ValueError(f"Invalid cron: {cron_expression}")
    # Quartz '?' means 'no specific value', map to '*'
    parts = [p.replace("?", "*") for p in parts]
    kwargs = {
        "second": parts[0],
        "minute": parts[1],
        "hour": parts[2],
        "day": parts[3],
        "month": parts[4],
        "day_of_week": parts[5],
    }
    if len(parts) >= 7:
        kwargs["year"] = parts[6]
    return CronTrigger(**kwargs)


def _misfire_grace(policy: str) -> int:
    """1=immediate(large grace), 2=once(moderate), 3=discard(tiny)."""
    return {
        "1": 3600,
        "2": 300,
    }.get(policy, 1)


async def _execute_job(
    job_id: int, job_name: str, job_group: str,
    invoke_target: str, concurrent: str,
):
    """Execute a job and record the log."""
    if concurrent == "1" and job_id in _running_jobs:
        logger.warning(f"Job {job_id} already running, skip (concurrent=forbid)")
        return

    _running_jobs.add(job_id)
    status = "0"
    job_message = ""
    exception_info = ""

    try:
        module_name, func_name, args = _parse_invoke_target(invoke_target)
        module = importlib.import_module(f"app.tasks.{module_name}")
        func = getattr(module, func_name)
        if asyncio.iscoroutinefunction(func):
            result = await func(*args)
        else:
            result = func(*args)
        job_message = str(result) if result else "执行成功"
    except Exception as e:
        status = "1"
        job_message = "执行失败"
        exception_info = str(e)[:2000]
        logger.exception(f"Job {job_id} failed: {e}")
    finally:
        _running_jobs.discard(job_id)
        try:
            async with async_session_factory() as session:
                session.add(SysJobLog(
                    job_name=job_name,
                    job_group=job_group,
                    invoke_target=invoke_target,
                    job_message=(job_message or "")[:500],
                    status=status,
                    exception_info=exception_info,
                    create_time=datetime.now(),
                ))
                await session.commit()
        except Exception:
            logger.exception("Failed to save job log")


def add_job_to_scheduler(job):
    """Add/replace a job in APScheduler from a SysJob instance."""
    if scheduler is None:
        return
    job_id_str = _make_job_id(job.job_id)
    try:
        scheduler.remove_job(job_id_str)
    except Exception:
        pass
    scheduler.add_job(
        _execute_job,
        trigger=_cron_to_trigger(job.cron_expression),
        id=job_id_str,
        args=[job.job_id, job.job_name, job.job_group,
              job.invoke_target, job.concurrent],
        misfire_grace_time=_misfire_grace(job.misfire_policy),
        replace_existing=True,
    )


def remove_job_from_scheduler(job_id: int):
    if scheduler is None:
        return
    try:
        scheduler.remove_job(_make_job_id(job_id))
    except Exception:
        pass


async def run_job_once(job):
    """Execute a job immediately (once)."""
    await _execute_job(
        job.job_id, job.job_name, job.job_group,
        job.invoke_target, job.concurrent,
    )


def get_next_fire_time(job_id: int) -> datetime | None:
    if scheduler is None:
        return None
    try:
        apjob = scheduler.get_job(_make_job_id(job_id))
        if apjob and apjob.next_run_time:
            return apjob.next_run_time
    except Exception:
        pass
    return None


async def init_scheduler(app=None):
    """Initialize scheduler and load enabled jobs from DB."""
    global scheduler
    scheduler = AsyncIOScheduler()
    scheduler.start()
    async with async_session_factory() as session:
        from app.crud.crud_job import crud_job
        jobs = await crud_job.get_all_enabled(session)
        for job in jobs:
            try:
                add_job_to_scheduler(job)
                logger.info(f"Scheduled job {job.job_id}: {job.job_name}")
            except Exception as e:
                logger.error(f"Failed to schedule job {job.job_id}: {e}")
    if app:
        app.state.scheduler = scheduler
    logger.info(f"Scheduler started, {len(scheduler.get_jobs())} jobs loaded")


async def shutdown_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info("Scheduler shutdown")
