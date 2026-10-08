#!/usr/bin/env python3
"""Evidence ledger: every claim in the dossier is a row with a source and a quoted span.

Usage:
  python3 ledger.py init  RUN_DIR
  python3 ledger.py add   RUN_DIR --claim "..." --url URL --quote "exact text" [--event-date 2026-09-01]
                          [--type primary|secondary|aggregator|marketing|derived] [--confidence HIGH|MEDIUM|LOW|INFERENCE]
                          [--section company]
  python3 ledger.py verify RUN_DIR [--refetch]   literal quote check against the fetched page text
  python3 ledger.py sources RUN_DIR              numbered source list generated from the ledger (never by the model)

Rules this enforces (borrowed from Anthropic's account-research skill, open_deep_research, dzhng/deep-research):
  - a quote must appear verbatim (whitespace/case-normalised) in the source text, or the claim is downgraded
  - INFERENCE rows need no quote but must say so in the report
  - "derived" rows (math) must name their inputs in --quote, e.g. "spent $6,841 / views 4.5M"
"""
from __future__ import annotations

import argparse
import json
import os
import html
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from _common import fetch, ok  # noqa: E402


TRACKING = re.compile(r"^(utm_\w+|fbclid|gclid|mc_cid|mc_eid|igshid|si|ref|ref_src|_hsenc|_hsmi|sessionid|sid|"
                      r"phpsessid|jsessionid|spm|share_id)$", re.I)


