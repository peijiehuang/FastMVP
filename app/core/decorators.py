"""Operation log decorator for recording API operations."""

import functools
import json
import time
from datetime import datetime

from fastapi import Request

from app.db.session import async_session_factory
from app.models.sys_oper_log import SysOperLog


def log_operation(title: str, business_type: int = 0):
    """Decorator for recording operation logs.

    Equivalent to RuoYi @Log annotation.

    Args:
        title: Module title (e.g., "用户管理")
        business_type: Operation type (0=other, 1=insert, 2=update, 3=delete, etc.)
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = kwargs.get("request")
            current_user: dict | None = kwargs.get("current_user")

            start_time = time.time()
            status = 0
            error_msg = ""
            json_result = ""

            try:
                result = await func(*args, **kwargs)
                if isinstance(result, dict):
                    json_result = json.dumps(result, default=str, ensure_ascii=False)[:2000]
                return result
            except Exception as e:
                status = 1
                error_msg = str(e)[:2000]
                raise
            finally:
                cost_time = int((time.time() - start_time) * 1000)

                oper_log = SysOperLog(
                    title=title,
                    business_type=business_type,
                    method=f"{func.__module__}.{func.__qualname__}",
                    request_method=request.method if request else "",
                    oper_name=current_user.get("user_name", "") if current_user else "",
                    dept_name=current_user.get("dept_name", "") if current_user else "",
                    oper_url=str(request.url.path) if request else "",
                    oper_ip=request.client.host if request and request.client else "",
                    status=status,
                    error_msg=error_msg,
                    json_result=json_result,
                    oper_time=datetime.now(),
                    cost_time=cost_time,
                )

                # Save log in a separate session (fire-and-forget)
                try:
                    async with async_session_factory() as session:
                        session.add(oper_log)
                        await session.commit()
                except Exception:
                    pass  # Don't let log failure affect the main request

        return wrapper
    return decorator
