"""Parse dmesg / journalctl JSON output into LogEntry objects."""
from __future__ import annotations
import json

from models.log_entry import LogEntry, LEVEL_NAMES, FACILITY_NAMES


def _parse_pri(pri_val) -> int:
    """
    Convert a pri value to an integer.
    With --decode, dmesg outputs strings like "kern.info".
    Without --decode (recommended), it is an integer like 14.
    """
    if isinstance(pri_val, int):
        return pri_val
    if isinstance(pri_val, float):
        return int(pri_val)
    # String form: "kern.info", "user.err", etc.
    s = str(pri_val)
    if "." in s:
        fac_name, lvl_name = s.split(".", 1)
        fac = next((k for k, v in FACILITY_NAMES.items() if v == fac_name), 0)
        lvl = next((k for k, v in LEVEL_NAMES.items() if v == lvl_name), 6)
        return (fac << 3) | lvl
    try:
        return int(s)
    except ValueError:
        return 6   # default: info


def parse_dmesg_json(raw: str) -> list[LogEntry]:
    """
    Parse output of `dmesg --json`.

    util-linux dmesg --json produces:
        {"dmesg": [{"pri": 14, "time": "12345.678901", "msg": "..."}, ...]}

    The "time" field is seconds since boot as a string "sec.usec".
    """
    raw = raw.strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: newline-delimited JSON
        entries = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                try:
                    obj = json.loads(line)
                    entry = _obj_to_entry_dmesg(obj)
                    if entry:
                        entries.append(entry)
                except json.JSONDecodeError:
                    pass
        return entries

    # Unwrap {"dmesg": [...]} envelope if present
    if isinstance(data, dict):
        data = data.get("dmesg", list(data.values())[0] if data else [])
    if not isinstance(data, list):
        data = [data]

    entries = []
    for obj in data:
        entry = _obj_to_entry_dmesg(obj)
        if entry:
            entries.append(entry)
    return entries


def _obj_to_entry_dmesg(obj: dict) -> LogEntry | None:
    try:
        pri = _parse_pri(obj.get("pri", 6))
        # dmesg --json uses "time" as "sec.usec" string or float
        ts_raw = obj.get("time", obj.get("timestamp", "0"))
        ts = float(ts_raw)
        msg = obj.get("msg", obj.get("message", ""))
        return LogEntry(timestamp=ts, pri=pri, message=str(msg), raw_json=obj, source="dmesg")
    except Exception:
        return None


def parse_dmesg_json_line(line: str) -> LogEntry | None:
    """Parse a single JSON line from `dmesg -w --json` (follow mode)."""
    line = line.strip()
    if not line:
        return None
    try:
        obj = json.loads(line)
        return _obj_to_entry_dmesg(obj)
    except json.JSONDecodeError:
        return None


def parse_journal_json_line(line: str) -> LogEntry | None:
    """Parse a single JSON line from journalctl -o json output."""
    line = line.strip()
    if not line:
        return None
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None

    try:
        pri = _parse_pri(obj.get("PRIORITY", 6))
        # journalctl uses __REALTIME_TIMESTAMP in microseconds since epoch
        ts_us = int(obj.get("__REALTIME_TIMESTAMP", 0))
        ts = ts_us / 1_000_000
        msg = obj.get("MESSAGE", "")
        if isinstance(msg, list):
            msg = " ".join(str(m) for m in msg)
        return LogEntry(timestamp=ts, pri=pri, message=str(msg), raw_json=obj, source="journalctl")
    except Exception:
        return None
