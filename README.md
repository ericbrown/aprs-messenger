# APRS Messenger

Simple APRS-IS messaging app. Pure Python, no dependencies. Connect to the APRS network via the internet, send and receive messages.

## Setup

1. Copy `config.json.example` to `config.json` and fill in your callsign and APRS-IS passcode:

```json
{
    "callsign": "YOURCALL-5",
    "passcode": 12345,
    "filter": "r/39.75/-104.99/50"
}
```

- **callsign**: Your callsign with optional SSID (-5 is conventional for software clients)
- **passcode**: Your APRS-IS verification passcode
- **filter** (optional): [APRS-IS filter string](http://www.aprs-is.net/javAPRSFilter.aspx). Example: `r/39.75/-104.99/50` for a 50km radius around a lat/lon. Omit for message-only mode.

## Usage

### CLI mode

```
python3 aprs_messenger.py
```

Interactive prompt — type a callsign and message to send. Incoming messages print in real-time.

Commands:
- `/heard` — show nearby stations (requires a filter with position data)
- `Ctrl+C` — quit

### Web mode

```
python3 web.py
```

Opens a web UI at `http://localhost:8073` with:
- Chat-style message view
- Send form (callsign + message)
- Heard stations sidebar (click a station to set as destination)
- Pending message indicator

## Features

- Send and receive APRS messages via APRS-IS
- Automatic ack handling (sends acks for incoming messages, tracks acks for outgoing)
- Message retry — resends unacknowledged messages up to 3 times (30s intervals)
- Last heard station list from position packets
- Message history logging to `messages.log`
- Configurable APRS-IS server filter

## Files

- `aprs_messenger.py` — core library + CLI
- `web.py` — web interface server
- `static/index.html` — web UI
- `config.json` — your callsign, passcode, and filter (gitignored)
- `config.json.example` — template config
- `messages.log` — message history (gitignored)

## License

MIT
