# DMESGVIEWOR

> A graphical desktop tool for Debian Linux to visualize, filter, search and
> diagnose kernel logs — without touching the terminal.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green?logo=qt)](https://pypi.org/project/PyQt6/)
[![Platform](https://img.shields.io/badge/Platform-Debian%2012%2B-red?logo=debian)](https://www.debian.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Permissions](#permissions)
- [User Interface](#user-interface)
  - [Toolbar](#toolbar)
  - [Filter Panel](#filter-panel)
  - [Log Table](#log-table)
  - [Timeline Tab](#timeline-tab)
  - [Detected Issues Tab](#detected-issues-tab)
- [Feature Reference](#feature-reference)
  - [Log Display and Colorization](#log-display-and-colorization)
  - [Log Level Filter](#log-level-filter)
  - [Facility Filter](#facility-filter)
  - [Search](#search)
  - [Live Follow Mode](#live-follow-mode)
  - [Log Source Selection](#log-source-selection)
  - [Refresh](#refresh)
  - [Export](#export)
  - [Clear Kernel Buffer](#clear-kernel-buffer)
  - [Console Log Level](#console-log-level)
  - [Kernel Error Timeline](#kernel-error-timeline)
  - [Automatic Critical Error Detection](#automatic-critical-error-detection)
  - [journalctl Correlation](#journalctl-correlation)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

DMESGVIEWOR replaces complex `dmesg` command-line usage with an intuitive
graphical interface. It provides real-time log streaming, advanced filtering,
automatic critical error detection and graphical timeline analysis — all in a
single desktop application built with Python and PyQt6.

---

## Screenshots

> _Screenshots will be added after the first release._

---

## Features

| Feature | Description |
|---|---|
| Colour-coded log table | Rows coloured by severity (emerg → debug) |
| Level filter | Checkboxes to show/hide any combination of log levels |
| Facility filter | Multi-select list to filter by kernel facility |
| Text search | Regex-capable, case-sensitive option, applied on top of level/facility filters |
| Live follow mode | Real-time streaming via `dmesg -w` or `journalctl -kf` |
| Kernel Timeline | Per-minute histogram of errors, warnings and info logs |
| Detected Issues | Automatic pattern-based detection of critical kernel events |
| journalctl source | Switch between dmesg buffer and systemd kernel journal |
| Correlation view | Merged table with a Source column (dmesg / journalctl) |
| Export | Save visible logs to TXT, JSON, CSV or HTML |
| Clear buffer | Wipe the kernel ring buffer (`dmesg -C`) with confirmation |
| Console log level | Set the kernel console log level (`dmesg -n`) via dropdown |
| Sudo authentication | Built-in password dialog when elevated privileges are required |

---

## Requirements

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Runtime |
| PyQt6 | 6.4+ | GUI framework |
| pyqtgraph | 0.13+ | Timeline chart |
| util-linux | any | Provides `dmesg` |
| systemd | any (optional) | Provides `journalctl` |

---

## Installation

### 1 — System packages

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv util-linux
```

### 2 — Clone the repository

```bash
git clone https://github.com/<your-username>/dmesgviewor.git
cd dmesgviewor
```

### 3 — Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

```bash
python3 main.py
```

If `dmesg` access is restricted on your system (see [Permissions](#permissions)),
the application will display a password dialog on startup.

---

## Permissions

On Debian 12 and later, access to the kernel ring buffer is restricted by
default (`kernel.dmesg_restrict = 1`). DMESGVIEWOR detects this situation and
offers several solutions.

### Option A — Add your user to the `adm` group (recommended)

This is the cleanest solution. Members of the `adm` group can read kernel logs
without elevated privileges.

```bash
sudo usermod -aG adm $USER
```

**Log out and log back in** for the group change to take effect.

### Option B — Enter your sudo password in the application

When DMESGVIEWOR detects a permission error, it automatically shows a password
dialog. Enter your sudo password to authenticate for the current session. The
password is stored only in memory and discarded when the application closes.

### Option C — Run with pkexec

```bash
pkexec python3 main.py
```

### Option D — Disable the restriction system-wide (not recommended)

```bash
sudo sysctl kernel.dmesg_restrict=0
```

This change affects all users and is not persistent across reboots. To make it
persistent, add `kernel.dmesg_restrict=0` to `/etc/sysctl.conf`.

---

## User Interface

The interface is organised into four areas:

```
┌─────────────────────────────────────────────────────────────┐
│  Toolbar                                                    │
├──────────────┬──────────────────────────────────────────────┤
│              │  [ Logs ] [ Timeline ] [ Detected Issues ]   │
│  Filter      │                                              │
│  Panel       │  Log Table / Timeline / Issues               │
│  (left)      │                                              │
├──────────────┴──────────────────────────────────────────────┤
│  Status bar: log count | follow status | permissions        │
└─────────────────────────────────────────────────────────────┘
```

### Toolbar

Located at the top of the window. Contains all action buttons and controls.

| Control | Description |
|---|---|
| **Source** dropdown | Switch between `dmesg buffer` and `journalctl kernel` |
| **⟳ Refresh** | Reload all logs from the selected source |
| **▶ Follow** | Start live log streaming |
| **⏸ Pause** | Stop live streaming |
| **⬇ Export** | Export visible (filtered) logs |
| **🗑 Clear Buffer** | Clear the kernel ring buffer |
| **Console level** dropdown | Set the kernel console log level (0 emerg → 7 debug) |
| **Search** field | Text filter applied to the Message column |
| **Regex** checkbox | Interpret the search field as a regular expression |
| **Case** checkbox | Make the search case-sensitive |

### Filter Panel

Located on the left side of the window.

**Log Levels** — Eight checkboxes, one per severity level. Uncheck a level to
hide all entries of that severity from the log table. All levels are enabled by
default.

**Facilities** — A multi-select list. Select one or more facilities to show only
entries from those sources. If nothing is selected, all facilities are shown.

> **Note:** The Filter Panel and the Search bar work together as a combined
> filter. An entry must match **both** the level/facility selection **and** the
> search text to be visible.

### Log Table

A scrollable, sortable table of kernel log entries. Click any column header to
sort. Rows are colour-coded by severity level (see
[Log Display and Colorization](#log-display-and-colorization)).

**Columns:**

| Column | Content |
|---|---|
| Timestamp | Seconds since boot (dmesg) or date-time (journalctl) |
| Level | Severity name: emerg, alert, crit, err, warn, notice, info, debug |
| Facility | Origin facility: kern, user, daemon, auth, syslog, etc. |
| Source | `dmesg` or `journalctl` |
| Message | The raw log message |

### Timeline Tab

A graphical histogram showing the number of log entries per minute, broken down
by severity. See [Kernel Error Timeline](#kernel-error-timeline).

### Detected Issues Tab

A panel listing kernel events that match critical patterns. See
[Automatic Critical Error Detection](#automatic-critical-error-detection).

---

## Feature Reference

### Log Display and Colorization

Every row in the log table is coloured according to its severity level:

| Level | Value | Background | Text |
|---|---|---|---|
| emerg | 0 | Red | White |
| alert | 1 | Red | White |
| crit | 2 | Dark red | White |
| err | 3 | White | Red |
| warn | 4 | White | Orange |
| notice | 5 | White | Dark blue |
| info | 6 | White | Black |
| debug | 7 | White | Gray |

---

### Log Level Filter

**Location:** Filter Panel → Log Levels section (left side)

Eight checkboxes corresponding to the eight kernel severity levels. Uncheck any
level to remove those entries from the table view. The filtering is applied
instantly in memory without re-running `dmesg`.

**Example use cases:**
- Uncheck `debug` and `info` to focus on warnings and above.
- Uncheck everything except `err` and `crit` to see only critical errors.

---

### Facility Filter

**Location:** Filter Panel → Facilities section (left side)

A multi-select list showing the main kernel facilities:

| Facility | Number | Typical origin |
|---|---|---|
| kern | 0 | Core kernel messages |
| user | 1 | User-space processes |
| daemon | 3 | System daemons |
| auth | 4 | Authentication subsystem |
| syslog | 5 | Syslog internal messages |
| lpr | 6 | Line printer subsystem |
| news | 7 | Network news subsystem |
| cron | 9 | Cron scheduler |

Click to select individual facilities. Hold `Ctrl` or `Shift` to select
multiple. If no facility is selected, all are shown.

---

### Search

**Location:** Toolbar → Search field

Filters the Message column of the log table. The search is applied on top of
the level and facility filters: an entry must pass all three checks to appear.

| Option | Behaviour |
|---|---|
| Plain text (default) | Case-insensitive substring match |
| **Regex** checked | The search field is interpreted as a Python regular expression |
| **Case** checked | The match becomes case-sensitive |

**Regex examples:**

```
usb.*disconnect        Match lines containing "usb" followed by "disconnect"
(error|fail|denied)    Match lines containing any of the three words
^\[.*PCIe             Match lines whose message starts with "[" and contains "PCIe"
```

> **Important:** Search and Console Level are completely independent features.
> Search filters what is **displayed** in the application. Console Level sets
> a **kernel parameter** that controls what is printed to the system console
> (`/dev/console`) — it has no effect on the application display.

---

### Live Follow Mode

**Location:** Toolbar → ▶ Follow / ⏸ Pause buttons

Streams new kernel log entries in real-time as they are produced by the kernel.

| Source | Command used |
|---|---|
| dmesg buffer | `dmesg -w --json` |
| journalctl kernel | `journalctl -kf -o json` |

New entries are appended to the bottom of the log table and the view scrolls
automatically. The Timeline and Detected Issues panels are updated
incrementally.

Click **⏸ Pause** to stop streaming. The existing log entries remain visible.
Click **▶ Follow** again to resume.

The status bar shows **Follow: ON** when streaming is active.

> Switching the log source (dmesg ↔ journalctl) while Follow is active will
> automatically stop the follow session before switching.

---

### Log Source Selection

**Location:** Toolbar → Source dropdown

| Option | Description |
|---|---|
| `dmesg buffer` | Reads the kernel ring buffer via `dmesg --json` |
| `journalctl kernel` | Reads systemd's persistent kernel journal via `journalctl -k -o json` |

The main difference between the two sources:

- **dmesg buffer** is a circular ring buffer of fixed size (~512 KB by default).
  Old entries are discarded as new ones arrive. The buffer is lost on reboot.
- **journalctl** reads from the persistent systemd journal on disk. It can
  provide kernel logs from previous boots.

Both sources support the same level/facility filters, text search, live follow
mode and export.

---

### Refresh

**Location:** Toolbar → ⟳ Refresh button

Runs a fresh one-shot read of the selected log source and replaces the current
table content. The Timeline and Detected Issues panels are also refreshed.

Useful after a system event to see the latest kernel messages without restarting
the application.

---

### Export

**Location:** Toolbar → ⬇ Export button

Exports the **currently visible (filtered) entries** to a file. Only entries
that pass the active level, facility and search filters are exported.

| Format | Extension | Description |
|---|---|---|
| Text | `.txt` | One entry per line, human-readable |
| JSON | `.json` | Array of objects with all fields |
| CSV | `.csv` | Spreadsheet-compatible, UTF-8 |
| HTML | `.html` | Colour-coded table, ready to open in a browser |

---

### Clear Kernel Buffer

**Location:** Toolbar → 🗑 Clear Buffer button

Runs `dmesg -C` to wipe the kernel ring buffer. A confirmation dialog is shown
before the action is executed. The log table and all panels are cleared
immediately after.

> **Warning:** This action is irreversible. All kernel log entries currently in
> the ring buffer will be permanently deleted.

This operation requires elevated privileges (`CAP_SYSLOG`). If the application
does not have sufficient permissions, the sudo password dialog will appear.

---

### Console Log Level

**Location:** Toolbar → Console level dropdown

Sets the **kernel console log level** via `dmesg -n <level>`.

This is a **kernel parameter**, not an application display filter. It controls
which log messages the kernel prints to `/dev/console` (the system terminal) in
real-time. It has **no effect** on what is displayed in DMESGVIEWOR.

| Dropdown value | `dmesg -n` sent | Effect |
|---|---|---|
| 0 emerg | `-n 1` | Only emergency messages reach the console |
| 1 alert | `-n 2` | Emergencies + alerts |
| 2 crit | `-n 3` | + critical |
| 3 err | `-n 4` | + errors |
| 4 warn | `-n 5` | + warnings |
| 5 notice | `-n 6` | + notices |
| 6 info | `-n 7` | + informational |
| 7 debug | `-n 8` | All messages (default on most systems) |

This operation requires elevated privileges. The sudo password dialog will
appear if needed.

---

### Kernel Error Timeline

**Location:** Timeline tab

A histogram showing the number of log entries per one-minute bucket, with
three colour-coded series:

| Colour | Series |
|---|---|
| Red | Errors and above (emerg, alert, crit, err — levels 0–3) |
| Orange | Warnings (level 4) |
| Blue | Info, notice, debug (levels 5–7) |

**Interactions:**

| Action | Result |
|---|---|
| Scroll wheel | Zoom in/out on the time axis |
| Click and drag | Pan the view |
| Drag the region handles | Select a time window |
| Click **Apply time window** | Filter the log table to the selected time range |
| Click **Clear selection** | Remove the time range filter and restore all entries |

The timeline updates automatically when:
- **Refresh** is clicked (full redraw)
- **Follow mode** is active (incremental update per new batch)

> **Requirement:** The Timeline tab requires the `pyqtgraph` package. If it is
> not installed, the tab displays an installation message.

---

### Automatic Critical Error Detection

**Location:** Detected Issues tab

DMESGVIEWOR automatically scans all loaded log entries for known critical
patterns and lists them in the Detected Issues panel.

**Detected patterns:**

| Category | Pattern matched | Severity |
|---|---|---|
| Kernel Panic | `kernel panic` | critical |
| Kernel BUG | `BUG:` | critical |
| Kernel Oops | `Oops:` | critical |
| OOM | `Out of memory` | critical |
| Hardware Error | `hardware error` | critical |
| Watchdog Timeout | `watchdog.*timeout` | critical |
| MCE / Machine Check | `MCE.*error`, `Machine Check` | critical |
| NMI | `NMI` | critical |
| Soft Lockup | `soft lockup` | critical |
| Segfault | `segfault` | error |
| Call Trace | `Call Trace:` | error |
| I/O Error | `I/O error` | error |
| EXT4 FS Error | `EXT4-fs error` | error |
| PCIe Error | `PCIe.*error` | error |
| ACPI Error | `ACPI.*error` | error |
| EDAC Error | `EDAC.*error` | error |
| Hung Task | `hung_task` | error |
| USB Disconnect | `USB disconnect` | warning |

**Severity colour coding:**

| Severity | Row colour |
|---|---|
| critical | Red |
| error | Orange |
| warning | Yellow |

**Interactions:**

| Action | Result |
|---|---|
| Double-click an issue | Switches to the Logs tab and scrolls to the corresponding entry |
| Click **Export issues (JSON)** | Saves the issue list to a `.json` file |

The panel refreshes automatically on Refresh and incrementally during Follow
mode.

---

### journalctl Correlation

**Location:** Toolbar → Source dropdown → `journalctl kernel`

When the `journalctl kernel` source is selected, the application reads kernel
logs from the systemd journal instead of the dmesg ring buffer. The journalctl
source:

- Persists across reboots (stored on disk by systemd)
- Provides absolute timestamps (date + time) instead of seconds since boot
- Supports the same filters, search, follow mode and export

**Correlation mode:**

Both sources populate the same log table with a **Source** column that
identifies the origin of each entry (`dmesg` or `journalctl`). To correlate
events from both sources simultaneously:

1. Load one source and export the visible entries.
2. Switch to the other source.
3. Use the Timeline to identify overlapping time windows.

A future version will provide a merged view that loads both sources
simultaneously.

---

## Architecture

DMESGVIEWOR follows the **Model-View-Controller (MVC)** pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│  Backend (data acquisition)                                     │
│  dmesg_runner.py  ─┐                                           │
│  journal_runner.py ┤──► json_parser.py ──► LogEntry objects    │
└────────────────────┼────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│  Model                                                          │
│  LogEntry (dataclass)                                           │
│  LogTableModel (QAbstractTableModel) ── max 50 000 entries      │
│  LogFilterProxyModel (QSortFilterProxyModel)                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│  Controller                                                     │
│  MainController — connects signals, drives background threads   │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│  View (UI)                                                      │
│  MainWindow ── AppToolBar                                       │
│            ├── FilterPanel                                      │
│            ├── LogTableView                                     │
│            ├── TimelineWidget                                   │
│            └── IssuesPanel                                      │
└─────────────────────────────────────────────────────────────────┘
```

Background operations (log loading, live follow) run in dedicated `QThread`
instances. Follow workers use `subprocess.Popen` with line-by-line reading
rather than `QProcess`, which must not be used outside the main thread.

---

## Project Structure

```
dmesgviewor/
├── main.py                   # Entry point — python3 main.py
├── app.py                    # QApplication setup
│
├── backend/
│   ├── __init__.py
│   ├── dmesg_runner.py       # run_dmesg_once(), DmesgFollowWorker
│   ├── journal_runner.py     # run_journal_once(), JournalFollowWorker
│   └── json_parser.py        # Parse dmesg/journalctl JSON → LogEntry
│
├── models/
│   ├── __init__.py
│   ├── log_entry.py          # LogEntry dataclass, level/facility maps
│   └── log_table_model.py    # QAbstractTableModel + QSortFilterProxyModel
│
├── controllers/
│   ├── __init__.py
│   └── main_controller.py    # Wires all signals, manages threads
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py        # MainWindow: layout, tabs, status bar
│   ├── toolbar.py            # AppToolBar: all action buttons + search
│   ├── filter_panel.py       # Level checkboxes + facility list
│   ├── log_table.py          # LogTableView (QTableView wrapper)
│   ├── timeline_widget.py    # PyQtGraph histogram + region selector
│   └── issues_panel.py       # Pattern detection + issue list
│
├── utils/
│   ├── __init__.py
│   ├── privileges.py         # Sudo password dialog
│   ├── exporter.py           # TXT / JSON / CSV / HTML writers
│   └── time_utils.py         # Boot timestamp → epoch conversion
│
├── resources/
│   └── icons/                # (reserved for future icons)
│
├── requirements.txt
└── README.md
```

---

## Security Notes

- DMESGVIEWOR **reads** the kernel ring buffer but never writes to it unless you
  explicitly use the Clear Buffer or Console Level features.
- The sudo password entered in the authentication dialog is stored **in memory
  only** for the duration of the session and is never written to disk.
- No network connection is made at any time. All operations are local.
- `dmesg -C` (clear buffer) and `dmesg -n` (set console log level) require
  `CAP_SYSLOG` or root access.
- The recommended permission setup (Option A — `adm` group) grants read-only
  access to kernel logs and does not require any elevated privileges at runtime.

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository and create a feature branch.
2. Follow [PEP 8](https://peps.python.org/pep-0008/) coding style.
3. Keep the MVC structure: backend logic stays in `backend/`, UI code stays in
   `ui/`, business logic stays in `controllers/`.
4. Test on Debian 12+ with Python 3.10+.
5. Open a pull request with a clear description of the change.

### Reporting Issues

Please include:
- Your Debian version (`cat /etc/debian_version`)
- Python version (`python3 --version`)
- PyQt6 version (`pip show PyQt6 | grep Version`)
- util-linux version (`dmesg --version`)
- The full error message or traceback

---

## License

MIT License

Copyright (c) 2024 DMESGVIEWOR contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
