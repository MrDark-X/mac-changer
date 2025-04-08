import ctypes
import os
import re
import subprocess
import random
import requests
import logging
import json
import getpass
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_valid_mac(mac):
    # Regular expression to validate MAC address format
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return re.match(pattern, mac) is not None

def get_random_mac():
    # Generate a random MAC address
    mac_digits = "0123456789ABCDEF"
    mac = ""
    for _ in range(6):
        mac += random.choice(mac_digits) + random.choice(mac_digits) + ":"
    return mac[:-1]

def get_vendor_info(mac):
    # Retrieve MAC address vendor information using an API (e.g., Macvendors.co)
    url = f"https://api.macvendors.com/{mac}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
    except requests.exceptions.RequestException as e:
        pass
    return "Vendor information not found"

def get_interface_info(interface):
    try:
        output = subprocess.check_output(["ipconfig", "/all"]).decode("utf-8")
        pattern = rf"({interface}).+?Physical Address.+?((?:[0-9A-Fa-f]{{2}}[:-]){5}[0-9A-Fa-f]{{2}}).+?IPv4 Address.+?((?:\d+\.){3}\d+)"
        match = re.search(pattern, output, re.DOTALL)
        if match:
            interface_name = match.group(1).strip()
            mac_address = match.group(2).strip()
            ip_address = match.group(3).strip()
            mac_vendor = get_vendor_info(mac_address)
            return interface_name, mac_address, ip_address, mac_vendor
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get interface info for {interface}. Error: {e}")
    return None

def change_mac(interface, new_mac):
    try:
        logger.info(f"Changing MAC address of {interface} to {new_mac}")
        subprocess.run(["reg", "add", f"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{interface}\\Ndi\\Params\\NetworkAddress", "/v", "NetworkAddress", "/t", "REG_SZ", "/d", new_mac, "/f"], check=True)
        subprocess.run(["netsh", "interface", "set", "interface", f"name={interface}", "admin=disable"], check=True)
        subprocess.run(["netsh", "interface", "set", "interface", f"name={interface}", "admin=enable"], check=True)
        logger.info(f"MAC address of {interface} changed to {new_mac}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to change MAC address of {interface}. Error: {e}")
        return False

def restore_mac(interface):
    try:
        logger.info(f"Restoring original MAC address of {interface}")
        subprocess.run(["reg", "delete", f"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{interface}\\Ndi\\Params\\NetworkAddress", "/f"], check=True)
        subprocess.run(["netsh", "interface", "set", "interface", f"name={interface}", "admin=disable"], check=True)
        subprocess.run(["netsh", "interface", "set", "interface", f"name={interface}", "admin=enable"], check=True)
        logger.info(f"Original MAC address of {interface} restored")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to restore original MAC address of {interface}. Error: {e}")
        return False

def select_interface():
    interfaces = subprocess.check_output(["netsh", "interface", "show", "interface"]).decode("utf-8").split("\n")
    interface_list = [interface.strip() for interface in interfaces if "Connected" in interface]

    if len(interface_list) == 0:
        print("No network interfaces found.")
        return None

    print("Available network interfaces:")
    print("{:<20} {:<20} {:<20} {:<20}".format("Interface Name", "MAC Address", "IP Address", "MAC Vendor"))
    for interface in interface_list:
        interface_info = get_interface_info(interface)
        if interface_info:
            interface_name, mac_address, ip_address, mac_vendor = interface_info
            print("{:<20} {:<20} {:<20} {:<20}".format(interface_name, mac_address, ip_address, mac_vendor))

    while True:
        selected_index = input("Enter the index of the interface to change the MAC address: ")
        if selected_index.isdigit():
            selected_index = int(selected_index) - 1
            if 0 <= selected_index < len(interface_list):
                return interface_list[selected_index]
        print("Invalid interface index. Please try again.")

def load_mac_history(secret_location):
    mac_history = {}
    try:
        with open(secret_location, "r") as file:
            mac_history = json.load(file)
    except Exception as e:
        logger.error("Failed to load MAC address history. Error: " + str(e))
    return mac_history

def save_mac_history(mac_history, secret_location):
    try:
        with open(secret_location, "w") as file:
            json.dump(mac_history, file, indent=4)
    except Exception as e:
        logger.error("Failed to save MAC address history. Error: " + str(e))

def view_mac_history(mac_history):
    if mac_history:
        print("MAC address history:")
        for interface, mac_changes in mac_history.items():
            print(f"Interface: {interface}")
            for mac_change in mac_changes:
                timestamp = mac_change["timestamp"]
                original_mac = mac_change["original_mac"]
                new_mac = mac_change["new_mac"]
                print(f"Timestamp: {timestamp}")
                print(f"Original MAC: {original_mac}")
                print(f"New MAC: {new_mac}")
            print()
    else:
        print("No MAC address history available.")

def main():
    if not is_admin():
        print("Please run the tool with administrative privileges.")
        input("Press Enter to exit...")
        return

    selected_interface = select_interface()
    if not selected_interface:
        return

    print(f"Selected interface: {selected_interface}")

    secret_location = os.path.join(os.path.expanduser("~"), ".mac_history.json")
    mac_history = load_mac_history(secret_location)
    view_mac_history(mac_history)

    print("MACaddress change options:")
    print("1. Enter a specific MAC address")
    print("2. Generate a random MAC address")

    option = input("Enter your choice: ")

    if option == "1":
        new_mac = input("Enter the new MAC address (e.g., 00:11:22:33:44:55): ")

        while not is_valid_mac(new_mac):
            print("Invalid MAC address format. Please try again.")
            new_mac = input("Enter the new MAC address (e.g., 00:11:22:33:44:55): ")

    elif option == "2":
        new_mac = get_random_mac()
        print(f"Generated random MAC address: {new_mac}")

    else:
        print("Invalid option selected. Exiting.")
        return

    username = getpass.getuser()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if change_mac(selected_interface, new_mac):
        vendor_info = get_vendor_info(new_mac)
        print(f"\nVendor information: {vendor_info}")

        # Update MAC address history
        if selected_interface not in mac_history:
            mac_history[selected_interface] = []

        # Add the current change to the history
        mac_change = {
            "timestamp": current_time,
            "original_mac": mac_history[selected_interface][-1]["new_mac"] if mac_history[selected_interface] else "",
            "new_mac": new_mac
        }
        mac_history[selected_interface].append(mac_change)
        save_mac_history(mac_history, secret_location)

    restore_option = input("Do you want to restore the original MAC address? (y/n): ")
    if restore_option.lower() == "y":
        restore_mac(selected_interface)
        print("Original MAC address restored successfully.")
    else:
        print("Exiting without restoring the original MAC address.")

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
