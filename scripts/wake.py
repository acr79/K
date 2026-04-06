#!/usr/bin/env python3
"""Wake the KLLM rig via magic packet, then wait for the API to come up."""

import socket
import struct
import time
import sys
import os
from pathlib import Path

# Load .env manually (no dotenv dependency needed)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

RIG_MAC  = os.environ.get("RIG_MAC_ADDRESS", "")
RIG_IP   = os.environ.get("RIG_IP", "")
RIG_PORT = int(os.environ.get("RIG_API_PORT", "8080"))
WAIT     = int(os.environ.get("RIG_BOOT_WAIT", "90"))


def send_magic_packet(mac: str):
    """Send a WoL magic packet to the given MAC address."""
    mac = mac.replace(":", "").replace("-", "").upper()
    if len(mac) != 12:
        raise ValueError(f"Invalid MAC address: {mac}")

    mac_bytes = bytes.fromhex(mac)
    magic = b"\xff" * 6 + mac_bytes * 16

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic, ("<broadcast>", 9))

    print(f"Magic packet sent to {mac}")


def wait_for_api(ip: str, port: int, timeout: int = 120) -> bool:
    """Poll until the KLLM API responds or timeout."""
    print(f"Waiting for KLLM API at {ip}:{port}...", end="", flush=True)
    start = time.time()

    while time.time() - start < timeout:
        try:
            with socket.create_connection((ip, port), timeout=2):
                print(" online.")
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            print(".", end="", flush=True)
            time.sleep(3)

    print(" timed out.")
    return False


def wake_and_wait() -> bool:
    if not RIG_MAC:
        print("RIG_MAC_ADDRESS not set in .env — skipping WoL.")
        print("Set it when the rig is built.")
        return False

    if not RIG_IP:
        print("RIG_IP not set in .env — cannot check if rig is online.")
        return False

    # Check if already awake
    try:
        with socket.create_connection((RIG_IP, RIG_PORT), timeout=2):
            print(f"Rig already online at {RIG_IP}:{RIG_PORT}")
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass

    # Send magic packet
    print(f"Rig is offline — sending magic packet to {RIG_MAC}")
    send_magic_packet(RIG_MAC)

    # Wait for it to boot and KLLM to start
    print(f"Waiting up to {WAIT}s for boot...")
    return wait_for_api(RIG_IP, RIG_PORT, timeout=WAIT)


if __name__ == "__main__":
    success = wake_and_wait()
    sys.exit(0 if success else 1)
