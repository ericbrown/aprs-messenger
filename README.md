# APRS Messenger

A simple APRS messaging application that connects to the APRS-IS (Automatic Packet Reporting System - Internet Service) network. Send and receive APRS messages from your computer without a radio — all you need is a ham radio license and an internet connection.

Pure Python. No dependencies. Works on Linux, macOS, and Windows.

## What is APRS-IS?

APRS-IS is the internet backbone of the APRS network. It connects to RF (radio) APRS via iGates — stations that bridge packets between RF and the internet. When you send a message through APRS-IS, any iGate near the recipient will transmit it over RF. Replies come back the same way.

This means you can message anyone on the APRS network — whether they're on a handheld radio, a mobile rig, or another internet client.

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/ericbrown/aprs-messenger.git
cd aprs-messenger
cp config.json.example config.json
```

Edit `config.json` with your callsign and APRS-IS passcode:

```json
{
    "callsign": "YOURCALL-5",
    "passcode": 12345,
    "filter": "r/39.75/-104.99/50"
}
```

### 2. Run it

**CLI mode:**
```bash
python3 aprs_messenger.py
```

**Web mode:**
```bash
python3 web.py
```
Then open `http://localhost:8073` in your browser.

## Configuration

The `config.json` file has three fields:

| Field | Required | Description |
|-------|----------|-------------|
| `callsign` | Yes | Your callsign with SSID. Use `-5` for a software client (e.g., `N0EDB-5`). Don't reuse an SSID that's already active on another station. |
| `passcode` | Yes | Your APRS-IS verification passcode. This is a numeric code derived from your callsign. If you don't know yours, search for "APRS-IS passcode generator" or use the `aprs_passcode()` function in the code. |
| `filter` | No | An [APRS-IS filter string](http://www.aprs-is.net/javAPRSFilter.aspx) that controls what packets you receive beyond your own messages. See [Filters](#filters) below. |

### APRS-IS Passcode

If you need to compute your passcode, you can use the built-in function:

```bash
python3 -c "from aprs_messenger import aprs_passcode; print(aprs_passcode('YOURCALL'))"
```

Replace `YOURCALL` with your callsign (no SSID). The passcode is the same for all SSIDs of a given callsign.

### SSIDs

APRS uses SSIDs (Secondary Station Identifiers) to distinguish multiple stations under one callsign. Common conventions:

| SSID | Meaning |
|------|---------|
| None | Primary station (home base) |
| -5 | Smartphone or software client |
| -7 | Handheld radio |
| -9 | Mobile (vehicle) |
| -10 | Internet / iGate |
| -15 | Weather station |

Pick an SSID that isn't already in use by another one of your stations.

### Filters

The `filter` field controls what additional APRS packets you receive from the network. Without a filter, you only receive messages addressed directly to your callsign. With a filter, you also receive position packets from nearby stations, which populates the "heard stations" list.

Common filter examples:

| Filter | Description |
|--------|-------------|
| `r/39.75/-104.99/50` | 50 km radius around lat 39.75, lon -104.99 |
| `r/39.75/-104.99/100` | 100 km radius |
| `p/W0/N0/K0` | All stations with callsigns starting W0, N0, or K0 |
| `b/W0ABC/N0XYZ` | Only specific callsigns |
| `t/p` | Position packets only (all stations passing the server) |

You can combine multiple filters with spaces: `r/39.75/-104.99/50 p/W0`

Full filter documentation: [aprs-is.net/javAPRSFilter.aspx](http://www.aprs-is.net/javAPRSFilter.aspx)

## CLI Mode

```
$ python3 aprs_messenger.py
Connecting to APRS-IS as N0EDB-5...
  Logged in (verified)
  Filter: g/N0EDB-5* r/39.75/-104.99/50
  Log file: /home/user/aprs-messenger/messages.log

Type a callsign to send a message, or /help for commands. Ctrl+C to quit.

> N0ABC
msg: Hello from my APRS messenger!
  Sent to N0ABC: "Hello from my APRS messenger!" (msg#001)

  [ack 001 from N0ABC]

  [N0ABC] Hey, nice app!
  > ack sent for 042
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `/heard` | Show nearby stations (callsign, last seen time, comment). Requires a position filter to be set. |
| `/pending` | Show messages that haven't been acknowledged yet, with retry count. |
| `/help` | Show available commands. |
| *(callsign)* | Type any callsign to start composing a message to that station. |
| `Ctrl+C` | Disconnect and quit. |

## Web Mode

```
$ python3 web.py
Connecting to APRS-IS as N0EDB-5...
  Logged in (verified)
  Filter: g/N0EDB-5* r/39.75/-104.99/50
  Log file: /home/user/aprs-messenger/messages.log

Web UI: http://localhost:8073
Ctrl+C to quit
```

The web interface provides:

- **Message view** — chat-style display of sent and received messages, with timestamps and direction indicators
- **Send form** — callsign and message input. The destination callsign persists between messages for easy back-and-forth conversations
- **Heard stations sidebar** — list of nearby stations heard via position packets, sorted by most recently seen. Click any station to set it as the message destination
- **Pending indicator** — shows when messages are awaiting acknowledgment

The web server listens on port 8073 by default.

## Message Retry

When you send a message, APRS Messenger tracks whether it was acknowledged by the recipient. If no ack is received within 30 seconds, the message is automatically resent. After 3 failed retries (about 90 seconds total), the message is marked as failed.

This matches the behavior of standard APRS messaging clients and helps ensure delivery over the sometimes-unreliable RF network.

In the CLI, you'll see retry and failure notifications:
```
  [N0ABC] retry #1 for msg#001
  [N0ABC] retry #2 for msg#001
  [FAILED msg#001 to N0ABC after 3 retries: "Hello!"]
```

## Message Logging

All sent and received messages are appended to `messages.log` in the project directory:

```
2026-04-08 11:02:42 TX N0ABC Hello from my APRS messenger!
2026-04-08 11:03:15 RX N0ABC Hey, nice app!
```

The log persists across sessions and is never overwritten. It's excluded from git via `.gitignore`.

## How It Works

1. **Connection** — Opens a TCP socket to an APRS-IS server (`rotate.aprs2.net:14580`), which load-balances across the APRS-IS network.

2. **Authentication** — Sends a login line with your callsign, passcode, software version, and server-side filter string.

3. **Receiving** — A background thread reads lines from the socket. Each line is either a message (parsed and displayed) or a position packet (parsed and added to the heard list). Incoming messages with a message ID automatically get an ack sent back.

4. **Sending** — Messages are formatted as APRS packets (`YOURCALL>APRS,TCPIP*::DEST_CALL :message text{NNN`) and written to the socket. The message ID (`NNN`) is tracked for retry purposes.

5. **Retry** — A second background thread checks every 10 seconds for messages that haven't been acked. If 30 seconds have elapsed, it resends. After 3 retries, it gives up.

## Project Structure

```
aprs-messenger/
  aprs_messenger.py    # Core library + CLI entry point
  web.py               # Web interface server
  static/
    index.html         # Web UI (single-page app)
  config.json          # Your config (gitignored)
  config.json.example  # Template config
  messages.log         # Message history (gitignored, created at runtime)
```

## Requirements

- Python 3.10+ (uses `X | Y` union type syntax)
- A valid amateur radio callsign
- An APRS-IS passcode for your callsign

No third-party packages are needed. Everything uses the Python standard library.

## License

MIT
