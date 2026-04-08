#!/usr/bin/env python3
"""Web interface for APRS messenger. Run this instead of the CLI."""

import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs

from aprs_messenger import APRSMessenger, load_config, LOG_FILE

APP_DIR = Path(__file__).parent
WEB_PORT = 8073


class APRSHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the APRS messenger web UI."""

    messenger: APRSMessenger = None  # set by main()

    def do_GET(self):
        if self.path == "/":
            self.path = "/static/index.html"
            return super().do_GET()
        if self.path.startswith("/static/"):
            return super().do_GET()
        if self.path.startswith("/api/messages"):
            self._api_messages()
        elif self.path == "/api/heard":
            self._api_heard()
        elif self.path == "/api/status":
            self._api_status()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/send":
            self._api_send()
        else:
            self.send_error(404)

    def _api_messages(self):
        """Return messages, optionally since an index."""
        since = 0
        if "?" in self.path:
            params = parse_qs(self.path.split("?", 1)[1])
            since = int(params.get("since", [0])[0])
        messages = self.messenger.get_messages(since)
        total = since + len(messages)
        self._json_response({"messages": messages, "total": total})

    def _api_heard(self):
        """Return heard stations."""
        stations = self.messenger.get_heard()
        self._json_response({"stations": stations[:50]})

    def _api_status(self):
        """Return connection status."""
        pending_count = len(self.messenger.pending)
        self._json_response({
            "callsign": self.messenger.callsign,
            "connected": self.messenger.connected,
            "pending": pending_count,
        })

    def _api_send(self):
        """Send a message."""
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        dest = body.get("to", "").strip().upper()
        text = body.get("message", "").strip()
        if not dest or not text:
            self._json_response({"error": "need 'to' and 'message'"}, 400)
            return
        msg_id = self.messenger.send(dest, text)
        self._json_response({"msg_id": msg_id})

    def _json_response(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        pass  # silence request logs

    def translate_path(self, path):
        """Serve files from APP_DIR."""
        return str(APP_DIR / path.lstrip("/"))


def main():
    config = load_config()
    messenger = APRSMessenger(config)

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

    APRSHandler.messenger = messenger

    server = HTTPServer(("0.0.0.0", WEB_PORT), APRSHandler)
    print(f"\nWeb UI: http://localhost:{WEB_PORT}")
    print("Ctrl+C to quit\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()
        messenger.disconnect()
        print("Done.")


if __name__ == "__main__":
    main()
