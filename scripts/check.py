"""ZEVQ KeepAlive scheduled public endpoint checker."""
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]


def validate_url(url):
    if not isinstance(url, str) or len(url) > 2048:
        return False
    try:
        parsed = urllib.parse.urlsplit(url)
        host = parsed.hostname or ""
        return (
            parsed.scheme == "https"
            and host.endswith(".onrender.com")
            and host != ".onrender.com"
            and parsed.port in (None, 443)
            and not parsed.username
            and not parsed.password
            and not parsed.fragment
            and all(ord(ch) >= 32 for ch in url)
        )
    except ValueError:
        return False


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def check(monitor, opener=None, now=None):
    url = monitor.get("url", "")
    timestamp = now or datetime.now(timezone.utc).isoformat()
    result = {
        "name": str(monitor.get("name", "Unnamed"))[:80],
        "url": url,
        "status": "invalid",
        "httpStatus": None,
        "latencyMs": None,
        "checkedAt": timestamp,
    }
    if not validate_url(url):
        return result
    opener = opener or urllib.request.build_opener(NoRedirect())
    started = time.monotonic()
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "ZEVQ-KeepAlive/1.0"})
        with opener.open(request, timeout=25) as response:
            code = response.status
        result["status"] = "online" if 200 <= code < 400 else "offline"
        result["httpStatus"] = code
    except urllib.error.HTTPError as error:
        result["status"] = "offline"
        result["httpStatus"] = error.code
    except (urllib.error.URLError, TimeoutError, OSError):
        result["status"] = "offline"
    result["latencyMs"] = round((time.monotonic() - started) * 1000)
    return result


def main():
    config = json.loads((ROOT / "monitors.json").read_text(encoding="utf-8"))
    if not isinstance(config, list):
        raise ValueError("monitors.json must contain an array")
    status_file = ROOT / "status.json"
    try:
        previous = json.loads(status_file.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        previous = {}
    timestamp = datetime.now(timezone.utc).isoformat()
    results = [check(m, now=timestamp) for m in config[:30] if isinstance(m, dict)]
    for result in results:
        print(result["name"], result["status"], result["latencyMs"])
    history = previous.get("history", [])
    if not isinstance(history, list):
        history = []
    history.append({"timestamp": timestamp, "services": results})
    output = {"updatedAt": timestamp, "services": results, "history": history[-1008:]}
    status_file.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
