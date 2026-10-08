"""Shared helpers: polite HTTP with cache, JSON output, graceful failure.

Python 3.9+ standard library only. No API keys. Every network call returns a
dict or raises nothing: failures come back as {"_error": ..., "url": ...} so the
calling agent can record "not reachable" instead of crashing.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

VERSION = "0.1.0"
UA_BROWSER = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"
)
UA_TOOL = f"cr-prospect-intel/{VERSION} (https://github.com/contentrewards-prospect-intel; low-volume sales research) python-urllib"

CACHE_DIR = Path(os.environ.get("CRPI_CACHE", Path.home() / ".cache" / "cr-prospect-intel"))
DEFAULT_TTL = int(os.environ.get("CRPI_CACHE_TTL", 6 * 3600))  # seconds
FRESH = os.environ.get("CRPI_FRESH") == "1"

FREE_MAIL = {
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "msn.com",
    "yahoo.com", "ymail.com", "icloud.com", "me.com", "mac.com", "aol.com",
    "protonmail.com", "proton.me", "gmx.com", "gmx.net", "zoho.com", "yandex.com",
    "mail.com", "hey.com", "fastmail.com", "pm.me",
}


def _cache_path(url: str) -> Path:
    return CACHE_DIR / (hashlib.sha256(url.encode()).hexdigest()[:32] + ".json")


def fetch(url: str, headers: dict | None = None, timeout: int = 20, ttl: int | None = None,
          browser_ua: bool = False, max_bytes: int = 6_000_000) -> dict:
    """GET a URL. Returns {"url","status","final_url","text","fetched_at","cached"} or {"_error"}.

    Responses are cached on disk (CRPI_CACHE) for `ttl` seconds; set CRPI_FRESH=1 to bypass.
    """
    ttl = DEFAULT_TTL if ttl is None else ttl
    cp = _cache_path(url + json.dumps(headers or {}, sort_keys=True))
    if not FRESH and cp.exists() and time.time() - cp.stat().st_mtime < ttl:
        try:
            d = json.loads(cp.read_text())
            d["cached"] = True
            return d
        except Exception:
            pass
    h = {
        "User-Agent": UA_BROWSER if browser_ua else UA_TOOL,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip",
    }
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(max_bytes)
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            charset = r.headers.get_content_charset() or "utf-8"
            d = {
                "url": url,
                "status": r.status,
                "final_url": r.geturl(),
                "content_type": r.headers.get("Content-Type", ""),
                "text": raw.decode(charset, errors="replace"),
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "cached": False,
            }
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read(4000).decode("utf-8", errors="replace")
        except Exception:
            pass
        return {"_error": f"HTTP {e.code}", "status": e.code, "url": url, "text": body}
    except Exception as e:  # DNS, TLS, proxy, timeout
        return {"_error": f"{type(e).__name__}: {str(e)[:160]}", "url": url}
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cp.write_text(json.dumps(d))
    except Exception:
        pass
    return d


def fetch_json(url: str, **kw) -> dict | list:
    r = fetch(url, **kw)
    if "_error" in r:
        return r
    try:
        return json.loads(r["text"])
    except Exception:
        return {"_error": "not JSON", "url": url, "head": r["text"][:200]}


def ok(x) -> bool:
    return not (isinstance(x, dict) and "_error" in x)


def domain_from_email(email: str) -> str | None:
    m = re.search(r"@([A-Za-z0-9.-]+\.[A-Za-z]{2,})$", (email or "").strip())
    return m.group(1).lower() if m else None


def brand_core(name: str) -> str:
    """'The Gym-Shark Co.' -> 'gymshark' (drops legal suffixes and punctuation)."""
    s = (name or "").lower()
    s = re.sub(r"\b(inc|llc|ltd|co|corp|corporation|company|limited|gmbh|plc|the|official|hq)\b\.?", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)


def label_from_domain(domain: str) -> str:
    parts = domain.lower().split(".")
    if len(parts) >= 3 and parts[-2] in {"co", "com", "org", "net"}:
        return parts[-3]
    return parts[-2] if len(parts) >= 2 else parts[0]


def emit(obj) -> None:
    json.dump(obj, sys.stdout, indent=2, ensure_ascii=False, default=str)
    sys.stdout.write("\n")


def median(xs):
    xs = sorted(x for x in xs if isinstance(x, (int, float)))
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def pct(xs, p):
    xs = sorted(x for x in xs if isinstance(x, (int, float)))
    if not xs:
        return None
    k = (len(xs) - 1) * p
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)
