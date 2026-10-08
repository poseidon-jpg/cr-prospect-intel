#!/usr/bin/env python3
"""Zero-key company signals from a domain.

Usage:
  python3 company_signals.py acme.com [--company "Acme"] [--ats-slugs acme,acmehq] [--no-news]

Collects (all public, no login, no keys):
  dns      : MX provider, SPF includes, TXT verification tokens -> SaaS stack hints (dns.google)
  rdap     : domain registration date (rdap.org)
  subdomains: certificate-transparency hostnames (crt.sh)  -- slow; skipped with --fast
  shopify  : /products.json catalog size, price band, launch cadence (if the store exposes it)
  ats      : open roles from Greenhouse / Lever / Ashby / Workable boards, flags creator/social/UGC roles
  news     : Google News RSS last 90 days
  wayback  : first archived snapshot (domain age proxy) from the Wayback CDX API

Every section returns data or {"_error": ...}. An error means "not reachable from here",
NOT "the company does not have this". Report it that way.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __import__("os").path.dirname(__file__))
from _common import emit, fetch, fetch_json, label_from_domain, median, ok, pct  # noqa: E402

# Verified token prefixes (sources: domainsproject.org 2026 TXT census, netspi, live lookups 2026-10-08).
TXT_TOKENS = [
    ("google-site-verification=", "Google (Search Console/Workspace)"),
    ("ms=ms", "Microsoft 365"),
    ("facebook-domain-verification=", "Meta Business Manager (runs/ran Meta ads or commerce)"),
    ("atlassian-domain-verification=", "Atlassian (Jira/Confluence)"),
    ("stripe-verification=", "Stripe"),
    ("docusign", "DocuSign"),
    ("brevo-code:", "Brevo (email marketing)"),
    ("zoho-verification=", "Zoho"),
    ("apple-domain-verification=", "Apple (Business Connect / Apple Pay)"),
    ("openai-domain-verification=", "OpenAI (ChatGPT Enterprise/Team)"),
    ("anthropic-domain-verification", "Anthropic (Claude for Work)"),
    ("adobe-idp-site-verification=", "Adobe enterprise"),
    ("adobe-sign-verification=", "Adobe Sign"),
    ("pardot", "Salesforce Pardot / Marketing Cloud"),
    ("dropbox-domain-verification=", "Dropbox"),
    ("firebase=", "Firebase"),
    ("amazonses:", "Amazon SES"),
    ("bv-domain-verification=", "Bazaarvoice (reviews / UGC syndication)"),
    ("storyteq-domain-verification", "Storyteq (creative automation, ad variants at scale)"),
    ("mixpanel-domain-verify=", "Mixpanel (product analytics)"),
    ("figma-domain-verification=", "Figma"),
    ("wrike-verification=", "Wrike"),
    ("onetrust-domain-verification=", "OneTrust (consent/privacy)"),
    ("h1-domain-verification=", "HackerOne"),
    ("zoom_verify_", "Zoom"),
    ("jamf-site-verification=", "Jamf (Apple device mgmt)"),
    ("globalsign-domain-verification=", "GlobalSign (certificates; not a stack signal)"),
    ("_globalsign-domain-verification=", "GlobalSign (certificates; not a stack signal)"),
    ("access-domain-verification=", "Access-management vendor (unmapped)"),
    ("miro-verification=", "Miro"),
    ("slack-domain-verification=", "Slack"),
    ("notion", "Notion"),
    ("canva-site-verification=", "Canva"),
    ("tiktok-developers-site-verification=", "TikTok for Developers (TikTok app/API integration)"),
    ("pinterest-site-verification=", "Pinterest (business account / ads)"),
    ("yandex-verification:", "Yandex Webmaster"),
    ("hubspot", "HubSpot (unconfirmed token form)"),
    ("klaviyo-site-verification=", "Klaviyo (email/SMS marketing; confirmed token form)"),
    ("zapier-domain-verification", "Zapier (automation)"),
    ("mailerlite-domain-verification=", "MailerLite (email marketing)"),
    ("airtable-verification=", "Airtable"),
    ("klaviyo", "Klaviyo"),
]
NOISE = ("afternic-verification", "dan-ownership-verification")
SPF_INCLUDES = [
    ("_spf.google.com", "Google Workspace sends mail"),
    ("spf.protection.outlook.com", "Microsoft 365 sends mail"),
    ("sendgrid.net", "SendGrid"),
    ("mailgun.org", "Mailgun"),
    ("spf.mtasv.net", "Postmark"),
    ("amazonses.com", "Amazon SES"),
    ("_spf.salesforce.com", "Salesforce"),
    ("mg-spf.greenhouse.io", "Greenhouse (recruiting)"),
    ("mail.zendesk.com", "Zendesk"),
    ("emailus.freshservice.com", "Freshservice"),
    ("pphosted.com", "Proofpoint (enterprise email security)"),
    ("servers.mcsv.net", "Mailchimp"),
    ("_spf.klaviyo.com", "Klaviyo"),
    ("klaviyomail", "Klaviyo"),
    ("shopify", "Shopify (transactional mail)"),
    ("hubspotemail.net", "HubSpot"),
    ("_spf.intercom.io", "Intercom"),
]
MX_PROVIDERS = [
    ("google.com", "Google Workspace"), ("googlemail.com", "Google Workspace"),
    ("outlook.com", "Microsoft 365"), ("pphosted.com", "Proofpoint (gateway)"),
    ("mimecast", "Mimecast (gateway)"), ("zoho", "Zoho Mail"), ("secureserver.net", "GoDaddy mail"),
]
BUYING_SIGNAL = re.compile(
    r"creator|influencer|\bugc\b|tiktok|social|affiliate|partnership|content|community|clip|"
    r"short[- ]form|video|podcast|growth|brand marketing|paid social|ambassador|talent", re.I)


def doh(name: str, rtype: str) -> list[str]:
    q = urllib.parse.urlencode({"name": name, "type": rtype})
    d = fetch_json(f"https://dns.google/resolve?{q}", ttl=24 * 3600)
    if not ok(d):
        d = fetch_json(f"https://cloudflare-dns.com/dns-query?{q}",
                       headers={"accept": "application/dns-json"}, ttl=24 * 3600)
    if not ok(d):
        raise RuntimeError(d.get("_error"))
    return [a.get("data", "").strip('"') for a in d.get("Answer", []) or [] if isinstance(a, dict)]


def dns_stack(domain: str) -> dict:
    try:
        txt = doh(domain, "TXT")
        mx = doh(domain, "MX")
        dmarc = doh(f"_dmarc.{domain}", "TXT")
    except Exception as e:
        return {"_error": str(e), "source": "dns.google / cloudflare-dns.com"}
    hits, unmapped = {}, []
    for t in txt:
        low = t.lower()
        if low.startswith(NOISE) or low.startswith("v=spf1"):
            continue
        for prefix, vendor in TXT_TOKENS:
            if low.startswith(prefix) or (prefix in ("pardot", "notion", "hubspot", "klaviyo", "docusign") and prefix in low):
                hits.setdefault(vendor, []).append(t[:60])
                break
        else:
            if "=" in t or "verif" in low:
                unmapped.append(t[:80])
    spf = [t for t in txt if t.lower().startswith("v=spf1")]
    spf_vendors = sorted({v for rec in spf for inc, v in SPF_INCLUDES if inc in rec.lower()})
    mail = sorted({v for m in mx for k, v in MX_PROVIDERS if k in m.lower()})
    policy = None
    for d in dmarc:
        m = re.search(r"p=(\w+)", d)
        if m:
            policy = m.group(1)
    return {
        "source": f"https://dns.google/resolve?name={domain}&type=TXT",
        "mail_provider": mail or None,
        "mx": mx,
        "stack_from_txt": hits,
        "spf_senders": spf_vendors,
        "unmapped_tokens": unmapped[:15],
        "dmarc_policy": policy,
        "note": "TXT tokens can be stale (old trials). Treat as 'has used / verified', not 'pays for today'.",
    }


def rdap(domain: str) -> dict:
    d = fetch_json(f"https://rdap.org/domain/{domain}", ttl=7 * 24 * 3600)
    if not ok(d):
        return d
    ev = {e.get("eventAction"): e.get("eventDate") for e in d.get("events", []) if isinstance(e, dict)}
    return {"source": f"https://rdap.org/domain/{domain}", "registered": ev.get("registration"),
            "expires": ev.get("expiration"), "last_changed": ev.get("last changed")}


def crtsh(domain: str) -> dict:
    d = fetch_json(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=45, ttl=7 * 24 * 3600)
    if not isinstance(d, list):
        return d if isinstance(d, dict) else {"_error": "unexpected"}
    names = set()
    for row in d:
        for n in str(row.get("name_value", "")).split("\n"):
            n = n.strip().lower()
            if n.endswith(domain) and "*" not in n:
                names.add(n)
    interesting = sorted(n for n in names if re.match(
        r"^(shop|store|app|status|help|support|go|link|links|careers|jobs|creators?|ambassadors?|"
        r"affiliates?|partners?|ugc|community|rewards|loyalty|api|admin|portal|blog|press|investors?)\.", n))
    return {"source": f"https://crt.sh/?q=%25.{domain}", "count": len(names),
            "interesting": interesting[:40], "sample": sorted(names)[:40]}


def shopify(domain: str) -> dict:
    products, page = [], 1
    while page <= 8:  # cap 2,000 products, ~8 polite requests
        d = fetch_json(f"https://{domain}/products.json?limit=250&page={page}", browser_ua=True)
        if not ok(d) or not isinstance(d, dict) or "products" not in d:
            if page == 1:
                return {"is_shopify_public_json": False,
                        "detail": (d.get("_error") if isinstance(d, dict) else None) or "no products.json",
                        "note": "Many headless/Plus stores block this. Not proof the brand isn't on Shopify."}
            break
        batch = d["products"]
        products += batch
        if len(batch) < 250:
            break
        page += 1
    prices, created = [], []
    types: dict[str, int] = {}
    for p in products:
        for v in (p.get("variants") or [])[:1]:
            try:
                prices.append(float(v.get("price")))
            except Exception:
                pass
        if p.get("created_at"):
            created.append(p["created_at"][:7])
        t = (p.get("product_type") or "").strip()
        if t:
            types[t] = types.get(t, 0) + 1
    by_month: dict[str, int] = {}
    for c in created:
        by_month[c] = by_month.get(c, 0) + 1
    recent = dict(sorted(by_month.items())[-12:])
    return {
        "source": f"https://{domain}/products.json",
        "is_shopify_public_json": True,
        "products_visible": len(products),
        "capped": len(products) >= 2000,
        "list_price_median": median(prices),
        "list_price_p25": pct(prices, 0.25),
        "list_price_p75": pct(prices, 0.75),
        "earliest_product_created": min(created) if created else None,
        "new_products_by_month_last12": recent,
        "top_product_types": sorted(types.items(), key=lambda x: -x[1])[:8],
        "caveat": "List prices of first variant, not AOV. Currency = store default for this IP.",
    }


def ats(slugs: list[str]) -> dict:
    found = {}
    for s in slugs:
        probes = {
            "greenhouse": (f"https://boards-api.greenhouse.io/v1/boards/{s}/jobs?content=true",
                           lambda d: [(j.get("title"), (j.get("location") or {}).get("name"), j.get("absolute_url"),
                                       ",".join(x.get("name", "") for x in j.get("departments", []) or []))
                                      for j in d.get("jobs", [])]),
            "lever": (f"https://api.lever.co/v0/postings/{s}?mode=json",
                      lambda d: [(j.get("text"), (j.get("categories") or {}).get("location"), j.get("hostedUrl"),
                                  (j.get("categories") or {}).get("team")) for j in d] if isinstance(d, list) else []),
            "ashby": (f"https://api.ashbyhq.com/posting-api/job-board/{s}?includeCompensation=true",
                      lambda d: [(j.get("title"), j.get("location"), j.get("jobUrl"), j.get("department"))
                                 for j in d.get("jobs", [])]),
            "workable": (f"https://apply.workable.com/api/v1/widget/accounts/{s}?details=false",
                         lambda d: [(j.get("title"), j.get("city"), j.get("url"), j.get("department"))
                                    for j in d.get("jobs", [])]),
        }
        for ats_name, (url, parse) in probes.items():
            d = fetch_json(url, ttl=12 * 3600)
            if not ok(d):
                continue
            try:
                rows = parse(d)
            except Exception:
                continue
            if not rows:
                found[f"{ats_name}:{s}"] = {"source": url, "open_roles": 0,
                                            "note": "board exists, no open roles right now"}
                continue
            sig = [r for r in rows if BUYING_SIGNAL.search(f"{r[0]} {r[3] or ''}")]
            found[f"{ats_name}:{s}"] = {
                "source": url, "open_roles": len(rows),
                "buying_signal_roles": [{"title": r[0], "location": r[1], "url": r[2], "dept": r[3]} for r in sig[:15]],
                "all_titles_sample": [r[0] for r in rows[:25]],
            }
    return found or {"result": "no public board found for slugs " + ",".join(slugs),
                     "note": "Company may use Workday/iCIMS/BambooHR/LinkedIn-only. Check careers page."}


def news(company: str) -> dict:
    q = urllib.parse.quote(f'"{company}" when:90d')
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    r = fetch(url, ttl=3 * 3600)
    if not ok(r):
        return r
    try:
        root = ET.fromstring(r["text"])
    except Exception as e:
        return {"_error": f"parse: {e}", "url": url}
    items = [{"title": i.findtext("title"), "date": i.findtext("pubDate"), "link": i.findtext("link"),
              "source": (i.find("source").text if i.find("source") is not None else None)}
             for i in root.iter("item")]
    return {"source": url, "count": len(items), "items": items[:20],
            "note": "Google News RSS is undocumented; links are Google redirect URLs. Open the original before citing."}


def wayback_first(domain: str) -> dict:
    url = (f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&fl=timestamp,statuscode"
           f"&filter=statuscode:200&limit=1")
    d = fetch_json(url, timeout=30, ttl=30 * 24 * 3600)
    if isinstance(d, list) and len(d) > 1:
        ts = d[1][0]
        return {"source": url, "first_snapshot": f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}",
                "note": "Age of the DOMAIN, not the brand (domains are often bought used). Prefer Shopify "
                        "earliest_product_created or Wikidata inception for brand age."}
    return d if isinstance(d, dict) else {"first_snapshot": None}


def tech(domain: str) -> dict:
    """Optional BuiltWith-class tech detection via projectdiscovery httpx (-td, wappalyzergo fingerprints,
    refreshed weekly upstream, MIT). Install: https://github.com/projectdiscovery/httpx/releases.
    Note: the Python 'httpx' package also installs an 'httpx' command, so we check which one it is."""
    import shutil
    import subprocess
    exe = shutil.which("httpx")
    if not exe:
        return {"skipped": "projectdiscovery httpx not installed (optional)",
                "manual": f"View source of https://{domain} and look for cdn.shopify.com, static.klaviyo.com, "
                          "cdn.attn.tv, analytics.tiktok.com (TikTok pixel), connect.facebook.net (Meta pixel)."}
    try:
        v = subprocess.run([exe, "-version"], capture_output=True, text=True, timeout=15)
        if "projectdiscovery" not in (v.stdout + v.stderr).lower():
            return {"skipped": "'httpx' on PATH is the Python package, not projectdiscovery httpx"}
        r = subprocess.run([exe, "-u", f"https://{domain}", "-td", "-json", "-silent", "-timeout", "15",
                            "-no-color"], capture_output=True, text=True, timeout=60)
        import json as _j
        rows = [_j.loads(x) for x in r.stdout.splitlines() if x.strip().startswith("{")]
        techs = sorted({t for row in rows for t in (row.get("tech") or row.get("technologies") or [])})
        return {"source": f"httpx -td https://{domain}", "detected": techs,
                "note": "Detected from headers/HTML/scripts on one public page fetch. 'Detected', not 'pays for'."}
    except Exception as e:
        return {"_error": f"{type(e).__name__}: {e}"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("domain")
    ap.add_argument("--company", default=None)
    ap.add_argument("--ats-slugs", default=None, help="comma list; default derived from domain")
    ap.add_argument("--fast", action="store_true", help="skip crt.sh and wayback (slow)")
    ap.add_argument("--no-news", action="store_true")
    a = ap.parse_args()
    domain = a.domain.lower().removeprefix("https://").removeprefix("http://").removeprefix("www.").strip("/")
    label = label_from_domain(domain)
    company = a.company or label
    slugs = a.ats_slugs.split(",") if a.ats_slugs else sorted({label, f"{label}hq", f"get{label}", f"try{label}",
                                                               re.sub(r'[^a-z0-9]', '', company.lower())})
    jobs = {"dns": (dns_stack, domain), "rdap": (rdap, domain), "shopify": (shopify, domain), "ats": (ats, slugs),
            "tech": (tech, domain)}
    if not a.no_news:
        jobs["news"] = (news, company)
    if not a.fast:
        jobs["subdomains"] = (crtsh, domain)
        jobs["wayback"] = (wayback_first, domain)
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {k: ex.submit(f, arg) for k, (f, arg) in jobs.items()}
        out = {"domain": domain, "company": company}
        for k, fu in futs.items():
            try:
                out[k] = fu.result()
            except Exception as e:
                out[k] = {"_error": f"{type(e).__name__}: {e}"}
    emit(out)


if __name__ == "__main__":
    main()
