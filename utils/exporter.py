"""Export filtered log entries to various formats."""
from __future__ import annotations
import csv
import json
import html
from typing import Iterable

from models.log_entry import LogEntry
from utils.time_utils import format_dmesg_ts


def _fmt(entry: LogEntry) -> dict:
    return {
        "timestamp": format_dmesg_ts(entry.timestamp, entry.source),
        "level": entry.level_name,
        "facility": entry.facility_name,
        "source": entry.source,
        "message": entry.message,
    }


def export_txt(entries: Iterable[LogEntry], path: str):
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            d = _fmt(e)
            f.write(f"[{d['timestamp']}] [{d['level']:6}] [{d['facility']:8}] {d['message']}\n")


def export_json(entries: Iterable[LogEntry], path: str):
    data = [_fmt(e) for e in entries]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_csv(entries: Iterable[LogEntry], path: str):
    rows = [_fmt(e) for e in entries]
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def export_html(entries: Iterable[LogEntry], path: str):
    LEVEL_CSS = {
        "emerg":  "background:#ff0000;color:white",
        "alert":  "background:#ff0000;color:white",
        "crit":   "background:#8b0000;color:white",
        "err":    "color:red",
        "warn":   "color:#ff8c00",
        "notice": "color:#00008b",
        "info":   "color:black",
        "debug":  "color:#808080",
    }
    rows_html = []
    for e in entries:
        d = _fmt(e)
        style = LEVEL_CSS.get(d["level"], "")
        row = (
            f"<tr style='{style}'>"
            f"<td>{html.escape(d['timestamp'])}</td>"
            f"<td>{html.escape(d['level'])}</td>"
            f"<td>{html.escape(d['facility'])}</td>"
            f"<td>{html.escape(d['source'])}</td>"
            f"<td>{html.escape(d['message'])}</td>"
            "</tr>"
        )
        rows_html.append(row)
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<title>DMESGVIEWOR Export</title>"
            "<style>table{border-collapse:collapse;width:100%}"
            "td,th{border:1px solid #ccc;padding:4px;font-family:monospace;font-size:12px}"
            "th{background:#eee}</style></head><body>"
            "<table><tr><th>Timestamp</th><th>Level</th><th>Facility</th>"
            "<th>Source</th><th>Message</th></tr>"
        )
        f.write("\n".join(rows_html))
        f.write("</table></body></html>")


def export_issues_json(issues: list[dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
