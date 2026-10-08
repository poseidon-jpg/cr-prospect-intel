#!/usr/bin/env python3
"""Public social signals without keys, plus the account-constellation detector.

Subcommands
  tiktok HANDLE [HANDLE...]          profile stats + last ~13 videos (official embed page, keyless)
  exists HANDLE [HANDLE...]          TikTok existence via official oEmbed (400 = no such account)
  tiktok-history HANDLE              full dated history via yt-dlp (opt-in, local; falls back to embed card)
  youtube @HANDLE|UCxxxx             channel id, subscriber text, last ~15 uploads with views (RSS)
  variants BRAND [--handle H]        candidate handles clip/UGC networks commonly use
  constellation BRAND --handle H [--domain D] [--extra h1,h2] [--max 60]
                                     generate variants -> check which exist -> score affiliation
  instagram HANDLE                   needs SCRAPECREATORS_API_KEY (Tier 1); otherwise prints manual recipe

Data sources (all official/public, no login):
  https://www.tiktok.com/oembed?url=https://www.tiktok.com/@HANDLE
  https://www.tiktok.com/embed/@HANDLE   (creator embed card: followers, likes, bio, recent views)
  https://www.youtube.com/@HANDLE  +  https://www.youtube.com/feeds/videos.xml?channel_id=UC...

Rules: low volume, polite, cached. If a platform blocks the request, report "not reachable from here",
never "account does not exist". Use the host's browser tool as the fallback for blocked pages.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from _common import brand_core, emit, fetch, fetch_json, median, ok  # noqa: E402

SUFFIXES = ["clips", "clip", "clipz", "edits", "edit", "moments", "highlights", "daily", "hq", "news", "tv",
            "fans", "fan", "fanpage", "updates", "media", "pod", "podcast", "show", "official", "world",
            "archive", "vault", "central", "nation", "army", "community", "ugc", "reviews", "tips", "life", "app"]
PREFIXES = ["the", "get", "try", "official", "real", "its", "best", "daily", "team", "drink", "shop", "wear"]
SEPS = ["", ".", "_"]


def gen_variants(brand: str, handle: str | None = None, limit: int = 120) -> list[str]:
    cores = {brand_core(brand)}
    if handle:
        cores.add(handle.lower().lstrip("@"))
    cores = {c for c in cores if c}
    # Ordered by observed likelihood so a 40-check budget covers the most common patterns first
    # (stress test 2026-10-08: the old order spent the whole budget on clip-suffix separator permutations).
    out: list[str] = []
    for c in sorted(cores):
        out.append(c)
    for c in sorted(cores):
        out += [f"{c}{s}" for s in SUFFIXES]                      # brandclips, branddaily...
        out += [f"{p}{c}" for p in PREFIXES]                      # thebrand, getbrand, drinkbrand...
        out += [f"{c}.{s}" for s in SUFFIXES[:12]] + [f"{c}_{s}" for s in SUFFIXES[:12]]
        out += [f"{p}.{c}" for p in PREFIXES[:6]]
        out += [f"{c}{n}" for n in ["1", "2", "247", "365", "x", "us", "uk"]]
        out += [f"{c}.{s}" for s in SUFFIXES[12:]] + [f"{c}_{s}" for s in SUFFIXES[12:]]
    seen, res = set(), []
    for h in out:
        h = h[:24]  # TikTok max 24 chars
        if h not in seen and re.fullmatch(r"[a-z0-9._]{2,24}", h) and not h.endswith("."):
            seen.add(h)
            res.append(h)
    return res[:limit]


# ---------------- TikTok ----------------

def tiktok_exists(handle: str) -> dict:
    h = handle.lstrip("@")
    url = "https://www.tiktok.com/oembed?url=" + urllib.parse.quote(f"https://www.tiktok.com/@{h}", safe=":/@")
    d = fetch_json(url, ttl=24 * 3600)
    if isinstance(d, dict) and d.get("embed_type") == "profile":
        return {"handle": h, "exists": True, "display_name": d.get("author_name"), "source": url}
    if isinstance(d, dict) and (d.get("code") == 400 or d.get("status") == 400 or "400" in str(d.get("_error", ""))):
        return {"handle": h, "exists": False, "source": url}
    return {"handle": h, "exists": None, "detail": d.get("_error") if isinstance(d, dict) else "unexpected",
            "source": url}


def tiktok_profile(handle: str) -> dict:
    h = handle.lstrip("@")
    url = f"https://www.tiktok.com/embed/@{h}"
    r = fetch(url, browser_ua=True, ttl=6 * 3600)
    if not ok(r):
        return {"handle": h, "_error": r.get("_error"), "source": url,
                "fallback": "Open the URL with the browser tool, or use ScrapeCreators /v1/tiktok/profile"}
    m = re.search(r'<script[^>]+id="__FRONTITY_CONNECT_STATE__"[^>]*>(.*?)</script>', r["text"], re.S)
    if not m:
        return {"handle": h, "_error": "embed state not found (blocked or layout changed)", "source": url}
    try:
        state = json.loads(m.group(1))
        data = state["source"]["data"]
        node = data.get(f"/embed/@{h}") or next(v for k, v in data.items() if k.startswith("/embed/@"))
    except Exception as e:
        return {"handle": h, "_error": f"parse: {e}", "source": url}
    u = node.get("userInfo") or {}
    vids = node.get("videoList") or []
    plays = [v.get("playCount") for v in vids if isinstance(v.get("playCount"), (int, float))]
    for v in vids:
        v["_date"] = tiktok_id_date(v.get("id"))
    dated = sorted((v for v in vids if v["_date"]), key=lambda v: v["_date"], reverse=True)
    now = datetime.now(timezone.utc).date()
    last30 = [v for v in dated if (now - date.fromisoformat(v["_date"])).days <= 30]
    span_days = ((date.fromisoformat(dated[0]["_date"]) - date.fromisoformat(dated[-1]["_date"])).days
                 if len(dated) > 1 else None)
    return {
        "platform": "tiktok", "handle": h, "source": url,
        "exists": bool(u) and not node.get("isError"),
        "nickname": u.get("nickname"), "verified": u.get("verified"), "private": u.get("privateAccount"),
        "bio": u.get("signature"),
        "followers": u.get("followerCount"), "following": u.get("followingCount"), "total_likes": u.get("heartCount"),
        "recent_videos_sampled": len(vids),
        "recent_views_median": median(plays), "recent_views_max": max(plays) if plays else None,
        "recent_views_min": min(plays) if plays else None,
        "last_post_date": dated[0]["_date"] if dated else None,
        "posts_in_sample_last_30d": len(last30),
        "median_views_last_30d": median([v.get("playCount") for v in last30]),
        "sample_span_days": span_days,
        "approx_posts_per_week": round(len(dated) / span_days * 7, 1) if span_days else None,
        "recent_videos": [{"id": v.get("id"), "date": v["_date"], "views": v.get("playCount"),
                           "caption": (v.get("desc") or "")[:160],
                           "url": f"https://www.tiktok.com/@{h}/video/{v.get('id')}"} for v in vids],
        "caveats": "Embed shows the latest ~13 videos (pinned ones included, which skew max). Dates are decoded "
                   "from the video ID (id >> 32 = Unix seconds, accurate to the day). Not full history.",
    }


def tiktok_id_date(vid) -> str | None:
    """TikTok video IDs are snowflake-style: the high 32 bits are the creation time in Unix seconds."""
    try:
        ts = int(vid) >> 32
        if 1_400_000_000 < ts < 2_100_000_000:
            return datetime.fromtimestamp(ts, timezone.utc).date().isoformat()
    except (TypeError, ValueError):
        pass
    return None


# ---------------- YouTube ----------------

def youtube_channel(ident: str) -> dict:
    ident = ident.strip()
    if ident.startswith("UC") and len(ident) == 24:
        cid, page_url, subs, vids_text, title = ident, None, None, None, None
    else:
        h = ident if ident.startswith("@") else "@" + ident
        page_url = f"https://www.youtube.com/{h}"
        r = fetch(page_url, browser_ua=True, ttl=12 * 3600)
        if not ok(r):
            return {"handle": h, "_error": r.get("_error"), "source": page_url}
        t = r["text"]
        m = re.search(r'"(?:externalId|channelId)":"(UC[\w-]{22})"', t) or \
            re.search(r'<meta itemprop="identifier" content="(UC[\w-]{22})"', t)
        if not m:
            return {"handle": h, "_error": "channel id not found (consent wall or layout change)", "source": page_url}
        cid = m.group(1)
        s = re.search(r'"subscriberCountText":\{.*?"(?:simpleText|content)":"([^"]+)"', t)
        subs = s.group(1) if s else None
        vc = re.search(r'"videosCountText":\{"runs":\[\{"text":"([^"]+)"', t)
        vids_text = vc.group(1) if vc else None
        ti = re.search(r'<meta property="og:title" content="([^"]+)"', t)
        title = ti.group(1) if ti else None
    rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
    r = fetch(rss, ttl=6 * 3600)
    items = []
    if ok(r):
        ns = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/",
              "yt": "http://www.youtube.com/xml/schemas/2015"}
        try:
            root = ET.fromstring(r["text"])
            for e in root.findall("a:entry", ns):
                st = e.find("m:group/m:community/m:statistics", ns)
                link = e.find("a:link", ns)
                href = link.get("href") if link is not None else None
                items.append({"title": e.findtext("a:title", namespaces=ns),
                              "published": e.findtext("a:published", namespaces=ns),
                              "views": int(st.get("views")) if st is not None and st.get("views") else None,
                              "url": href, "is_short": bool(href and "/shorts/" in href)})
        except Exception as ex:
            items = [{"_error": f"rss parse {ex}"}]
    views = [i.get("views") for i in items if isinstance(i.get("views"), int)]
    dates = sorted(i["published"][:10] for i in items if i.get("published"))
    return {"platform": "youtube", "channel_id": cid, "title": title, "subscribers_text": subs,
            "videos_text": vids_text, "source": page_url or rss, "rss": rss,
            "recent_uploads": items, "recent_views_median": median(views),
            "upload_window": (dates[0], dates[-1]) if dates else None,
            "uploads_in_window": len(dates),
            "caveats": "RSS = latest ~15 uploads. For full inventory use yt-dlp --flat-playlist (needs deno>=2.3 "
                       "or node>=22) or YouTube Data API playlistItems (1 unit/50 videos)."}


# ---------------- Instagram (Tier 1 only) ----------------

def instagram(handle: str) -> dict:
    key = os.environ.get("SCRAPECREATORS_API_KEY")
    h = handle.lstrip("@")
    if not key:
        return {"handle": h, "tier": "manual",
                "recipe": [f"Browser tool: open https://www.instagram.com/{h}/ (public view, read followers/posts/bio).",
                           f'Search: site:instagram.com "{h}"',
                           "Tier 1: export SCRAPECREATORS_API_KEY (100 free credits) and rerun."]}
    url = f"https://api.scrapecreators.com/v1/instagram/profile?handle={urllib.parse.quote(h)}"
    d = fetch_json(url, headers={"x-api-key": key}, ttl=24 * 3600)
    return {"handle": h, "source": "scrapecreators /v1/instagram/profile", "data": d}


# ---------------- Constellation ----------------

def _shingles(s: str, k: int = 3) -> set:
    w = re.findall(r"[a-z0-9#@]+", (s or "").lower())
    return {" ".join(w[i:i + k]) for i in range(max(0, len(w) - k + 1))}


def score_candidate(c: dict, brand: str, official: str, domain: str | None, peers: list[dict]) -> dict:
    core = brand_core(brand)
    off = official.lower().lstrip("@")
    h = c["handle"].lower()
    if h == off:
        return {"score": 100, "label": "CONFIRMED OFFICIAL", "signals": ["is the official handle"]}
    sig, s = [], 0
    sim = max(difflib.SequenceMatcher(None, re.sub(r"[._]", "", h), x).ratio() for x in {core, off} if x)
    if core and core in re.sub(r"[._]", "", h):
        s += 15; sig.append(f"handle contains '{core}'")
    elif sim >= 0.75:
        s += 10; sig.append(f"handle similar ({sim:.2f})")
    bio = (c.get("bio") or "").lower()
    if f"@{off}" in bio or (domain and domain.lower() in bio):
        s += 30; sig.append("bio tags the official account or brand domain (CR briefs often REQUIRE this)")
    elif core and core in re.sub(r"[^a-z0-9]", "", bio):
        s += 15; sig.append("bio mentions brand name")
    caps = [v.get("caption", "") for v in c.get("recent_videos", [])]
    if caps:
        hits = sum(1 for x in caps if core in re.sub(r"[^a-z0-9]", "", x.lower()) or f"@{off}" in x.lower())
        share = hits / len(caps)
        if share >= 0.5:
            s += 25; sig.append(f"{hits}/{len(caps)} recent captions mention brand")
        elif share >= 0.2:
            s += 12; sig.append(f"{hits}/{len(caps)} recent captions mention brand")
    mine = set().union(*[_shingles(x) for x in caps]) if caps else set()
    best = 0.0
    for p in peers:
        if p is c or not p.get("recent_videos"):
            continue
        other = set().union(*[_shingles(v.get("caption", "")) for v in p["recent_videos"]])
        if mine and other:
            best = max(best, len(mine & other) / max(1, len(mine | other)))
    if best >= 0.25:
        s += 20; sig.append(f"captions overlap with another candidate (Jaccard {best:.2f}) = coordinated template")
    elif best >= 0.1:
        s += 8; sig.append(f"some caption overlap with another candidate ({best:.2f})")
    label = ("LIKELY AFFILIATED" if s >= 70 else "POSSIBLY AFFILIATED" if s >= 40 else
             "NAME MATCH ONLY" if s > 0 else "UNRELATED")
    if c.get("nickname") and brand_core(c["nickname"]) == core and not c.get("verified"):
        sig.append("display name copies brand exactly but unverified: fan page OR impersonation, check manually")
    return {"score": min(s, 99), "label": label, "signals": sig}


def constellation(brand: str, handle: str, domain: str | None, extra: list[str], max_checks: int) -> dict:
    cands = gen_variants(brand, handle)[:max_checks]
    for e in extra:
        e = e.lower().lstrip("@")
        if e and e not in cands:
            cands.insert(0, e)
    existing, checked, unknown = [], 0, 0
    for h in cands:
        r = tiktok_exists(h)
        checked += 1
        if r["exists"] is None:
            unknown += 1
            if "403" in str(r.get("detail")):
                return {"_error": "TikTok edge returned 403 (rate limited). STOP. Wait 30+ minutes; do not retry in a loop.",
                        "partial_existing": existing, "checked": checked}
            if unknown >= 5 and not existing:
                return {"_error": "TikTok oEmbed not reachable from this environment",
                        "fallback": "Run from a laptop (Claude Code) or use the browser tool / ScrapeCreators search."}
        elif r["exists"]:
            existing.append(h)
        time.sleep(1.2)  # TikTok's edge (Akamai) blocks bursts: ~150 parallel calls got an IP 'Access Denied' in testing
    profiles, unprofiled = [], []
    for h in existing:
        p = tiktok_profile(h)
        if "403" in str(p.get("_error")):
            unprofiled += existing[existing.index(h):]
            break
        if p.get("exists"):
            profiles.append(p)
        else:
            unprofiled.append(h)
        time.sleep(2.0)
    for p in profiles:
        p["affiliation"] = score_candidate(p, brand, handle, domain, profiles)
    profiles.sort(key=lambda p: -p["affiliation"]["score"])
    slim = [{k: p.get(k) for k in ("handle", "nickname", "verified", "bio", "followers", "total_likes",
                                   "recent_views_median", "source")} | {"affiliation": p["affiliation"]}
            for p in profiles]
    total_followers = sum((p.get("followers") or 0) for p in profiles
                          if p["affiliation"]["label"] in ("LIKELY AFFILIATED", "POSSIBLY AFFILIATED"))
    return {
        "brand": brand, "official_handle": handle, "platform": "tiktok",
        "variants_checked": checked, "existing_accounts": len(existing), "unreachable_checks": unknown,
        "accounts": slim,
        "exists_but_card_unreachable": unprofiled,
        "summary": {
            "likely_affiliated": [p["handle"] for p in slim if p["affiliation"]["label"] == "LIKELY AFFILIATED"],
            "possibly_affiliated": [p["handle"] for p in slim if p["affiliation"]["label"] == "POSSIBLY AFFILIATED"],
            "followers_in_affiliated_cluster": total_followers,
        },
        "method": "Handle variants -> official oEmbed existence -> official embed card (bio, captions) -> rubric. "
                  "Variant generation misses accounts with unrelated names (e.g. theme pages): add them with --extra "
                  "after searching TikTok/Google for the brand's @handle in bios and captions.",
        "interpretation": "Affiliation is an evidence score, never a fact about who runs an account.",
    }


def tiktok_history(handle: str, limit: int = 200) -> dict:
    """Full dated video history via yt-dlp (opt-in, runs on the rep's machine).
    Needs: pip install -U "yt-dlp[default,curl-cffi]". Public data, no login, no cookies. yt-dlp's TikTok
    extractor breaks periodically (issues #17500, #17403); if it fails, fall back to the embed card."""
    import shutil
    import subprocess
    exe = shutil.which("yt-dlp")
    if not exe:
        return {"handle": handle, "skipped": "yt-dlp not installed (optional)",
                "install": 'pip install -U "yt-dlp[default,curl-cffi]"'}
    h = handle.lstrip("@")
    try:
        r = subprocess.run([exe, "--flat-playlist", "-J", "--playlist-end", str(limit), "--impersonate", "chrome",
                            "--sleep-requests", "1", f"https://www.tiktok.com/@{h}"],
                           capture_output=True, text=True, timeout=240)
        d = json.loads(r.stdout or "{}")
    except Exception as e:
        return {"handle": h, "_error": f"{type(e).__name__}: {str(e)[:200]}"}
    if not d.get("entries"):
        return {"handle": h, "_error": (r.stderr or "no entries")[-300:], "fallback": "social_probe.py tiktok"}
    rows = []
    for e in d["entries"]:
        ts = e.get("timestamp")
        day = datetime.fromtimestamp(ts, timezone.utc).date().isoformat() if ts else tiktok_id_date(e.get("id"))
        rows.append({"date": day, "views": e.get("view_count"), "likes": e.get("like_count"),
                     "comments": e.get("comment_count"), "shares": e.get("repost_count"),
                     "caption": (e.get("description") or e.get("title") or "")[:140], "id": e.get("id")})
    rows = [r for r in rows if r["date"]]
    rows.sort(key=lambda r: r["date"], reverse=True)
    now = datetime.now(timezone.utc).date()

    def window(days):
        w = [r for r in rows if (now - date.fromisoformat(r["date"])).days <= days]
        return {"posts": len(w), "median_views": median([r["views"] for r in w]),
                "top": max(w, key=lambda r: r["views"] or 0) if w else None}
    return {"platform": "tiktok", "handle": h, "source": "yt-dlp flat playlist (public profile)",
            "videos_returned": len(rows), "first": rows[-1]["date"] if rows else None,
            "last": rows[0]["date"] if rows else None,
            "last_30d": window(30), "last_90d": window(90), "last_365d": window(365),
            "videos": rows[:limit]}


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("tiktok", "exists"):
        p = sub.add_parser(name)
        p.add_argument("handles", nargs="+")
    p = sub.add_parser("youtube"); p.add_argument("ident")
    p = sub.add_parser("tiktok-history"); p.add_argument("handle"); p.add_argument("--limit", type=int, default=200)
    p = sub.add_parser("instagram"); p.add_argument("handle")
    p = sub.add_parser("variants"); p.add_argument("brand"); p.add_argument("--handle")
    p = sub.add_parser("constellation")
    p.add_argument("brand"); p.add_argument("--handle", required=True); p.add_argument("--domain")
    p.add_argument("--extra", default=""); p.add_argument("--max", type=int, default=40)
    a = ap.parse_args()
    if a.cmd == "tiktok":
        emit([tiktok_profile(h) for h in a.handles])
    elif a.cmd == "exists":
        emit([tiktok_exists(h) for h in a.handles])
    elif a.cmd == "tiktok-history":
        emit(tiktok_history(a.handle, a.limit))
    elif a.cmd == "youtube":
        emit(youtube_channel(a.ident))
    elif a.cmd == "instagram":
        emit(instagram(a.handle))
    elif a.cmd == "variants":
        emit(gen_variants(a.brand, a.handle))
    elif a.cmd == "constellation":
        emit(constellation(a.brand, a.handle, a.domain, [x for x in a.extra.split(",") if x], a.max))


if __name__ == "__main__":
    main()