def normalize_url(u: str) -> str:
    """Dedup key for sources (after jina-ai/node-DeepResearch normalizeUrl): lowercase host, drop www,
    default ports, fragments, tracking/session params, trailing slash; sort the remaining query params."""
    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
    if not u:
        return u
    p = urlsplit(u.strip())
    host = (p.hostname or "").lower().removeprefix("www.")
    if p.port and p.port not in (80, 443):
        host += f":{p.port}"
    q = sorted((k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not TRACKING.match(k))
    path = re.sub(r"/{2,}", "/", p.path).rstrip("/") or "/"
    return urlunsplit(("https", host, path, urlencode(q), ""))


def _norm(s: str) -> str:
    s = re.sub(r"<!--.*?-->", "", s or "", flags=re.S)  # React inserts <!-- --> between "$" and numbers
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"[\u200b-\u200f\u2066-\u2069\u202a-\u202e\ufeff]", "", s)  # zero-width / bidi marks
    s = re.sub(r"([$€£])\s+(?=\d)", r"\1", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def _path(run: str) -> Path:
    return Path(run) / "ledger.jsonl"


def init(run: str) -> None:
    Path(run).mkdir(parents=True, exist_ok=True)
    _path(run).touch()
    print(json.dumps({"ok": True, "ledger": str(_path(run))}))


def add(run: str, a) -> None:
    rows = _load(run)
    row = {"id": f"C{len(rows) + 1:03d}", "section": a.section, "claim": a.claim, "url": a.url,
           "quote": a.quote, "event_date": a.event_date, "source_type": a.type,
           "confidence": a.confidence, "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "verified": None}
    with _path(run).open("a") as f:
        f.write(json.dumps(row) + "\n")
    print(json.dumps(row))


def _load(run: str) -> list[dict]:
    p = _path(run)
    if not p.exists():
        sys.exit(f"no ledger at {p}; run init first")
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def verify(run: str, refetch: bool) -> None:
    rows = _load(run)
    cache: dict[str, str] = {}
    for r in rows:
        if r["confidence"] == "INFERENCE" or r["source_type"] == "derived":
            r["verified"] = "n/a"
            continue
        if not r.get("quote") or not r.get("url"):
            r["verified"] = "FAIL: missing quote or url"
            continue
        if r["url"] not in cache:
            res = fetch(r["url"], browser_ua=True, ttl=0 if refetch else 24 * 3600)
            cache[r["url"]] = res.get("text", "") if ok(res) else ""
        text = cache[r["url"]]
        if not text:
            r["verified"] = "UNCHECKED: source not reachable from here (verify manually or via WebFetch)"
        elif _norm(r["quote"]) in _norm(text):
            r["verified"] = "PASS"
        else:
            r["verified"] = "FAIL: quote not found on page"
    _path(run).write_text("".join(json.dumps(r) + "\n" for r in rows))
    # Verdict rules (after LearningCircuit/local-deep-research grade_all_claims): a claim that is not
    # INFERENCE/derived and lacks a passing quote can never be "supported".
    for r in rows:
        v = str(r["verified"])
        if v == "n/a":
            r["verdict"] = "inference" if r["confidence"] == "INFERENCE" else "derived"
        elif v == "PASS":
            r["verdict"] = r.get("verdict_hint") or "supported"
        elif v.startswith("UNCHECKED"):
            r["verdict"] = "unverified"
        else:
            r["verdict"] = "unverified"
    _path(run).write_text("".join(json.dumps(r) + "\n" for r in rows))
    summary = {}
    for r in rows:
        k = r["verified"].split(":")[0]
        summary[k] = summary.get(k, 0) + 1
    print(json.dumps({"summary": summary,
                      "fails": [{k: r[k] for k in ("id", "claim", "url", "verified")}
                                for r in rows if str(r["verified"]).startswith("FAIL")]}, indent=2))


def sources(run: str) -> None:
    """Numbered source list built from the ledger (deduped by normalized URL). The model never writes this."""
    rows = _load(run)
    order: list[str] = []
    first: dict[str, str] = {}
    for r in rows:
        if r.get("url"):
            k = normalize_url(r["url"])
            if k not in first:
                first[k] = r["url"]
                order.append(k)
    for i, k in enumerate(order, 1):
        ids = [r["id"] for r in rows if r.get("url") and normalize_url(r["url"]) == k]
        unver = [r["id"] for r in rows if r.get("url") and normalize_url(r["url"]) == k
                 and r.get("verdict") == "unverified"]
        flag = f"  UNVERIFIED: {', '.join(unver)}" if unver else ""
        print(f"[S{i}] {first[k]}  (claims: {', '.join(ids)}){flag}")


def lint(run: str, report: str) -> None:
    """Citation contract (after miurla/morphic): the report may only cite [S<n>] or [C<nnn>] ids that exist.
    Flags unknown ids, raw URLs typed into prose, and claims marked unverified that are cited as fact."""
    rows = _load(run)
    text = Path(report).read_text(encoding="utf-8")
    cids = {r["id"] for r in rows}
    n_sources = len({normalize_url(r["url"]) for r in rows if r.get("url")})
    bad = []
    for m in re.finditer(r"\[(S(\d+)|C\d{3})\]", text):
        if m.group(2) and not (1 <= int(m.group(2)) <= n_sources):
            bad.append(m.group(0))
        elif not m.group(2) and m.group(1) not in cids:
            bad.append(m.group(0))
    unverified_cited = sorted({r["id"] for r in rows if r.get("verdict") == "unverified" and f"[{r['id']}]" in text})
    body = text.split("## 23.")[0] if "## 23." in text else text
    raw_urls = re.findall(r"(?<!\()https?://\S+", body)
    print(json.dumps({"unknown_citations": sorted(set(bad)), "unverified_claims_cited": unverified_cited,
                      "raw_urls_in_body": raw_urls[:20],
                      "pass": not bad and not unverified_cited}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("run")
    p = sub.add_parser("add"); p.add_argument("run")
    p.add_argument("--claim", required=True); p.add_argument("--url", default=None); p.add_argument("--quote", default=None)
    p.add_argument("--event-date", default=None); p.add_argument("--section", default=None)
    p.add_argument("--type", default="secondary", choices=["primary", "secondary", "aggregator", "marketing", "derived"])
    p.add_argument("--confidence", default="MEDIUM", choices=["HIGH", "MEDIUM", "LOW", "INFERENCE"])
    p = sub.add_parser("verify"); p.add_argument("run"); p.add_argument("--refetch", action="store_true")
    p = sub.add_parser("sources"); p.add_argument("run")
    p = sub.add_parser("lint"); p.add_argument("run"); p.add_argument("report")
    a = ap.parse_args()
    {"init": lambda: init(a.run), "add": lambda: add(a.run, a), "verify": lambda: verify(a.run, a.refetch),
     "sources": lambda: sources(a.run), "lint": lambda: lint(a.run, a.report)}[a.cmd]()


if __name__ == "__main__":
    main()
