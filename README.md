<![CDATA[<div align="center">

# 🐧 DMESGVIEWOR

### Graphical kernel log viewer for Debian Linux

*Visualize, filter, search and diagnose kernel logs — without touching the terminal.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4%2B-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![Debian](https://img.shields.io/badge/Debian-12%2B-A81D33?style=for-the-badge&logo=debian&logoColor=white)](https://www.debian.org/)
[![License](https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge)](LICENSE)
[![util-linux](https://img.shields.io/badge/util--linux-dmesg-555555?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/util-linux/util-linux)

</div>

---

## 📋 Table of Contents

- [🔭 Overview](#-overview)
- [✨ Features](#-features)
- [⚙️ Requirements](#️-requirements)
- [🚀 Installation](#-installation)
- [▶️ Running the Application](#️-running-the-application)
- [🔑 Permissions](#-permissions)
- [🖥️ User Interface](#️-user-interface)
  - [🔧 Toolbar](#-toolbar)
  - [🎛️ Filter Panel](#️-filter-panel)
  - [📋 Log Table](#-log-table)
  - [📈 Timeline Tab](#-timeline-tab)
  - [🚨 Detected Issues Tab](#-detected-issues-tab)
- [📖 Feature Reference](#-feature-reference)
  - [🎨 Log Display and Colorization](#-log-display-and-colorization)
  - [☑️ Log Level Filter](#️-log-level-filter)
  - [🏭 Facility Filter](#-facility-filter)
  - [🔍 Search](#-search)
  - [📡 Live Follow Mode](#-live-follow-mode)
  - [🔀 Log Source Selection](#-log-source-selection)
  - [🔄 Refresh](#-refresh)
  - [💾 Export](#-export)
  - [🗑️ Clear Kernel Buffer](#️-clear-kernel-buffer)
  - [📻 Console Log Level](#-console-log-level)
  - [📈 Kernel Error Timeline](#-kernel-error-timeline)
  - [🚨 Automatic Critical Error Detection](#-automatic-critical-error-detection)
  - [🔗 journalctl Correlation](#-journalctl-correlation)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [🔒 Security Notes](#-security-notes)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🔭 Overview

**DMESGVIEWOR** replaces complex `dmesg` command-line usage with an intuitive
graphical interface. It provides real-time log streaming, advanced filtering,
automatic critical error detection and graphical timeline analysis — all in a
single desktop application built with **Python** and **PyQt6**.

```
┌─────────────────────────────────────────────────────────────┐
│  🔧 Toolbar  [Source] [Refresh] [Follow] [Export] [Search]  │
├──────────────┬──────────────────────────────────────────────┤
│  🎛️ Filters  │  📋 Logs  │  📈 Timeline  │  🚨 Issues       │
│              │                                              │
│  ☑ emerg     │  Timestamp  Level  Facility  Source  Message │
│  ☑ alert     │  ─────────────────────────────────────────  │
│  ☑ crit      │  🔴 12345.67  emerg   kern   dmesg   …      │
│  ☑ err       │  🟠 12346.12  warn    kern   dmesg   …      │
│  ☑ warn      │  ⚫ 12347.00  info    kern   dmesg   …      │
│  ☑ notice    │                                              │
│  ☑ info      │                                              │
│  ☑ debug     │                                              │
├──────────────┴──────────────────────────────────────────────┤
│  📊 Logs: 4821/4821  |  📡 Follow: OFF  |  🔑 Permissions: OK│
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|:---:|---|
| 🎨 | **Colour-coded log table** — rows coloured by severity (emerg → debug) |
| ☑️ | **Level filter** — checkboxes to show/hide any combination of log levels |
| 🏭 | **Facility filter** — multi-select list to filter by kernel facility |
| 🔍 | **Text search** — regex-capable, case-sensitive, stacked on top of level/facility filters |
| 📡 | **Live follow mode** — real-time streaming via `dmesg -w` or `journalctl -kf` |
| 📈 | **Kernel Timeline** — per-minute histogram of errors, warnings and info logs |
| 🚨 | **Detected Issues** — automatic pattern-based detection of 18 critical kernel events |
| 🔀 | **journalctl source** — switch between dmesg ring buffer and systemd kernel journal |
| 💾 | **Export** — save visible logs to TXT, JSON, CSV or HTML |
| 🗑️ | **Clear buffer** — wipe the kernel ring buffer (`dmesg -C`) with confirmation |
| 📻 | **Console log level** — set the kernel console log level (`dmesg -n`) via dropdown |
| 🔑 | **Sudo authentication** — built-in password dialog when elevated privileges are required |

---

## ⚙️ Requirements

| 📦 Dependency | 🔢 Version | 📝 Purpose |
|---|---|---|
| 🐍 Python | 3.10+ | Runtime |
| 🖼️ PyQt6 | 6.4+ | GUI framework |
| 📊 pyqtgraph | 0.13+ | Timeline chart |
| 🐧 util-linux | any | Provides `dmesg` |
| ⚙️ systemd | any *(optional)* | Provides `journalctl` |

---

## 🚀 Installation

### 1️⃣ — Install system packages

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv util-linux
```

### 2️⃣ — Clone the repository

```bash
git clone https://github.com/nouhailler/DmesgViewor.git
cd DmesgViewor
```

### 3️⃣ — Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4️⃣ — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

```bash
python3 main.py
```

> 💡 If `dmesg` access is restricted on your system, the application will
> automatically display a **sudo password dialog** on startup.
> See [🔑 Permissions](#-permissions) below.

---

## 🔑 Permissions

On **Debian 12+**, access to the kernel ring buffer is restricted by default
(`kernel.dmesg_restrict = 1`). DMESGVIEWOR detects this and offers several
solutions.

### ✅ Option A — Add your user to the `adm` group *(recommended)*

Members of the `adm` group can read kernel logs without elevated privileges at runtime.

```bash
sudo usermod -aG adm $USER
```

> ⚠️ **Log out and log back in** for the group change to take effect.

---

### 🔐 Option B — Enter your sudo password in the application *(built-in)*

When DMESGVIEWOR detects a permission error, it automatically shows a password
dialog. Enter your sudo password to authenticate for the current session.

> 🛡️ The password is stored **in memory only** and discarded when the
> application closes. It is never written to disk.

---

### 🚀 Option C — Run with pkexec

```bash
pkexec python3 main.py
```

---

### ⚠️ Option D — Disable the restriction system-wide *(not recommended)*

```bash
sudo sysctl kernel.dmesg_restrict=0
```

> This affects all users and is not persistent across reboots.
> To make it persistent, add `kernel.dmesg_restrict=0` to `/etc/sysctl.conf`.

---

## 🖥️ User Interface

The interface is organised into four areas:

```
┌─────────────────────────────────────────────────────────────┐
│  🔧 Toolbar                                                 │
├──────────────┬──────────────────────────────────────────────┤
│              │  📋 Logs  |  📈 Timeline  |  🚨 Issues       │
│  🎛️ Filter   │                                              │
│  Panel       │  Log Table / Timeline / Issues Panel         │
│  (left)      │                                              │
├──────────────┴──────────────────────────────────────────────┤
│  📊 Status bar: log count | follow status | permissions     │
└─────────────────────────────────────────────────────────────┘
```

---

### 🔧 Toolbar

Located at the top of the window. Contains all action buttons and controls.

| Control | 📝 Description |
|---|---|
| 🔀 **Source** dropdown | Switch between `dmesg buffer` and `journalctl kernel` |
| ⟳ **Refresh** | Reload all logs from the selected source |
| ▶️ **Follow** | Start live log streaming |
| ⏸️ **Pause** | Stop live streaming |
| ⬇️ **Export** | Export visible (filtered) logs to file |
| 🗑️ **Clear Buffer** | Clear the kernel ring buffer |
| 📻 **Console level** dropdown | Set the kernel console log level (0 emerg → 7 debug) |
| 🔍 **Search** field | Text filter applied to the Message column |
| **Regex** checkbox | Interpret the search field as a regular expression |
| **Case** checkbox | Make the search case-sensitive |

---

### 🎛️ Filter Panel

Located on the **left side** of the window. Two independent filters:

**☑️ Log Levels** — Eight checkboxes, one per severity level. Uncheck a level
to hide all entries of that severity. All levels are enabled by default.

**🏭 Facilities** — A multi-select list. Hold `Ctrl` or `Shift` to select
multiple facilities. If nothing is selected, all facilities are shown.

> 💡 The Filter Panel and the Search bar are **combined**: an entry must match
> **both** the level/facility selection **and** the search text to appear.

---

### 📋 Log Table

A scrollable, sortable table of kernel log entries.
Click any column header to sort by that column.

| Column | 📝 Content |
|---|---|
| 🕐 **Timestamp** | Seconds since boot (dmesg) or date-time (journalctl) |
| 🏷️ **Level** | Severity: emerg, alert, crit, err, warn, notice, info, debug |
| 🏭 **Facility** | Origin: kern, user, daemon, auth, syslog, etc. |
| 🔀 **Source** | `dmesg` or `journalctl` |
| 💬 **Message** | The raw kernel log message |

---

### 📈 Timeline Tab

A graphical histogram showing log frequency per minute with three colour-coded
series. Supports zoom, pan and time-window selection to filter the log table.

---

### 🚨 Detected Issues Tab

Lists kernel events matching critical patterns (kernel panic, OOM, segfault…).
Double-click any issue to jump to the corresponding log entry.

---

## 📖 Feature Reference

### 🎨 Log Display and Colorization

Every row in the log table is coloured according to its severity level:

| Level | 🔢 Value | 🎨 Background | ✏️ Text | Description |
|---|:---:|---|---|---|
| 🔴 **emerg** | 0 | Red | White | System is unusable |
| 🔴 **alert** | 1 | Red | White | Action must be taken immediately |
| 🟥 **crit** | 2 | Dark red | White | Critical conditions |
| 🔴 **err** | 3 | White | Red | Error conditions |
| 🟠 **warn** | 4 | White | Orange | Warning conditions |
| 🔵 **notice** | 5 | White | Dark blue | Normal but significant |
| ⚫ **info** | 6 | White | Black | Informational |
| 🔘 **debug** | 7 | White | Gray | Debug-level messages |

---

### ☑️ Log Level Filter

**📍 Location:** Filter Panel → Log Levels section *(left side)*

Eight checkboxes corresponding to the eight kernel severity levels. Filtering
is applied instantly in memory — **without re-running `dmesg`**.

**💡 Example use cases:**
- Uncheck `debug` and `info` → focus on warnings and above
- Keep only `err` and `crit` → see only critical errors
- Keep all levels → full log view

---

### 🏭 Facility Filter

**📍 Location:** Filter Panel → Facilities section *(left side)*

| 🏭 Facility | 🔢 Number | 📝 Typical origin |
|---|:---:|---|
| kern | 0 | Core kernel messages |
| user | 1 | User-space processes |
| daemon | 3 | System daemons |
| auth | 4 | Authentication subsystem |
| syslog | 5 | Syslog internal messages |
| lpr | 6 | Line printer subsystem |
| news | 7 | Network news subsystem |
| cron | 9 | Cron scheduler |

---

### 🔍 Search

**📍 Location:** Toolbar → Search field

Filters the **Message** column. The search is applied **on top of** the level
and facility filters — an entry must pass all three to appear.

| Option | 📝 Behaviour |
|---|---|
| Plain text | Case-insensitive substring match |
| ✅ **Regex** checked | Interpreted as a Python regular expression |
| ✅ **Case** checked | Match becomes case-sensitive |

**🔎 Regex examples:**

```regex
usb.*disconnect          # Match "usb" followed by "disconnect"
(error|fail|denied)      # Match any of the three words
^\[.*PCIe               # Lines whose message starts with "[" and contains "PCIe"
```

> ⚠️ **Important:** Search and Console Level are **completely independent**.
> - 🔍 **Search** → filters what is **displayed** in the application
> - 📻 **Console Level** → sets a **kernel parameter** for `/dev/console` output

---

### 📡 Live Follow Mode

**📍 Location:** Toolbar → ▶️ Follow / ⏸️ Pause buttons

Streams new kernel log entries in real-time as they are produced.

| 🔀 Source | ⌨️ Command used |
|---|---|
| dmesg buffer | `dmesg -w --json` |
| journalctl kernel | `journalctl -kf -o json` |

New entries are appended at the bottom and the view scrolls automatically.
The **Timeline** and **Detected Issues** panels update incrementally.

> 💡 Switching the log source while Follow is active will **automatically stop**
> the follow session before switching.

---

### 🔀 Log Source Selection

**📍 Location:** Toolbar → Source dropdown

| Option | 📝 Description |
|---|---|
| 🐧 `dmesg buffer` | Reads the kernel ring buffer via `dmesg --json` |
| ⚙️ `journalctl kernel` | Reads systemd's persistent journal via `journalctl -k -o json` |

**Key differences:**

| | 🐧 dmesg | ⚙️ journalctl |
|---|---|---|
| Storage | RAM ring buffer | Disk (persistent) |
| Survives reboot | ❌ No | ✅ Yes |
| Timestamps | Seconds since boot | Absolute date/time |
| Previous boots | ❌ No | ✅ Yes |

---

### 🔄 Refresh

**📍 Location:** Toolbar → ⟳ Refresh button

Runs a fresh one-shot read of the selected source, replaces the table content
and updates the Timeline and Detected Issues panels.

---

### 💾 Export

**📍 Location:** Toolbar → ⬇️ Export button

Exports the **currently visible (filtered) entries** only.

| 📄 Format | 🔖 Extension | 📝 Description |
|---|---|---|
| 📝 Text | `.txt` | One entry per line, human-readable |
| 🔧 JSON | `.json` | Array of objects with all fields |
| 📊 CSV | `.csv` | Spreadsheet-compatible, UTF-8 |
| 🌐 HTML | `.html` | Colour-coded table, opens in a browser |

---

### 🗑️ Clear Kernel Buffer

**📍 Location:** Toolbar → 🗑️ Clear Buffer button

Runs `dmesg -C` to wipe the kernel ring buffer. A confirmation dialog is shown
before execution.

> ⚠️ **Warning:** This action is **irreversible**. All entries in the ring
> buffer will be permanently deleted.

Requires elevated privileges (`CAP_SYSLOG`). The sudo password dialog will
appear if needed.

---

### 📻 Console Log Level

**📍 Location:** Toolbar → Console level dropdown

Sets the **kernel console log level** via `dmesg -n <level>`.

> 💡 This is a **kernel parameter**, not an application display filter.
> It controls which messages the kernel prints to `/dev/console` (the system
> terminal). It has **no effect** on what DMESGVIEWOR displays.

| 🎚️ Dropdown | ⌨️ Sent | 📝 Effect |
|---|---|---|
| 0 emerg | `-n 1` | Only emergencies reach the console |
| 1 alert | `-n 2` | + alerts |
| 2 crit | `-n 3` | + critical |
| 3 err | `-n 4` | + errors |
| 4 warn | `-n 5` | + warnings |
| 5 notice | `-n 6` | + notices |
| 6 info | `-n 7` | + informational |
| 7 debug | `-n 8` | All messages *(default)* |

---

### 📈 Kernel Error Timeline

**📍 Location:** Timeline tab

A histogram showing log frequency per one-minute bucket, with three series:

| 🎨 Colour | 📊 Series |
|---|---|
| 🔴 Red | Errors and above (emerg, alert, crit, err — levels 0–3) |
| 🟠 Orange | Warnings (level 4) |
| 🔵 Blue | Info, notice, debug (levels 5–7) |

**🖱️ Interactions:**

| Action | Result |
|---|---|
| 🖱️ Scroll wheel | Zoom in/out on the time axis |
| 🖱️ Click + drag | Pan the view |
| ↔️ Drag region handles | Select a time window |
| ▶️ **Apply time window** | Filter the log table to the selected range |
| ✖️ **Clear selection** | Remove the time filter and restore all entries |

> 📦 **Requirement:** The Timeline tab requires the `pyqtgraph` package.
> If not installed: `pip install pyqtgraph`

---

### 🚨 Automatic Critical Error Detection

**📍 Location:** Detected Issues tab

DMESGVIEWOR automatically scans all loaded entries for known critical patterns:

| 🚨 Category | 🔍 Pattern | ⚠️ Severity |
|---|---|:---:|
| 💥 Kernel Panic | `kernel panic` | 🔴 critical |
| 🐛 Kernel BUG | `BUG:` | 🔴 critical |
| 💀 Kernel Oops | `Oops:` | 🔴 critical |
| 🧠 OOM | `Out of memory` | 🔴 critical |
| 🔧 Hardware Error | `hardware error` | 🔴 critical |
| ⏱️ Watchdog Timeout | `watchdog.*timeout` | 🔴 critical |
| 🖥️ MCE / Machine Check | `MCE.*error`, `Machine Check` | 🔴 critical |
| ⚡ NMI | `NMI` | 🔴 critical |
| 🔒 Soft Lockup | `soft lockup` | 🔴 critical |
| 💣 Segfault | `segfault` | 🟠 error |
| 📜 Call Trace | `Call Trace:` | 🟠 error |
| 💾 I/O Error | `I/O error` | 🟠 error |
| 📁 EXT4 FS Error | `EXT4-fs error` | 🟠 error |
| 🔌 PCIe Error | `PCIe.*error` | 🟠 error |
| ⚡ ACPI Error | `ACPI.*error` | 🟠 error |
| 🧩 EDAC Error | `EDAC.*error` | 🟠 error |
| 🧵 Hung Task | `hung_task` | 🟠 error |
| 🔌 USB Disconnect | `USB disconnect` | 🟡 warning |

**🖱️ Interactions:**

| Action | Result |
|---|---|
| 🖱️ Double-click an issue | Switches to Logs tab and scrolls to the entry |
| 💾 **Export issues (JSON)** | Saves the issue list to a `.json` file |

---

### 🔗 journalctl Correlation

**📍 Location:** Toolbar → Source dropdown → `journalctl kernel`

When selected, the application reads from the **systemd journal** instead of
the dmesg ring buffer. Both sources populate the same table with a **Source**
column (`dmesg` / `journalctl`), making it easy to correlate events.

**Advantages of journalctl source:**
- ✅ Persistent across reboots
- ✅ Absolute timestamps (date + time)
- ✅ Access to logs from previous boots
- ✅ Same filters, search, follow mode and export as dmesg

---

## 🏗️ Architecture

DMESGVIEWOR follows the **Model-View-Controller (MVC)** pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│  🔧 Backend (data acquisition)                                  │
│  dmesg_runner.py  ─┐                                           │
│  journal_runner.py ┤──► json_parser.py ──► LogEntry objects    │
└────────────────────┼────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│  📦 Model                                                       │
│  LogEntry (dataclass)                                           │
│  LogTableModel (QAbstractTableModel)  ── max 50 000 entries     │
│  LogFilterProxyModel (QSortFilterProxyModel)                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│  🎮 Controller                                                  │
│  MainController — connects signals, manages background threads  │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│  🖥️ View (UI)                                                   │
│  MainWindow ── AppToolBar                                       │
│            ├── FilterPanel                                      │
│            ├── LogTableView                                     │
│            ├── TimelineWidget  (pyqtgraph)                      │
│            └── IssuesPanel                                      │
└─────────────────────────────────────────────────────────────────┘
```

> 💡 Follow workers use **`subprocess.Popen`** with line-by-line reading rather
> than `QProcess`, which must not be used outside the main Qt thread.

---

## 📁 Project Structure

```
DmesgViewor/
│
├── 🐍 main.py                   # Entry point — python3 main.py
├── 🐍 app.py                    # QApplication setup
│
├── 📂 backend/
│   ├── 🐍 dmesg_runner.py       # run_dmesg_once(), DmesgFollowWorker
│   ├── 🐍 journal_runner.py     # run_journal_once(), JournalFollowWorker
│   └── 🐍 json_parser.py        # Parse dmesg/journalctl JSON → LogEntry
│
├── 📂 models/
│   ├── 🐍 log_entry.py          # LogEntry dataclass, level/facility maps
│   └── 🐍 log_table_model.py    # QAbstractTableModel + QSortFilterProxyModel
│
├── 📂 controllers/
│   └── 🐍 main_controller.py    # Wires all signals, manages threads
│
├── 📂 ui/
│   ├── 🐍 main_window.py        # MainWindow: layout, tabs, status bar
│   ├── 🐍 toolbar.py            # AppToolBar: action buttons + search
│   ├── 🐍 filter_panel.py       # Level checkboxes + facility list
│   ├── 🐍 log_table.py          # LogTableView (QTableView wrapper)
│   ├── 🐍 timeline_widget.py    # PyQtGraph histogram + region selector
│   └── 🐍 issues_panel.py       # Pattern detection + issue list
│
├── 📂 utils/
│   ├── 🐍 privileges.py         # Sudo password dialog
│   ├── 🐍 exporter.py           # TXT / JSON / CSV / HTML writers
│   └── 🐍 time_utils.py         # Boot timestamp → epoch conversion
│
├── 📂 resources/
│   └── 📂 icons/                # (reserved for future icons)
│
├── 📄 requirements.txt
├── 📄 .gitignore
└── 📄 README.md
```

---

## 🔒 Security Notes

| 🛡️ | Detail |
|---|---|
| 📖 | DMESGVIEWOR **reads** the kernel ring buffer but never writes to it unless you explicitly use Clear Buffer or Console Level |
| 🔑 | The sudo password is stored **in memory only** for the session duration — never written to disk |
| 🌐 | **No network connection** is made at any time — all operations are local |
| 🔐 | `dmesg -C` and `dmesg -n` require `CAP_SYSLOG` or root access |
| ✅ | The recommended setup (`adm` group) grants **read-only** access without elevated privileges at runtime |

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. 🍴 Fork the repository and create a feature branch
2. 📏 Follow [PEP 8](https://peps.python.org/pep-0008/) coding style
3. 🏗️ Keep the MVC structure: backend logic in `backend/`, UI in `ui/`, business logic in `controllers/`
4. 🧪 Test on Debian 12+ with Python 3.10+
5. 📬 Open a pull request with a clear description of the change

### 🐛 Reporting Issues

Please include:

- 🐧 Debian version: `cat /etc/debian_version`
- 🐍 Python version: `python3 --version`
- 🖼️ PyQt6 version: `pip show PyQt6 | grep Version`
- 🔧 util-linux version: `dmesg --version`
- 📋 The full error message or traceback

---

## 📄 License

```
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
```

---

<div align="center">

**Made with ❤️ for the 🐧 Linux community**

⭐ If you find this project useful, please consider giving it a star!

</div>
]]>