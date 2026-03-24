# ð MT5 Trading Bot - Deployment Guide

## ð **Table of Contents**
- [Prerequisites](#prerequisites)
- [Building the Executable](#building-the-executable)
- [Running the Bot](#running-the-bot)
- [Deployment Options](#deployment-options)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## [ok] **Prerequisites**

### **Required Software:**
1. **Python 3.8+** installed
2. **MetaTrader 5 Terminal** installed and configured
3. **Git** (if cloning from repository)

### **Python Dependencies:**
All dependencies are listed in `requirements.txt`

---

## ð¨ **Building the Executable**

### **Option 1: Automatic Build (Recommended)**

1. **Open Command Prompt or PowerShell**
2. **Navigate to project directory:**
   ```bash
   cd "C:\IvÃ¡n\Yosoybuendesarrollador\Python\Portafolio\mt5_live_trading_bot"
   ```

3. **Run the build script:**
   ```bash
   build_exe.bat
   ```

4. **Wait for completion** (1-2 minutes)
   - The script will install PyInstaller if needed
   - Build the executable
   - Clean up temporary files

5. **Find your executable:**
   - Location: `dist\MT5_Trading_Bot.exe`
   - Size: ~50-150MB (includes all dependencies)

### **Option 2: Manual Build**

If you prefer to build manually:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --name "MT5_Trading_Bot" --noconsole advanced_mt5_monitor_gui.py
```

---

## â¶ï¸ **Running the Bot**

### **Method 1: Direct Execution**

1. **Navigate to the dist folder:**
   ```bash
   cd dist
   ```

2. **Double-click** `MT5_Trading_Bot.exe`
   - Or run from command line: `MT5_Trading_Bot.exe`

3. **GUI will appear** - Enter your MT5 credentials

### **Method 2: Using Launcher Script (Recommended)**

The launcher provides automatic restart on crashes:

```bash
run_bot.bat
```

**Features:**
- [ok] Automatic error detection
- [ok] Option to restart on failure
- [ok] Separate launcher logs
- [ok] Timestamped log files

### **Method 3: Background Process**

Run without a visible window:

```bash
start /B dist\MT5_Trading_Bot.exe
```

---

## ð¯ **Deployment Options**

### **Option A: Local Development/Testing**

**Use Case:** Testing, debugging, development

**Setup:**
- Keep in project directory
- Use `run_bot.bat` for easy restarts
- Monitor via `mt5_advanced_monitor.log`

**Pros:**
- [ok] Easy access to source code
- [ok] Quick rebuilds after changes
- [ok] Familiar environment

**Cons:**
- [warn]ï¸ Mixed with source files

---

### **Option B: Dedicated Production Folder**

**Use Case:** Long-term production deployment

**Setup Steps:**

1. **Create production folder:**
   ```bash
   mkdir C:\Trading\MT5_Bot
   ```

2. **Copy executable:**
   ```bash
   copy dist\MT5_Trading_Bot.exe C:\Trading\MT5_Bot\
   ```

3. **Create shortcut on Desktop** (optional):
   - Right-click `MT5_Trading_Bot.exe`
   - Send to -> Desktop (create shortcut)

4. **Run from production folder**

**Pros:**
- [ok] Clean separation from source code
- [ok] Professional organization
- [ok] Easy to find and launch
- [ok] Centralized logs

**Cons:**
- [warn]ï¸ Must copy new .exe after rebuilds

---

### **Option C: Auto-Start with Windows**

**Use Case:** 24/7 automated trading

**Setup via Task Scheduler:**

1. **Open Task Scheduler** (Win + R -> `taskschd.msc`)

2. **Create Basic Task:**
   - Name: `MT5 Trading Bot`
   - Description: `Automated MT5 Trading Bot - KIPS STRATEGY Strategy`

3. **Trigger:** At log on (or daily at specific time)

4. **Action:** Start a program
   - Program: `C:\Trading\MT5_Bot\MT5_Trading_Bot.exe`
   - Start in: `C:\Trading\MT5_Bot`

5. **Settings:**
   - [ok] Allow task to be run on demand
   - [ok] Run task as soon as possible after a scheduled start is missed
   - [ok] If the task fails, restart every: 1 minute
   - [ok] Attempt to restart up to: 3 times

**Pros:**
- [ok] Fully automated
- [ok] Survives reboots
- [ok] Auto-recovery on crashes

**Cons:**
- [warn]ï¸ Runs on every login (may need credentials automation)

---

### **Option D: Multiple Instances**

**Use Case:** Running different configurations simultaneously

**Setup:**

1. **Create separate folders:**
   ```bash
   mkdir C:\Trading\Bot_Conservative
   mkdir C:\Trading\Bot_Aggressive
   ```

2. **Copy executable to each folder**

3. **Modify strategy parameters** (if using config files)

4. **Run each instance separately**

**Pros:**
- [ok] Test different strategies
- [ok] Different asset allocations
- [ok] Independent logging

**Cons:**
- [warn]ï¸ Higher resource usage
- [warn]ï¸ Must manage multiple logs

---

## ð **Monitoring & Logs**

### **Primary Log File:**
- **File:** `mt5_advanced_monitor.log`
- **Location:** Same directory as .exe
- **Content:** Detailed bot activity, trades, errors

### **Viewing Logs:**

**Option 1: Real-time monitoring (PowerShell)**
```powershell
Get-Content mt5_advanced_monitor.log -Wait -Tail 50
```

**Option 2: Text Editor**
- Use Notepad++, Sublime Text, or VS Code
- Enable auto-reload to see updates

**Option 3: Log Analysis Tools**
- BareTail (free log viewer)
- LogExpert
- mTail

### **Log Rotation:**

To prevent logs from growing too large:

**Manual cleanup (weekly):**
```bash
# Keep last 7 days only
forfiles /P "." /M *.log /D -7 /C "cmd /c del @path"
```

**Automated script** (create `cleanup_logs.bat`):
```batch
@echo off
forfiles /P "." /M *.log /D -7 /C "cmd /c del @path"
echo Old logs deleted. Keeping last 7 days only.
```

---

## ð§ **Troubleshooting**

### **Issue: Executable doesn't start**

**Solution:**
1. Check if MetaTrader 5 is installed
2. Run from command prompt to see errors:
   ```bash
   dist\MT5_Trading_Bot.exe
   ```
3. Check Windows Event Viewer for crash details

---

### **Issue: "DLL Load Failed" error**

**Solution:**
1. Install Visual C++ Redistributable:
   - Download from Microsoft: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Restart computer
3. Try running .exe again

---

### **Issue: Antivirus blocks the .exe**

**Solution:**
1. Add exclusion in Windows Defender:
   - Settings -> Update & Security -> Windows Security -> Virus & threat protection
   - Manage settings -> Add exclusion -> File
   - Select `MT5_Trading_Bot.exe`

2. Whitelist in third-party antivirus (similar process)

---

### **Issue: Bot crashes on startup**

**Solution:**
1. Check `mt5_advanced_monitor.log` for errors
2. Verify MT5 terminal is running
3. Test MT5 connection manually
4. Rebuild .exe: `build_exe.bat`

---

### **Issue: Cannot see GUI window**

**Solution:**
1. Check if running with `--noconsole` flag
2. Rebuild without noconsole:
   ```bash
   pyinstaller --onefile --name "MT5_Trading_Bot" advanced_mt5_monitor_gui.py
   ```
3. Window may be minimized - check taskbar

---

### **Issue: Logs not being created**

**Solution:**
1. Check file permissions in directory
2. Run .exe as administrator (right-click -> Run as administrator)
3. Check if log path is hardcoded to different location

---

## ð **Security Best Practices**

### **[ok] DO:**
- [ok] Keep the .exe in a secure location
- [ok] Use strong MT5 account passwords
- [ok] Regular backups of logs and configurations
- [ok] Monitor account activity regularly
- [ok] Run on trusted networks only
- [ok] Keep Windows updated

### **â DON'T:**
- â Share your .exe publicly (may contain your paths)
- â Commit .exe to public GitHub repositories
- â Store credentials in plain text files
- â Run on public/untrusted computers
- â Disable antivirus completely (whitelist only)
- â Share your MT5 credentials

### **Credential Management:**

**Best Practice - Separate Config File:**

Create `mt5_config.py` (add to .gitignore):
```python
MT5_LOGIN = 12345678
MT5_PASSWORD = "YourSecurePassword"
MT5_SERVER = "YourBroker-Demo"
```

**Environment Variables (Advanced):**
```python
import os
login = os.getenv('MT5_LOGIN')
password = os.getenv('MT5_PASSWORD')
```

---

## ð **Version Control**

### **Files in Git Repository:**
[ok] Source code (`.py` files)
[ok] Build scripts (`.bat` files)
[ok] Documentation (`.md` files)
[ok] Dependencies (`requirements.txt`)
[ok] `.gitignore` file

### **Files NOT in Git (Local Only):**
â `.exe` files
â `.log` files
â `dist/` folder
â `build/` folder
â Credential files
â Personal configurations

---

## ð¯ **Recommended Deployment Workflow**

### **Development Phase:**
1. Edit code in VS Code
2. Test with `python advanced_mt5_monitor_gui.py`
3. Verify in logs
4. Commit changes to Git

### **Build Phase:**
1. Run `build_exe.bat`
2. Test .exe locally
3. Verify logs are working

### **Deployment Phase:**
1. Copy .exe to production folder
2. Set up Task Scheduler (optional)
3. Monitor first 24 hours closely
4. Review logs daily

### **Maintenance Phase:**
1. Monitor logs weekly
2. Clean old logs monthly
3. Rebuild .exe after any code changes
4. Keep backups of working versions

---

## ð **Support & Updates**

- **GitHub Repository:** Check for updates regularly
- **Logs:** Always check `mt5_advanced_monitor.log` first
- **Rebuilding:** After any Python code changes, rebuild the .exe

---

## [ok] **Quick Start Checklist**

- [ ] Python 3.8+ installed
- [ ] MetaTrader 5 installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Built executable (`build_exe.bat`)
- [ ] Tested .exe runs correctly
- [ ] Logs being created successfully
- [ ] MT5 connection working
- [ ] Credentials secured (not in code)
- [ ] `.gitignore` configured
- [ ] Production folder created (optional)
- [ ] Task Scheduler configured (optional for auto-start)

---

**ð You're ready to deploy! Good luck with your automated trading!**
