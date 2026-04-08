#!/usr/bin/env python3
"""Simple APRS-IS messenger. Send and receive APRS messages via the internet."""

import json
import socket
import threading
import time
import sys
from datetime import datetime
from pathlib import Path

APP_DIR = Path(__file__).parent
CONFIG_FILE = APP_DIR / "config.json"
LOG_FILE = APP_DIR / "messages.log"
SERVER = "rotate.aprs2.net"
PORT = 14580


def load_config() -> dict:
    """Load callsign and passcode from config.json."""
    if not CONFIG_FILE.exists():
        print(f"Config file not found: {CONFIG_FILE}")
        print('Create it with: {{"callsign": "YOURCALL", "passcode": 12345}}')
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    if "callsign" not in config or "passcode" not in config:
        print('Config must have "callsign" and "passcode" fields.')
        sys.exit(1)
    return config


def aprs_passcode(callsign: str) -> int:
    """Compute APRS-IS verification passcode from callsign (no SSID)."""
    callsign = callsign.split("-")[0].upper()
    code = 0x73E2
    for i in range(0, len(callsign), 2):
        code ^= ord(callsign[i]) << 8
        if i + 1 < len(callsign):
            code ^= ord(callsign[i + 1])
    return code & 0x7FFF


def log_message(direction: str, callsign: str, text: str):
    """Append a message to the log file."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} {direction} {callsign} {text}\n")


def format_message(callsign: str, dest: str, text: str, msg_id: int) -> str:
    """Format an APRS message packet."""
    dest_padded = f"{dest.upper():<9}"
    return f"{callsign}>APRS,TCPIP*::{dest_padded}:{text}{{{msg_id:03d}"


def format_ack(callsign: str, dest: str, msg_id: str) -> str:
    """Format an APRS ack packet."""
    dest_padded = f"{dest.upper():<9}"
    return f"{callsign}>APRS,TCPIP*::{dest_padded}:ack{msg_id}"


def parse_message(line: str, callsign: str) -> dict | None:
    """Parse an incoming APRS message directed at us."""
    # Format: SENDER>PATH::DEST_____:message text{ID
    if "::" not in line:
        return None
    try:
        sender = line.split(">")[0]
        # Find the :: message delimiter
        msg_start = line.index("::") + 2
        dest = line[msg_start:msg_start + 9].strip()
        body = line[msg_start + 10:]  # skip the ":"

        if dest.upper() != callsign.upper():
            return None

        # Check if it's an ack
        if body.startswith("ack"):
            return {"type": "ack", "from": sender, "id": body[3:].strip()}

        # Check if it's a reject
        if body.startswith("rej"):
            return {"type": "rej", "from": sender, "id": body[3:].strip()}

        # Regular message — extract optional message ID
        msg_id = None
        text = body
        if "{" in body:
            text, msg_id = body.rsplit("{", 1)
            msg_id = msg_id.strip()

        return {"type": "msg", "from": sender, "text": text, "id": msg_id}
    except (ValueError, IndexError):
        return None


def receiver(sock: socket.socket, callsign: str):
    """Background thread: read lines from APRS-IS and print incoming messages."""
    buf = ""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("\n[Disconnected from APRS-IS]")
                break
            buf += data.decode("ascii", errors="replace")
            while "\r\n" in buf:
                line, buf = buf.split("\r\n", 1)
                if line.startswith("#"):
                    continue  # server comment

                parsed = parse_message(line, callsign)
                if not parsed:
                    continue

                if parsed["type"] == "ack":
                    print(f"  [ack {parsed['id']} from {parsed['from']}]")
                elif parsed["type"] == "rej":
                    print(f"  [REJECTED {parsed['id']} by {parsed['from']}]")
                elif parsed["type"] == "msg":
                    print(f"\n  [{parsed['from']}] {parsed['text']}")
                    log_message("RX", parsed["from"], parsed["text"])
                    # Send ack if message had an ID
                    if parsed["id"]:
                        ack = format_ack(callsign, parsed["from"], parsed["id"])
                        sock.sendall((ack + "\r\n").encode())
                        print(f"  > ack sent for {parsed['id']}")
        except OSError:
            break


def main():
    config = load_config()
    callsign = config["callsign"].upper()
    passcode = config["passcode"]

    print(f"Connecting to APRS-IS as {callsign}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    try:
        sock.connect((SERVER, PORT))
    except OSError as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    # Read server banner
    sock.settimeout(5)
    try:
        banner = sock.recv(512).decode("ascii", errors="replace").strip()
        print(f"  {banner}")
    except socket.timeout:
        pass

    # Login
    login = f"user {callsign} pass {passcode} vers aprs-messenger 1.0 filter g/{callsign}*"
    sock.sendall((login + "\r\n").encode())

    # Read login response
    try:
        resp = sock.recv(512).decode("ascii", errors="replace").strip()
        if "logresp" in resp and "verified" in resp.lower():
            print(f"  Logged in (verified)")
        else:
            print(f"  {resp}")
    except socket.timeout:
        pass

    sock.settimeout(None)
    print(f"  Log file: {LOG_FILE}")
    print(f"\nReady. Type a callsign and message to send. Ctrl+C to quit.\n")

    # Start receiver thread
    rx_thread = threading.Thread(target=receiver, args=(sock, callsign), daemon=True)
    rx_thread.start()

    msg_counter = 1

    try:
        while True:
            try:
                dest = input("to: ").strip().upper()
                if not dest:
                    continue
                text = input("msg: ").strip()
                if not text:
                    continue
            except EOFError:
                break

            packet = format_message(callsign, dest, text, msg_counter)
            sock.sendall((packet + "\r\n").encode())
            print(f"  Sent to {dest}: \"{text}\" (msg#{msg_counter:03d})")
            log_message("TX", dest, text)
            msg_counter += 1
            print()
    except KeyboardInterrupt:
        print("\n\nDisconnecting...")
    finally:
        sock.close()
        print("Done.")


if __name__ == "__main__":
    main()
