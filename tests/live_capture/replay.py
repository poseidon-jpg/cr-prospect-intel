#!/usr/bin/env python3
"""Run the REAL skill scripts against payloads captured live on 2026-10-08 (see captured_2026-10-08.py).
Only the network layer is replayed; every parser, scorer and rule is the shipped code."""
import importlib.util, json, os, re, sys, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "..", "skills", "content-rewards-prospect-intel", "scripts")
sys.path.insert(0, SCRIPTS)
spec = importlib.util.spec_from_file_location("cap", os.path.join(HERE, "captured_2026-10-08.py"))
cap = importlib.util.module_from_spec(spec); spec.loader.exec_module(cap)
import _common, identity, company_signals, social_probe, cr_library, money_math  # noqa

LOG = []

def _resp(body, url):
    return {"url": url, "status": 200, "final_url": url, "text": body if isinstance(body, str) else json.dumps(body), "fetched_at": "2026-10-08", "cached": False}

def fake_fetch(url, **kw):
    LOG.append(url)
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    if "dns.google" in url:
        name, t = q["name"][0], q["type"][0]
        if name == "liquiddeath.com" and t == "TXT": return _resp(cap.DNS_TXT_LIQUIDDEATH, url)
        if name == "liquiddeath.com" and t == "MX": return _resp(cap.DNS_MX_LIQUIDDEATH, url)
        if name == "_dmarc.liquiddeath.com": return _resp(cap.DNS_DMARC_LIQUIDDEATH, url)
    if "wbsearchentities" in url and "Liquid" in url: return _resp(cap.WD_SEARCH_LIQUIDDEATH, url)
    if "EntityData/Q106254248" in url: return _resp(cap.WD_ENTITY_Q106254248, url)
    if "EntityData/Q134585034" in url: return _resp(cap.WD_ENTITY_Q134585034, url)
    if "wbgetentities" in url: return _resp(cap.WD_LABELS, url)
    if "boards-api.greenhouse.io/v1/boards/liquiddeath/" in url: return _resp(cap.GREENHOUSE_LIQUIDDEATH, url)
    if "tiktok.com/oembed" in url:
        h = re.search(r"@([^/&]+)", urllib.parse.unquote(url)).group(1)
        if h in cap.OEMBED_EXISTS: return _resp({"embed_type": "profile", "author_name": cap.OEMBED_EXISTS[h]}, url)
        if h in cap.OEMBED_MISSING: return {"_error": "HTTP 400", "status": 400, "url": url, "text": '{"code":400}'}
    if "tiktok.com/embed/@" in url:
        h = url.rsplit("@", 1)[1]
        if h in cap.EMBED:
            u, vids, caps = cap.EMBED[h]
            vl = [{"id": i, "playCount": p, "desc": caps[k] if k < len(caps) else ""} for k, (i, p) in enumerate(vids)]
            state = {"source": {"data": {f"/embed/@{h}": {"isError": False, "userInfo": dict(u, uniqueId=h), "videoList": vl}}}}
            return _resp(f'<script id="__FRONTITY_CONNECT_STATE__" type="application/json">{json.dumps(state)}</script>', url)
    return {"_error": "not captured in this replay (would be a live call on a laptop)", "url": url}

def fake_fetch_json(url, **kw):
    r = fake_fetch(url, **kw)
    if "_error" in r:
        try: return json.loads(r.get("text") or "x")
        except Exception: return r
    return json.loads(r["text"])

for m in (_common, identity, company_signals, social_probe, cr_library):
    for n, f in (("fetch", fake_fetch), ("fetch_json", fake_fetch_json)):
        if hasattr(m, n): setattr(m, n, f)
social_probe.time.sleep = lambda s: None

def show(title, obj):
    print(f"\n===== {title} =====")
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str)[:6000])

if __name__ == "__main__":
    case = sys.argv[1] if len(sys.argv) > 1 else "all"
    if case in ("all", "identity"):
        r = identity.search("Liquid Death", "liquiddeath.com")
        show("1. identity.py 'Liquid Death' --domain liquiddeath.com (namesake: a 1953 novel)",
             {"picked": r["match"]["qid"], "label": r["match"]["label"], "match_confidence": r["match"]["match_confidence"],
              "official_website": r["match"].get("official_website"), "profile_urls": r["match"]["profile_urls"],
              "headquarters": r["match"].get("headquarters"), "candidates": r["candidates"]})
    if case in ("all", "dns"):
        show("2. company_signals.dns_stack('liquiddeath.com')", company_signals.dns_stack("liquiddeath.com"))
        show("2b. company_signals.ats(['liquiddeath'])", company_signals.ats(["liquiddeath"]))
    if case in ("all", "tiktok"):
        p = social_probe.tiktok_profile("liquiddeath")
        show("3. social_probe.py tiktok liquiddeath", {k: p[k] for k in ("followers","total_likes","verified","bio","last_post_date","posts_in_sample_last_30d","median_views_last_30d","recent_views_median","approx_posts_per_week","sample_span_days")} | {"videos": [(v["date"], v["views"], v["caption"][:40]) for v in p["recent_videos"]]})
    if case in ("all", "constellation"):
        show("4. social_probe.py constellation 'Boxabl' --handle boxabl --domain boxabl.com --max 20",
             social_probe.constellation("Boxabl", "boxabl", "boxabl.com", [], 20))
        show("4b. constellation 'Liquid Death' --handle liquiddeath (contrast)",
             social_probe.constellation("Liquid Death", "liquiddeath", "liquiddeath.com",
                                        cap.OEMBED_MISSING[10:] + ["liquiddeathfan"], 0))
    if case in ("all", "edge"):
        show("5. edge cases", {
            "free-mail email -> domain": _common.domain_from_email("jane.doe@gmail.com"),
            "is free mail": _common.domain_from_email("jane.doe@gmail.com") in _common.FREE_MAIL,
            "nonexistent handle": social_probe.tiktok_exists("boxablpodcast"),
            "uncaptured endpoint (simulated block)": company_signals.shopify("liquiddeath.com"),
            "CR match for 'boxabl' (existing-customer detection)": [ (m["title"], m["organizer"], m["rate_per_1k"]) for m in cr_library.match(["boxabl","housing"], None, 3)["matches"]],
        })
    print(f"\n[replay served {len(LOG)} requests]")
