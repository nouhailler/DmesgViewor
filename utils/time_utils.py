"""Timestamp helpers."""
from __future__ import annotations
import time
from datetime import datetime


def boot_offset() -> float:
    """Return the system boot time as a Unix timestamp."""
    try:
        with open("/proc/uptime") as f:
            uptime_s = float(f.read().split()[0])
        return time.time() - uptime_s
    except Exception:
        return 0.0


def dmesg_ts_to_epoch(ts: float) -> float:
    """Convert a dmesg boot-relative timestamp to Unix epoch."""
    return boot_offset() + ts


def format_dmesg_ts(ts: float, source: str = "dmesg") -> str:
    if source == "journalctl":
        dt = datetime.fromtimestamp(ts)
    else:
        epoch = dmesg_ts_to_epoch(ts)
        dt = datetime.fromtimestamp(epoch)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
