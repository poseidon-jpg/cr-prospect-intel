#!/usr/bin/env python3
"""Keyless company identity + official social handles from Wikidata.

Usage:
  python3 identity.py "Gymshark"                 search + best match
  python3 identity.py --qid Q56246099            a known entity
  python3 identity.py "Acme" --domain acme.com   prefer the entity whose official website matches the domain

Why: Wikidata often lists a brand's OFFICIAL handles (X, Instagram, YouTube channel id, TikTok, Facebook),
website, founding date, HQ and founders. Verified live 2026-10-08 on Gymshark (Q56246099): returned
@gymshark (IG/TikTok), YouTube UCma7hhYJ3bfEhZgw3xl77ww, X Gymshark + GymsharkCentral, founded 2012.
Coverage is strong for notable brands and thin for small ones. Treat it as corroboration plus a seed list
for the constellation step. A missing handle means "not on Wikidata", not "doesn't exist".

Endpoints (CC0, no key): wikidata.org/w/api.php?action=wbsearchentities and
wikidata.org/wiki/Special:EntityData/{QID}.json
"""
from __future__ import annotations

import argparse
import re
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from _common import emit, fetch_json, ok  # noqa: E402

PROPS = {
    "P856": "official_website", "P2002": "x_handles", "P2003": "instagram_handles",
    "P2397": "youtube_channel_ids", "P7085": "tiktok_handles", "P2013": "facebook_ids",
    "P4264": "linkedin_company_ids", "P571": "inception", "P159": "headquarters_qid",
    "P112": "founder_qids", "P169": "ceo_qids", "P1128": "employees", "P452": "industry_qids",
    "P749": "parent_org_qids", "P355": "subsidiary_qids", "P1278": "lei", "P414": "stock_exchange_qids",
    "P249": "ticker",
}


def _val(snak):
    v = (snak.get("mainsnak", {}).get("datavalue") or {}).get("value")
    if isinstance(v, dict):
        return v.get("id") or v.get("time") or v.get("amount") or v.get("text")
    return v


def labels(qids: list[str]) -> dict:
    if not qids:
        return {}
    url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&languages=en&format=json&ids="
           + "|".join(qids[:50]))
    d = fetch_json(url, ttl=30 * 24 * 3600)
    if not ok(d):
        return {}
    return {q: (e.get("labels", {}).get("en", {}) or {}).get("value") for q, e in (d.get("entities") or {}).items()}


def entity(qid: str) -> dict:
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    d = fetch_json(url, ttl=7 * 24 * 3600)
    if not ok(d):
        return {"qid": qid, "_error": d.get("_error"), "source": url}
    e = next(iter(d.get("entities", {}).values()), {})
    claims = e.get("claims", {})
    out = {"qid": qid, "source": f"https://www.wikidata.org/wiki/{qid}",
           "label": (e.get("labels", {}).get("en") or {}).get("value"),
           "description": (e.get("descriptions", {}).get("en") or {}).get("value")}
    qrefs = []
    for p, name in PROPS.items():
        vals = [_val(s) for s in claims.get(p, []) if _val(s) is not None]
        if not vals:
            continue
        if name == "inception":
            vals = [str(v).lstrip("+")[:10] for v in vals]
        out[name] = vals
        if name.endswith("_qids") or name.endswith("_qid"):
            qrefs += vals
    lab = labels(sorted(set(qrefs)))
    for k in list(out):
        if k.endswith("_qids") or k.endswith("_qid"):
            out[re.sub(r"_qids?$", "", k)] = [lab.get(q) or q for q in out[k]]
    out["profile_urls"] = (
        [f"https://x.com/{h}" for h in out.get("x_handles", [])]
        + [f"https://www.instagram.com/{h}/" for h in out.get("instagram_handles", [])]
        + [f"https://www.tiktok.com/@{h}" for h in out.get("tiktok_handles", [])]
        + [f"https://www.youtube.com/channel/{c}" for c in out.get("youtube_channel_ids", [])]
        + [f"https://www.facebook.com/{h}" for h in out.get("facebook_ids", [])])
    out["note"] = "Community-edited. Corroborate each handle on the site footer or the profile itself before citing."
    return out


def search(name: str, domain: str | None, limit: int = 5) -> dict:
    url = ("https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&type=item&format=json&limit="
           f"{limit}&search=" + urllib.parse.quote(name))
    d = fetch_json(url, ttl=7 * 24 * 3600)
    if not ok(d):
        return {"_error": d.get("_error"), "source": url,
                "fallback": "WebFetch the same URL, or skip: identity can come from the site footer."}
    cands = [{"qid": r.get("id"), "label": r.get("label"), "description": r.get("description")}
             for r in d.get("search", [])]
    if not cands:
        return {"query": name, "match": None, "candidates": [], "source": url}
    best = None
    if domain:
        for c in cands:
            e = entity(c["qid"])
            if any(domain.lower() in (w or "").lower() for w in e.get("official_website", [])):
                best = e
                break
    if best is None:
        best = entity(cands[0]["qid"])
        best["match_confidence"] = "LOW: first search hit, website not matched" if domain else "MEDIUM: first hit"
    else:
        best["match_confidence"] = "HIGH: official website matches domain"
    return {"query": name, "match": best, "candidates": cands, "source": url}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?")
    ap.add_argument("--qid")
    ap.add_argument("--domain")
    a = ap.parse_args()
    if a.qid:
        emit(entity(a.qid))
    elif a.name:
        emit(search(a.name, a.domain))
    else:
        ap.error("give a name or --qid")


if __name__ == "__main__":
    main()
