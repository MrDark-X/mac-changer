# Windows MAC Address Changer 🖧

A Python-based tool to view, change, and restore the MAC addresses of network interfaces on Windows systems. This script supports both manual MAC address entry and random MAC generation, with built-in logging and change history tracking.

## ✨ Features

- ✅ View connected network interfaces with IP, MAC, and vendor details
- 🔀 Change MAC address (manual or random)
- ♻️ Restore original MAC address
- 📜 MAC address format validation
- 🗂️ JSON-based MAC change history tracking
- 🌐 Vendor lookup via [macvendors.co](https://macvendors.co/)
- 🔐 Admin privilege check and registry manipulation
- 📋 Clean CLI interface with detailed logging


## ⚙️ Requirements

- **Windows OS** (Tested on Windows 10)
- Python 3.6+
- Internet connection (for vendor lookup)

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/MrDark-X/windows-mac-changer.git
   cd windows-mac-changer
   ```
---
2. Execute
⚠️ You must run the script with admin privileges, or it will not work.
```Python
python3 mac.py
```
### 🧪 Usage
When you launch the script:
- It will list all connected interfaces.
You can:
- Choose a custom MAC address.
- Generate a random one.
- The tool will:
- Change your MAC via registry modification.
- Restart the interface.
- Save the change history.
- Optionally, it allows you to restore the original MAC.

### 🛑 Disclaimer
This tool is intended for educational and research purposes only. Changing your MAC address can violate the terms of use of some networks or services. Use responsibly and at your own risk.

### 🧑‍💻 Author
Yaswanth Surya Chalamalasetty
