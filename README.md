# SysIntel - Real-Time System Monitor for Windows



**SysIntel** is a modern, extensible system monitor for Windows built with Python. Inspired by Windows Task Manager, it provides real-time graphs, hardware stats, and efficient logging—all within a clean, dark-themed GUI. Perfect for system enthusiasts, developers, or anyone who wants deeper control and insight into their PC.

---

## 🚀 Features

- **Modern Tkinter GUI** with dark theme and responsive layout
- **Real-time system stats**: CPU, RAM, Disk, Network, GPU, Fans, System Info
- **Scrolling Graphs** with optional smoothing styles (Sharp, Average, Round)
- **Compact CSV Logging** optimized for long-term use and future AI analysis
- **Settings tab** for update rate, smoothing style, and temperature units
- **Automatic restart** when settings are applied
- **GPU auto-selection** (always uses your dedicated GPU if present)
- **Modular design** using `gui/`, `monitor/`, and `utils/` packages

---

## 📂 Project Structure

```
sysintel/
├── __main__.py              # Entry point (run with `python -m sysintel`)
├── gui/
│   ├── __init__.py
│   └── main_window.py       # GUI layout and event handling
├── monitor/
│   ├── __init__.py
│   └── system_stats.py      # CPU, RAM, GPU, etc. monitoring
├── utils/
│   ├── __init__.py
│   └── formatters.py        # Byte/speed/temp format helpers
└── config.json              # User settings (auto-generated)
```

---

## 📦 Installation

### Requirements

- Python 3.10+
- Windows 10/11

### Dependencies

```bash
pip install psutil GPUtil pywin32
```

### Run the App

```bash
python -m run.py
```

### Optional: Build Executable

Use [PyInstaller](https://pyinstaller.org/) to turn it into a `.exe`:

```bash
pyinstaller --noconfirm --clean --onefile --windowed -n SysIntel sysintel/__main__.py
```

---

## 🧠 AI + Logs

- Logs are written in `sysintel_log.csv` using compact columns:
  - `ts` (timestamp, base36)
  - `cpu`, `mem`, `gpu`, `ct`, `gt`, `fan`
- Ready for trend detection, anomaly alerts, or assistant-style optimization.

---

## 🔮 Roadmap Ideas

- AI Assistant (analyze logs, recommend cleanups)
- Graph export / snapshot saving
- Web or mobile dashboards
- Remote monitoring support
- Plugin system for more sensor support

---

## 🛠 Contributing

Contributions welcome! If you’ve got ideas, improvements, or widgets to add, open a PR or drop an issue.

---

## 📜 License

MIT License. Use it, remix it, and make it better.

---

Made with 💻, caffeine ☕, and a suspiciously active GPU fan.

---

> *"Built not just to monitor, but to understand your machine."*