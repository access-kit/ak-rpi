"""Utility functions."""

import uuid

import netifaces


def get_mac_address():
    """Get the mac address of the player.

    Returns:
        mac (str): The mac address.
    """
    mac = hex(uuid.getnode()).replace("0x", "").upper()
    mac = ":".join(mac[i : i + 2] for i in range(0, len(mac), 2))
    return mac


def determine_serial_number():
    """Determine the serial number of the player.

    Returns:
        serial_number (str): The serial number.
    """
    # check if we are running on a raspberry pi
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("Serial"):
                    return line.split(":")[1].strip()
            return get_mac_address()
    except FileNotFoundError:
        # if we are not running on a raspberry pi, check the mac address
        return get_mac_address()


def get_ip_addresses():
    """Get the ip addresses of the player.

    Returns:
        ip_addresses (dict[str, str]): The ip addresses.
    """
    ip_addresses: dict[str, str] = {}
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            ip_addresses[interface] = addrs[netifaces.AF_INET][0]["addr"]
    return ip_addresses
