"""Utility functions."""

import socket
import uuid
from pathlib import Path

import psutil


def get_mac_address():
    """Get the mac address of the player.

    Returns:
        mac (str): The mac address.
    """
    mac = hex(uuid.getnode()).replace("0x", "").upper()
    mac = ":".join(mac[i : i + 2] for i in range(0, len(mac), 2))
    return mac


def get_serial_number():
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
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip_addresses[interface] = addr.address
    return ip_addresses


def select_ip_by_priority(ip_addresses: dict[str, str]) -> str:
    """Select the best ip address by priority.

    Args:
        ip_addresses (dict[str, str]): The ip addresses.

    Returns:
        ip_address (str): The best ip address.
    """
    keys_priority = ["ethernet", "eth0", "wi-fi", "wifi", "wlan0"]
    best_match = next(iter(ip_addresses.values()), "127.0.0.1")
    best_ix = len(keys_priority)
    for key, val in ip_addresses.items():
        if key.lower() in keys_priority:
            ix = keys_priority.index(key.lower())
            if ix < best_ix:
                best_match = val
                best_ix = ix
    return best_match


def scan_for_exts(
    dirpath: Path | str, exts: list[str], recursive: bool = False
) -> list[Path]:
    """Scan a directory for files with specific extensions.

    Args:
        dirpath (Path | str): The directory to scan.
        exts (list[str]): The extensions to look for.
        recursive (bool): Whether to scan recursively.

    Returns:
        files (list[Path]): The files found.
    """
    dirpath = Path(dirpath)
    files = []
    for ext in exts:
        files.extend(dirpath.glob(f"*.{ext}" if not recursive else f"**/*.{ext}"))
    return files
