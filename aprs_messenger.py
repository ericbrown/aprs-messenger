#!/usr/bin/env python3
"""Simple APRS-IS messenger. Send and receive APRS messages via the internet."""

import json
import math
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

RETRY_INTERVAL = 30  # seconds between retries
RETRY_MAX = 3


def load_config() -> dict:
    """Load callsign and passcode from config.json."""
    if not CONFIG_FILE.exists():
        print(f"Config file not found: {CONFIG_FILE}")
        print('Create it with: {"callsign": "YOURCALL", "passcode": 12345}')
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


def haversine(lat1, lon1, lat2, lon2):
    """Distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_lat(s: str) -> float | None:
    """Parse APRS latitude: DDMM.MMN/S."""
    try:
        deg = int(s[:2])
        minutes = float(s[2:7])
        val = deg + minutes / 60
        if s[7] == "S":
            val = -val
        return val
    except (ValueError, IndexError):
        return None


def parse_lon(s: str) -> float | None:
    """Parse APRS longitude: DDDMM.MME/W."""
    try:
        deg = int(s[:3])
        minutes = float(s[3:8])
        val = deg + minutes / 60
        if s[8] == "W":
            val = -val
        return val
    except (ValueError, IndexError):
        return None


def parse_position(line: str) -> dict | None:
    """Parse an APRS position packet. Returns {from, lat, lon, comment} or None."""
    try:
        sender = line.split(">")[0]
        # Find the data type indicator after the path
        colon_idx = line.index(":", line.index(">"))
        body = line[colon_idx + 1:]

        # Position formats: !lat/lonS, =lat/lonS, /time lat/lonS, @time lat/lonS
        if not body:
            return None

        dtype = body[0]
        if dtype in "!=":
            # Uncompressed: !DDMM.MMN/DDDMM.MME
            lat = parse_lat(body[1:9])
            lon = parse_lon(body[10:19])
            comment = body[20:].strip() if len(body) > 20 else ""
        elif dtype in "/@":
            # With timestamp: /HHMMSSh or @HHMMSSh then position
            lat = parse_lat(body[8:16])
            lon = parse_lon(body[17:26])
            comment = body[27:].strip() if len(body) > 27 else ""
        else:
            return None

        if lat is None or lon is None:
            return None
        return {"from": sender, "lat": lat, "lon": lon, "comment": comment}
    except (ValueError, IndexError):
        return None


def parse_message(line: str, callsign: str) -> dict | None:
    """Parse an incoming APRS message directed at us."""
    if "::" not in line:
        return None
    try:
        sender = line.split(">")[0]
        msg_start = line.index("::") + 2
        dest = line[msg_start:msg_start + 9].strip()
        body = line[msg_start + 10:]

        if dest.upper() != callsign.upper():
            return None

        if body.startswith("ack"):
            return {"type": "ack", "from": sender, "id": body[3:].strip()}
        if body.startswith("rej"):
            return {"type": "rej", "from": sender, "id": body[3:].strip()}

        msg_id = None
        text = body
        if "{" in body:
            text, msg_id = body.rsplit("{", 1)
            msg_id = msg_id.strip()

        return {"type": "msg", "from": sender, "text": text, "id": msg_id}
    except (ValueError, IndexError):
        return None


class APRSMessenger:
    """Core APRS-IS messaging engine."""

    def __init__(self, config: dict):
        self.callsign = config["callsign"].upper()
        self.passcode = config["passcode"]
        self.filter = config.get("filter", "")
        self.sock = None
        self.connected = False
        self.msg_counter = 1
        self.lock = threading.Lock()

        # Pending messages awaiting ack: {msg_id_str: {dest, text, sent_at, retries}}
        self.pending = {}
        self.pending_lock = threading.Lock()

        # Last heard stations: {callsign: {lat, lon, last_seen, comment}}
        self.heard = {}
        self.heard_lock = threading.Lock()

        # Message history for web UI: [{direction, callsign, text, timestamp}]
        self.messages = []
        self.messages_lock = threading.Lock()

        # Callbacks for UI updates
        self.on_message = None  # called with (direction, sender, text)
        self.on_ack = None  # called with (msg_id, sender)
        self.on_retry_failed = None  # called with (msg_id, dest, text)

    def connect(self) -> str:
        """Connect and authenticate to APRS-IS. Returns status string."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)
        self.sock.connect((SERVER, PORT))

        self.sock.settimeout(5)
        try:
            banner = self.sock.recv(512).decode("ascii", errors="replace").strip()
        except socket.timeout:
            banner = ""

        # Build filter: always include our messages, plus user filter
        aprs_filter = f"g/{self.callsign}*"
        if self.filter:
            aprs_filter += f" {self.filter}"

        login = f"user {self.callsign} pass {self.passcode} vers aprs-messenger 1.0 filter {aprs_filter}"
        self.sock.sendall((login + "\r\n").encode())

        try:
            resp = self.sock.recv(512).decode("ascii", errors="replace").strip()
            verified = "logresp" in resp and "verified" in resp.lower()
        except socket.timeout:
            resp = ""
            verified = False

        self.sock.settimeout(None)
        self.connected = True

        # Start background threads
        threading.Thread(target=self._receiver, daemon=True).start()
        threading.Thread(target=self._retry_loop, daemon=True).start()

        status = "verified" if verified else resp
        return status

    def send(self, dest: str, text: str) -> int:
        """Send a message. Returns the message ID."""
        with self.lock:
            msg_id = self.msg_counter
            self.msg_counter += 1

        dest = dest.upper()
        packet = format_message(self.callsign, dest, text, msg_id)
        self.sock.sendall((packet + "\r\n").encode())
        log_message("TX", dest, text)

        id_str = f"{msg_id:03d}"
        with self.pending_lock:
            self.pending[id_str] = {
                "dest": dest,
                "text": text,
                "sent_at": time.time(),
                "retries": 0,
            }

        with self.messages_lock:
            self.messages.append({
                "direction": "TX",
                "callsign": dest,
                "text": text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "msg_id": id_str,
            })

        return msg_id

    def get_heard(self) -> list[dict]:
        """Return list of heard stations sorted by last seen (most recent first)."""
        with self.heard_lock:
            stations = []
            for call, info in self.heard.items():
                stations.append({"callsign": call, **info})
            stations.sort(key=lambda s: s["last_seen"], reverse=True)
            return stations

    def get_messages(self, since: int = 0) -> list[dict]:
        """Return messages newer than index `since`."""
        with self.messages_lock:
            return self.messages[since:]

    def _receiver(self):
        """Background: read from APRS-IS, dispatch messages and positions."""
        buf = ""
        while self.connected:
            try:
                data = self.sock.recv(4096)
                if not data:
                    self.connected = False
                    break
                buf += data.decode("ascii", errors="replace")
                while "\r\n" in buf:
                    line, buf = buf.split("\r\n", 1)
                    if line.startswith("#"):
                        continue
                    self._handle_line(line)
            except OSError:
                self.connected = False
                break

    def _handle_line(self, line: str):
        """Process a single APRS-IS line."""
        # Try as message first
        parsed = parse_message(line, self.callsign)
        if parsed:
            if parsed["type"] == "ack":
                self._handle_ack(parsed)
            elif parsed["type"] == "rej":
                self._handle_ack(parsed, rejected=True)
            elif parsed["type"] == "msg":
                self._handle_incoming(parsed)
            return

        # Try as position
        pos = parse_position(line)
        if pos:
            with self.heard_lock:
                self.heard[pos["from"]] = {
                    "lat": pos["lat"],
                    "lon": pos["lon"],
                    "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "comment": pos["comment"],
                }

    def _handle_ack(self, parsed: dict, rejected: bool = False):
        """Handle an ack or rej for a pending message."""
        msg_id = parsed["id"]
        with self.pending_lock:
            self.pending.pop(msg_id, None)
        if self.on_ack:
            self.on_ack(msg_id, parsed["from"], rejected)

    def _handle_incoming(self, parsed: dict):
        """Handle an incoming message."""
        log_message("RX", parsed["from"], parsed["text"])

        with self.messages_lock:
            self.messages.append({
                "direction": "RX",
                "callsign": parsed["from"],
                "text": parsed["text"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "msg_id": parsed.get("id"),
            })

        # Send ack
        if parsed["id"]:
            ack = format_ack(self.callsign, parsed["from"], parsed["id"])
            try:
                self.sock.sendall((ack + "\r\n").encode())
            except OSError:
                pass

        if self.on_message:
            self.on_message("RX", parsed["from"], parsed["text"], parsed.get("id"))

    def _retry_loop(self):
        """Background: resend unacknowledged messages."""
        while self.connected:
            time.sleep(10)
            now = time.time()
            to_retry = []
            to_fail = []

            with self.pending_lock:
                for msg_id, info in list(self.pending.items()):
                    if now - info["sent_at"] >= RETRY_INTERVAL:
                        if info["retries"] < RETRY_MAX:
                            info["retries"] += 1
                            info["sent_at"] = now
                            to_retry.append((msg_id, info))
                        else:
                            to_fail.append((msg_id, info))
                            del self.pending[msg_id]

            for msg_id, info in to_retry:
                packet = format_message(self.callsign, info["dest"], info["text"], int(msg_id))
                try:
                    self.sock.sendall((packet + "\r\n").encode())
                except OSError:
                    break
                if self.on_message:
                    self.on_message("RETRY", info["dest"], f"retry #{info['retries']} for msg#{msg_id}", None)

            for msg_id, info in to_fail:
                if self.on_retry_failed:
                    self.on_retry_failed(msg_id, info["dest"], info["text"])

    def disconnect(self):
        """Close the connection."""
        self.connected = False
        if self.sock:
            self.sock.close()


def cli_main():
    """Run the interactive CLI."""
    config = load_config()
    messenger = APRSMessenger(config)

    def on_message(direction, sender, text, msg_id):
        if direction == "RX":
            print(f"\n  [{sender}] {text}")
            if msg_id:
                print(f"  > ack sent for {msg_id}")
        elif direction == "RETRY":
            print(f"  [{sender}] {text}")

    def on_ack(msg_id, sender, rejected):
        if rejected:
            print(f"  [REJECTED {msg_id} by {sender}]")
        else:
            print(f"  [ack {msg_id} from {sender}]")

    def on_retry_failed(msg_id, dest, text):
        print(f"  [FAILED msg#{msg_id} to {dest} after {RETRY_MAX} retries: \"{text}\"]")

    messenger.on_message = on_message
    messenger.on_ack = on_ack
    messenger.on_retry_failed = on_retry_failed

    print(f"Connecting to APRS-IS as {messenger.callsign}...")
    try:
        status = messenger.connect()
        print(f"  Logged in ({status})")
    except OSError as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    aprs_filter = f"g/{messenger.callsign}*"
    if messenger.filter:
        aprs_filter += f" {messenger.filter}"
    print(f"  Filter: {aprs_filter}")
    print(f"  Log file: {LOG_FILE}")
    print(f"\nType a callsign to send a message, or /help for commands. Ctrl+C to quit.\n")

    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break

            if not line:
                continue

            if line.lower() == "/heard":
                stations = messenger.get_heard()
                if not stations:
                    print("  No stations heard yet.\n")
                    continue
                print(f"  {'Callsign':<12} {'Last seen':<20} {'Comment'}")
                print(f"  {'-'*11:<12} {'-'*19:<20} {'-'*30}")
                for s in stations[:20]:
                    print(f"  {s['callsign']:<12} {s['last_seen']:<20} {s['comment'][:40]}")
                print()
                continue

            if line.lower() == "/pending":
                with messenger.pending_lock:
                    if not messenger.pending:
                        print("  No pending messages.\n")
                        continue
                    for mid, info in messenger.pending.items():
                        print(f"  msg#{mid} to {info['dest']}: \"{info['text']}\" (retries: {info['retries']})")
                print()
                continue

            if line.lower() == "/help":
                print("  /heard   — show nearby stations")
                print("  /pending — show unacknowledged messages")
                print("  /help    — this help")
                print("  Or type a callsign to send a message\n")
                continue

            if line.startswith("/"):
                print(f"  Unknown command: {line}. Type /help\n")
                continue

            dest = line.upper()
            try:
                text = input("msg: ").strip()
            except EOFError:
                break
            if not text:
                continue

            msg_id = messenger.send(dest, text)
            print(f"  Sent to {dest}: \"{text}\" (msg#{msg_id:03d})")
            print()
    except KeyboardInterrupt:
        print("\n\nDisconnecting...")
    finally:
        messenger.disconnect()
        print("Done.")


if __name__ == "__main__":
    cli_main()
