#!/usr/bin/env python3
"""Live Content Rewards case library + agency matcher (public pages only).

Subcommands
  discover                         featured campaigns from https://contentrewards.com/c/discover (structured)
  org HANDLE [HANDLE...]           an organization/agency profile: https://contentrewards.com/c/HANDLE
  campaign UUID                    one campaign page: per-platform CPM, payout caps, budget, brief, views
  match --keywords "a,b" [--category Apps] [--top 8]
                                   rank live + seed campaigns by similarity to the prospect

Public surface (verified 2026-10-08): /c/discover embeds ~50 campaign objects (brand, title, category,
platforms, type, ratePer1kLabel, budgetTotalRaw, budgetSpentRaw, creatorCountRaw, organizationProfileHandle).
/c/{handle} lists every campaign an org has run. /discover/{uuid} shows the brief and results.
robots.txt disallows /api/ -- this script never touches it.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from _common import emit, fetch, ok  # noqa: E402

BASE = "https://contentrewards.com"
SEED = Path(__file__).resolve().parent.parent / "assets" / "cr_seed_library.json"
BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "br", "section", "article", "span", "a", "button", "tr"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        elif tag in BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def html_lines(text: str) -> list[str]:
    p = _Text()
    p.feed(text)
    lines = [re.sub(r"\s+", " ", html.unescape(x)).strip() for x in "".join(p.out).split("\n")]
    return [x.replace("⁦", "").replace("⁩", "") for x in lines if x]


def _rsc_payload(page: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', page, re.S)
    out = []
    for c in chunks:
        try:
            out.append(json.loads('"' + c + '"'))
        except Exception:
            out.append(c.replace('\\"', '"'))
    return "".join(out)


def _objects_with(payload: str, key: str) -> list[dict]:
    res, i = [], 0
    while True:
        i = payload.find('{"' + key + '"', i)
        if i < 0:
            break
        depth, j, in_str, esc = 0, i, False, False
        while j < len(payload):
            ch = payload[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        try:
            res.append(json.loads(payload[i:j + 1]))
        except Exception:
            pass
        i = j + 1
    return res


def discover() -> dict:
    url = f"{BASE}/c/discover"
    r = fetch(url, browser_ua=True, ttl=6 * 3600)
    if not ok(r):
        return {"_error": r.get("_error"), "source": url,
                "fallback": "WebFetch or browser-open https://contentrewards.com/c/discover and read the cards"}
    objs = _objects_with(_rsc_payload(r["text"]), "availableBudgetRaw")
    camps = []
    for o in objs:
        spent, total = o.get("budgetSpentRaw"), o.get("budgetTotalRaw")
        camps.append({
            "id": o.get("id"), "organizer": o.get("brand"), "title": o.get("title"),
            "category": o.get("category") or None, "type": o.get("type"),
            "rate_per_1k": (o.get("ratePer1kLabel") or "").replace("$$", "$"),
            "platforms": o.get("platforms"), "budget_total": total, "budget_spent": spent,
            "creators": o.get("creatorCountRaw"), "submissions": o.get("submissionCountRaw"),
            "requires_application": o.get("requiresApplication"), "verified_org": o.get("isVerified"),
            "org_handle": o.get("organizationProfileHandle"),
            "description": (o.get("description") or "")[:240],
            "url": f"{BASE}/discover/{o.get('id')}" if o.get("id") else None,
            "org_url": f"{BASE}/c/{o['organizationProfileHandle']}" if o.get("organizationProfileHandle") else None,
        })
    if not camps:
        lines = html_lines(r["text"])
        return {"source": url, "structured": False, "note": "RSC layout changed; raw text lines returned",
                "lines": lines[:400]}
    return {"source": url, "fetched_at": r.get("fetched_at"), "structured": True, "count": len(camps),
            "campaigns": camps}


def org(handle: str) -> dict:
    url = f"{BASE}/c/{handle}"
    r = fetch(url, browser_ua=True, ttl=12 * 3600)
    if not ok(r):
        return {"handle": handle, "_error": r.get("_error"), "source": url}
    lines = html_lines(r["text"])
    title = re.search(r"<title>(.*?)</title>", r["text"], re.S)
    name = html.unescape(title.group(1)).replace(" | Content Rewards", "").strip() if title else handle
    count = None
    for k, ln in enumerate(lines[:40]):
        if ln == "Campaigns" and k and re.fullmatch(r"[\d,]+", lines[k - 1]):
            count = int(lines[k - 1].replace(",", ""))
            break
    camps = []
    for k, ln in enumerate(lines):
        if re.fullmatch(r"\$[\d.,]+/(1K|mo|post)", ln) and k >= 2:
            cnt = lines[k - 1]
            t = lines[k - 2]
            age = lines[k - 3] if k >= 3 else None
            if re.fullmatch(r"[\d,/]+", cnt):
                camps.append({"title": t, "rate": ln, "participants": cnt, "age": age})
    members = next((ln for ln in lines if re.search(r"members$", ln)), None)
    return {"handle": handle, "name": name, "source": url, "campaign_count": count,
            "community": members, "campaigns_visible": camps[:120],
            "note": ("Campaign list loaded client-side (not in the page HTML as of 2026-10-08): open the URL with the "
                     "browser tool / WebFetch to read titles, rates and participants." if not camps else
                     "Newest first; counts are participants. Open a campaign for brief/results.")}


def campaign(uuid: str) -> dict:
    url = f"{BASE}/discover/{uuid}"
    r = fetch(url, browser_ua=True, ttl=6 * 3600)
    if not ok(r):
        return {"id": uuid, "_error": r.get("_error"), "source": url}
    L = html_lines(r["text"])
    out = {"id": uuid, "source": url, "final_url": r.get("final_url")}
    t = re.search(r"<title>(.*?)</title>", r["text"], re.S)
    out["title"] = html.unescape(t.group(1)).replace(" | Content Rewards", "").strip() if t else None
    plats = {}
    names = {"TikTok", "Instagram", "YouTube", "X", "facebook", "Facebook", "Twitter", "Snapchat", "Threads"}
    for k, ln in enumerate(L):
        if ln in names and k + 6 < len(L) and L[k + 1].startswith("Per 1K"):
            plats[ln.lower()] = {"per_1k": L[k + 2], "min_payout": L[k + 4] if "Min" in L[k + 3] else None,
                                 "max_payout": L[k + 6] if "Max" in L[k + 5] else None}
    out["platform_rates"] = plats
    for k, ln in enumerate(L):
        if ln == "Budget" and k + 2 < len(L):
            j = k + 1
            spent = L[j]
            if spent == "$" and j + 1 < len(L):  # "$" and the number render as separate nodes
                spent, j = "$" + L[j + 1], j + 1
            out["budget_spent"] = spent
            rem = L[j + 1] if j + 1 < len(L) else ""
            out["budget_remaining"] = rem.replace(" remaining", "")
            try:
                s = float(spent.replace("$", "").replace(",", ""))
                r_ = float(out["budget_remaining"].replace("$", "").replace(",", ""))
                out["budget_total_derived"] = round(s + r_)
            except ValueError:
                pass
        if ln == "Brief":
            brief = []
            for x in L[k + 1:k + 40]:
                if x in ("Content requirements", "Top clippers", "Reference materials"):
                    break
                brief.append(x)
            out["brief"] = brief
        if ln == "Content requirements":
            out["content_requirements"] = L[k + 1:k + 4]
        m = re.fullmatch(r"([\d.,]+[KMB]?)", ln)
        if m and k + 1 < len(L) and L[k + 1] == "views":
            out["total_views"] = ln
        if ln.startswith("Clippers in this campaign earn"):
            out["avg_earnings_line"] = ln
        if re.fullmatch(r"\d+ / \d+", ln) and "participants" not in out:
            out["participants"] = ln.split("/")[1].strip()
        if re.fullmatch(r"/ \d+", ln) and "participants" not in out:
            out["participants"] = ln[1:].strip()
    try:
        v = out.get("total_views", "")
        mult = {"K": 1e3, "M": 1e6, "B": 1e9}.get(v[-1:], 1)
        views = float(v.rstrip("KMB").replace(",", "")) * mult
        spent = float(out["budget_spent"].replace("$", "").replace(",", ""))
        out["effective_cpm_derived"] = round(spent / (views / 1000), 2)
    except Exception:
        out["effective_cpm_derived"] = None
    return out


def _tokens(s: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 2}


def match(keywords: list[str], category: str | None, top: int) -> dict:
    pool = []
    d = discover()
    if d.get("structured"):
        pool += [dict(c, origin="live /c/discover") for c in d["campaigns"]]
    if SEED.exists():
        seed = json.loads(SEED.read_text())
        pool += [dict(c, origin=f"seed {seed.get('verified_on')}") for c in seed.get("example_campaigns", [])]
    kw = set()
    for k in keywords:
        kw |= _tokens(k)
    scored = []
    for c in pool:
        text = " ".join(str(c.get(f, "")) for f in ("title", "organizer", "category", "description", "notes"))
        overlap = len(kw & _tokens(text))
        cat = 2 if category and (c.get("category") or "").lower() == category.lower() else 0
        if overlap or cat:
            scored.append((overlap * 2 + cat, c))
    scored.sort(key=lambda x: -x[0])
    return {"query": {"keywords": keywords, "category": category},
            "matches": [dict(c, match_score=s) for s, c in scored[:top]],
            "live_feed_ok": bool(d.get("structured")),
            "next_step": "Open the top 2-3 campaign URLs (campaign subcommand) to pull brief + results, and the "
                         "organizer's /c/{handle} page to see its full campaign history before naming an agency."}


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("discover")
    p = sub.add_parser("org"); p.add_argument("handles", nargs="+")
    p = sub.add_parser("campaign"); p.add_argument("uuid")
    p = sub.add_parser("match"); p.add_argument("--keywords", required=True); p.add_argument("--category")
    p.add_argument("--top", type=int, default=8)
    a = ap.parse_args()
    if a.cmd == "discover":
        emit(discover())
    elif a.cmd == "org":
        emit([org(h) for h in a.handles])
    elif a.cmd == "campaign":
        emit(campaign(a.uuid))
    elif a.cmd == "match":
        emit(match([k.strip() for k in a.keywords.split(",")], a.category, a.top))


if __name__ == "__main__":
    main()
