"""LogEntry data model."""
from dataclasses import dataclass, field
from typing import Optional


LEVEL_NAMES = {
    0: "emerg",
    1: "alert",
    2: "crit",
    3: "err",
    4: "warn",
    5: "notice",
    6: "info",
    7: "debug",
}

FACILITY_NAMES = {
    0: "kern",
    1: "user",
    2: "mail",
    3: "daemon",
    4: "auth",
    5: "syslog",
    6: "lpr",
    7: "news",
    8: "uucp",
    9: "cron",
    10: "authpriv",
    11: "ftp",
    16: "local0",
    17: "local1",
    18: "local2",
    19: "local3",
    20: "local4",
    21: "local5",
    22: "local6",
    23: "local7",
}


@dataclass
class LogEntry:
    timestamp: float          # seconds since boot (dmesg) or epoch (journalctl)
    pri: int
    message: str
    raw_json: dict = field(default_factory=dict)
    source: str = "dmesg"     # "dmesg" or "journalctl"

    @property
    def level(self) -> int:
        return self.pri & 7

    @property
    def facility(self) -> int:
        return self.pri >> 3

    @property
    def level_name(self) -> str:
        return LEVEL_NAMES.get(self.level, str(self.level))

    @property
    def facility_name(self) -> str:
        return FACILITY_NAMES.get(self.facility, str(self.facility))
