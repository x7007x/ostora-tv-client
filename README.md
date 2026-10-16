# ostora-tv-client

Python client for **Ostora TV** (الأسطورة TV, `com.t4w.ostora516`) — re-implements every network request the Android app makes, one method per request.

## How the app works

The app hides its server behind DNS TXT records and AES-256-CBC encrypted strings (key/IV hardcoded in its native library). This client reproduces the full chain:

1. **Bootstrap** — DNS-over-HTTPS TXT lookup of `start.ver6.top` (random server from 1.1.1.1 / 8.8.8.8)
2. **Config** — TXT data → base64 → AES-256-CBC decrypt → base64 → zlib → JSON (website URL, update APK link, popup link, API hosts)
3. **Notifications** — raw DNS TXT lookup of `n6.not6.top` via 8.8.8.8 → base64 → zlib → JSON

## Install

```bash
pip install requests cryptography dnspython
```

## Usage

```python
from main import OstoraTV

tv = OstoraTV()
tv.get_website()        # https://ostora.tv
tv.get_update_url()     # APK download link
tv.get_popup_url()      # popup/ad link
tv.get_notifications()  # notifications dict
tv.decrypt_string("lmWqTW6yPAoclJQWaBxA8w==")  # start.ver6.top
```

Run `python main.py` to see live examples.

## Methods

| Method | Request |
|---|---|
| `decrypt_string(b64)` | Decrypt an app-encrypted string (AES-256-CBC) |
| `doh_txt(host)` | DNS-over-HTTPS TXT lookup |
| `dns_txt(host)` | Raw DNS TXT query to 8.8.8.8 (DoH fallback if UDP blocked) |
| `get_config()` | Full app config as dict |
| `get_website()` | Site URL the app's WebView loads |
| `get_update_url()` | Self-update APK link |
| `get_popup_url()` | Popup/ad link |
| `get_notifications()` | Notifications payload as dict |

## Note

For research and interoperability purposes. Server endpoints and keys were extracted from the public APK via static analysis.
