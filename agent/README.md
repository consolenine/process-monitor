# Process Monitor Agent

A lightweight, standalone monitoring agent that tracks running processes, system resource usage, and reports data to a remote Django backend. It is designed to work cross-platform and is easily installable or executable.

---

## Features

- Monitors CPU & memory usage of processes
- Tracks parent-child process relationships
- Captures machine details (RAM, disk, network)
- Sends data to a REST API backend
- Supports remote config from the server
- Runs as a CLI or one-file executable
- Lightweight and install-free using PyInstaller

---

## Requirements

- Python 3.13+
- `pip`, `virtualenv` (recommended)

---

## Build Instructions

```bash
pyinstaller --onefile run.py --name ProcessMonitorAgent