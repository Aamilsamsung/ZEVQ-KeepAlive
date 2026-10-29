import json
import pathlib
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
config = json.loads((ROOT / "monitors.json").read_text())
status_file = ROOT / "status.json"
previous = json.loads(status_file.read_text()) if status_file.exists() else {"history": []}
timestamp = datetime.now(timezone.utc).isoformat()
results = []
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener = urllib.request.build_opener(NoRedirect())
for monitor in config[:30]:
    url = monitor["url"]
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.endswith(".onrender.com") or parsed.hostname == ".onrender.com" or parsed.port not in (None, 443) or parsed.username or parsed.password:
        results.append({"name": monitor["name"], "url": url, "status": "invalid", "latencyMs": None})
        continue
    start = time.monotonic()
    try:
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "ZEVQ-KeepAlive/1.0"}), timeout=25) as response:
            code = response.status
        state = "online" if 200 <= code < 400 else "offline"
    except Exception as exc:
        code = getattr(exc, "code", None)
        state = "offline"
    latency = round((time.monotonic() - start) * 1000)
    results.append({"name": monitor["name"], "url": url, "status": state, "httpStatus": code, "latencyMs": latency, "checkedAt": timestamp})
    print(monitor["name"], state, latency, "ms")
history = previous.get("history", [])
history.append({"timestamp": timestamp, "services": results})
history = history[-1008:]
status_file.write_text(json.dumps({"updatedAt": timestamp, "services": results, "history": history}, indent=2) + "\n")
