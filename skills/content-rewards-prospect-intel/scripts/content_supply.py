#!/usr/bin/env python3
"""Content-supply audit: what long-form source material exists that could be clipped.

Usage:
  python3 content_supply.py podcasts "Brand or Founder Name" [--person "Jane Doe"] [--limit 8]
  python3 content_supply.py feed https://example.com/podcast.rss [--person "Jane Doe"]

podcasts: iTunes Search API (keyless) -> each show's RSS -> episode count, cadence, recency,
          and (with --person) episodes whose title/notes mention that person = guest appearances.
feed:     one RSS feed directly.

A founder with 100+ hours of podcast/YouTube/livestream footage and little short-form distribution
is the highest-fit clipping prospect. This script measures the first half of that sentence.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(__file__))
from _common import emit, fetch, fetch_json, median, ok  # noqa: E402

IT = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"


def parse_feed(url: str, person: str | None = None, max_items: int = 400) -> dict:
    r = fetch(url, ttl=12 * 3600, timeout=30)
    if not ok(r):
        return {"feed": url, "_error": r.get("_error")}
    try:
        root = ET.fromstring(r["text"].encode("utf-8", errors="ignore"))
    except Exception as e:
        return {"feed": url, "_error": f"xml: {e}"}
    ch = root.find("channel")
    if ch is None:
        return {"feed": url, "_error": "no channel"}
    items = ch.findall("item")[:max_items]
    dates, durs, mentions = [], [], []
    pat = re.compile(re.escape(person), re.I) if person else None
    for it in items:
        d = it.findtext("pubDate")
        try:
            dates.append(parsedate_to_datetime(d))
        except Exception:
            pass
        dur = it.findtext(f"{IT}duration") or ""
        secs = None
        if re.fullmatch(r"\d+", dur):
            secs = int(dur)
        elif re.fullmatch(r"\d+:\d{2}(:\d{2})?", dur):
            p = [int(x) for x in dur.split(":")]
            secs = p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]
        if secs:
            durs.append(secs)
        if pat:
            blob = " ".join(filter(None, [it.findtext("title"), it.findtext("description"),
                                          it.findtext(f"{IT}summary")]))
            if pat.search(blob):
                mentions.append({"title": it.findtext("title"), "date": d, "link": it.findtext("link")})
    dates = sorted((x for x in dates if x), reverse=True)
    gaps = [(dates[i] - dates[i + 1]).days for i in range(min(len(dates) - 1, 20))]
    hours = round(sum(durs) / 3600, 1) if durs else None
    return {
        "feed": url, "show": ch.findtext("title"), "author": ch.findtext(f"{IT}author"),
        "episodes_in_feed": len(items), "latest": dates[0].date().isoformat() if dates else None,
        "first": dates[-1].date().isoformat() if dates else None,
        "median_days_between_episodes": median(gaps),
        "total_hours_in_feed": hours,
        "active": bool(dates) and (datetime.now(dates[0].tzinfo) - dates[0]).days <= 45,
        "person_mentions": mentions[:25] if pat else None,
    }


def podcasts(term: str, person: str | None, limit: int) -> dict:
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(
        {"media": "podcast", "term": term, "limit": limit, "country": "us"})
    d = fetch_json(url, ttl=24 * 3600)
    if not ok(d):
        return {"_error": d.get("_error"), "source": url}
    shows = []
    for res in d.get("results", []):
        f = res.get("feedUrl")
        entry = {"name": res.get("collectionName"), "artist": res.get("artistName"),
                 "itunes_episode_count": res.get("trackCount"), "genre": res.get("primaryGenreName"),
                 "apple_url": res.get("collectionViewUrl"), "feed": f}
        blob = f"{res.get('collectionName','')} {res.get('artistName','')}".lower()
        entry["name_match"] = all(w in blob for w in term.lower().split())
        if f:
            entry["feed_stats"] = parse_feed(f, person)
        shows.append(entry)
    total_hours = sum((s.get("feed_stats") or {}).get("total_hours_in_feed") or 0 for s in shows)
    shows.sort(key=lambda s: not s.get("name_match"))
    return {"source": url, "shows": shows, "total_hours_across_feeds": round(total_hours, 1),
            "note": "Search matches by name; confirm each show is the prospect's own (host/author) vs a guest spot."}


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("podcasts"); p.add_argument("term"); p.add_argument("--person"); p.add_argument("--limit", type=int, default=8)
    p = sub.add_parser("feed"); p.add_argument("url"); p.add_argument("--person")
    a = ap.parse_args()
    emit(podcasts(a.term, a.person, a.limit) if a.cmd == "podcasts" else parse_feed(a.url, a.person))


if __name__ == "__main__":
    main()
