import platform

import psutil
from fastapi import APIRouter, Depends

from app.core.deps import has_permi
from app.core.response import AjaxResult

router = APIRouter()


@router.get("")
async def get_server_info(
    current_user: dict = Depends(has_permi("monitor:server:list")),
):
    """Get server system information using psutil."""
    # CPU
    cpu_count = psutil.cpu_count(logical=True)
    cpu_percent = psutil.cpu_percent(interval=1)

    # Memory
    mem = psutil.virtual_memory()

    # Disk
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "dirName": part.mountpoint,
                "sysTypeName": part.fstype,
                "typeName": part.device,
                "total": _format_bytes(usage.total),
                "used": _format_bytes(usage.used),
                "free": _format_bytes(usage.free),
                "usage": round(usage.percent, 2),
            })
        except (PermissionError, OSError):
            continue

    # Python process info (replacing JVM)
    import sys
    import os
    process = psutil.Process(os.getpid())
    proc_mem = process.memory_info()

    data = {
        "cpu": {
            "cpuNum": cpu_count,
            "total": cpu_percent,
            "sys": 0,
            "used": cpu_percent,
            "wait": 0,
            "free": round(100 - cpu_percent, 2),
        },
        "mem": {
            "total": _format_bytes(mem.total),
            "used": _format_bytes(mem.used),
            "free": _format_bytes(mem.available),
            "usage": round(mem.percent, 2),
        },
        "sys": {
            "computerName": platform.node(),
            "computerIp": _get_local_ip(),
            "osName": f"{platform.system()} {platform.release()}",
            "osArch": platform.machine(),
            "userDir": os.getcwd(),
        },
        "sysFiles": disks,
        "jvm": {
            "total": _format_bytes(proc_mem.rss),
            "max": _format_bytes(proc_mem.vms),
            "free": _format_bytes(proc_mem.vms - proc_mem.rss),
            "usage": round(proc_mem.rss / proc_mem.vms * 100, 2) if proc_mem.vms else 0,
            "version": sys.version,
            "home": sys.executable,
            "name": "Python",
            "startTime": "",
            "runTime": "",
            "inputArgs": "",
        },
    }
    return AjaxResult.success(data=data)


def _format_bytes(size: int) -> str:
    """Convert bytes to human-readable GB format."""
    gb = size / (1024 ** 3)
    return f"{gb:.2f} GB"


def _get_local_ip() -> str:
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
