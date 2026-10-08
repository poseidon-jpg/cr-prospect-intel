#!/usr/bin/env python3
"""Environment check. Tells the agent which research mode to use. Run this first.

  python3 doctor.py          human table + JSON on the last line
Modes:
  SCRIPTS   open network from this shell: run the bundled scripts (fastest, most structured)
  HYBRID    some endpoints reachable: run what works, use WebFetch/browser for the rest
  AGENT     shell network is locked down (common in cloud sandboxes): use WebSearch/WebFetch and the
            browser tool with the exact URLs in references/source-recipes.md
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
from _common import fetch  # noqa: E402

PROBES = {
    "dns (dns.google)": "https://dns.google/resolve?name=example.com&type=TXT",
    "tiktok oembed": "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@tiktok",
    "tiktok embed card": "https://www.tiktok.com/embed/@tiktok",
    "youtube": "https://www.youtube.com/feeds/videos.xml?channel_id=UCBR8-60-B28hp2BmDPdntcQ",
    "content rewards": "https://contentrewards.com/c/discover",
    "greenhouse ats": "https://boards-api.greenhouse.io/v1/boards/discord/jobs",
    "itunes podcasts": "https://itunes.apple.com/search?media=podcast&term=test&limit=1",
    "google news rss": "https://news.google.com/rss/search?q=test",
    "rdap": "https://rdap.org/domain/example.com",
}
KEYS = {
    "SCRAPECREATORS_API_KEY": "TikTok/IG/YouTube/X/LinkedIn public data (100 free credits)",
    "HUNTER_API_KEY": "person + company enrichment, email verify (50 free/mo)",
    "PDL_API_KEY": "identity resolution with likelihood score (100 free/mo)",
    "YOUTUBE_API_KEY": "full channel inventory (10k units/day free)",
    "XAI_API_KEY": "live X search with citations (paid per result)",
    "SERPAPI_API_KEY": "Google Ads Transparency lookups (250 free/mo)",
}


def main() -> None:
    os.environ["CRPI_FRESH"] = "1"
    with ThreadPoolExecutor(max_workers=9) as ex:
        res = dict(zip(PROBES, ex.map(lambda u: fetch(u, timeout=10, ttl=0, browser_ua=True), PROBES.values())))
    reach = {k: ("OK" if "_error" not in v and v.get("status", 0) < 400 else v.get("_error", "fail")[:50])
             for k, v in res.items()}
    n_ok = sum(1 for v in reach.values() if v == "OK")
    mode = "SCRIPTS" if n_ok >= 7 else "HYBRID" if n_ok >= 2 else "AGENT"
    tools = {t: bool(shutil.which(t)) for t in ("yt-dlp", "deno", "node", "maigret", "dig")}
    keys = {k: bool(os.environ.get(k)) for k in KEYS}
    print(f"Python {sys.version.split()[0]}  |  mode: {mode}  ({n_ok}/{len(PROBES)} endpoints reachable)")
    for k, v in reach.items():
        print(f"  {'WORKING ' if v == 'OK' else 'BLOCKED '} {k:22s} {'' if v == 'OK' else v}")
    for t, v in tools.items():
        print(f"  {'FOUND   ' if v else 'OPTIONAL'} {t}")
    for k, v in keys.items():
        print(f"  {'SET     ' if v else 'OPTIONAL'} {k:24s} {KEYS[k]}")
    if mode != "SCRIPTS":
        print("  -> Use WebSearch/WebFetch/browser with references/source-recipes.md for blocked sources.")
        print("  -> FIX (Claude.ai / Cowork): Settings > Capabilities > Code execution > Domain allowlist = 'All domains'")
        print("     (or add the domains in README 'Network setup'), then start a NEW chat. Claude Code in a")
        print("     local terminal uses your normal internet and needs no change.")
    print(json.dumps({"mode": mode, "reachable": reach, "tools": tools, "keys": keys}))


if __name__ == "__main__":
    main()
