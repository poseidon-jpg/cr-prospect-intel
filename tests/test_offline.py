"""Offline tests: parsers run against fixtures shaped like the live pages observed on 2026-10-08.
Run: python3 -m unittest discover -s tests -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "content-rewards-prospect-intel", "scripts")
sys.path.insert(0, SCRIPTS)

import _common  # noqa: E402
import cr_library  # noqa: E402
import social_probe  # noqa: E402
import company_signals  # noqa: E402
import money_math  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures")


def _page(text, status=200, url="x"):
    return {"url": url, "status": status, "final_url": url, "text": text, "fetched_at": "t", "cached": False}


class TestCRLibrary(unittest.TestCase):
    def test_discover_rsc(self):
        obj = {"availableBudgetRaw": 3158.59, "brand": "Michael Sartain's Clipper Army", "budgetSpentLabel": "$$6.8k",
               "budgetSpentRaw": 6841.41, "budgetTotalRaw": 10000, "category": "Personal Brand", "creatorCountRaw": 20,
               "description": "Turn podcasts into clips {with braces} and \"quotes\"", "id": "86842687-ba2b",
               "isVerified": False, "organizationProfileHandle": None,
               "platforms": ["facebook", "instagram", "tiktok", "x", "youtube"], "requiresApplication": False,
               "submissionCountRaw": 40, "title": "Michael Sartain's Clipping Army", "ratePer1kLabel": "$$2", "type": "cpm"}
        obj2 = dict(obj, id="b2", brand="Clip Farm", organizationProfileHandle="clip-farm", title="Boxabl")
        payload = '1:["$","div",null,{"campaigns":[' + json.dumps(obj) + "," + json.dumps(obj2) + "]}]"
        escaped = json.dumps(payload)[1:-1]
        html = f'<html><script>self.__next_f.push([1,"{escaped}"])</script></html>'
        cr_library.fetch = lambda *a, **k: _page(html)
        d = cr_library.discover()
        self.assertTrue(d["structured"])
        self.assertEqual(d["count"], 2)
        self.assertEqual(d["campaigns"][0]["rate_per_1k"], "$2")
        self.assertEqual(d["campaigns"][1]["org_url"], "https://contentrewards.com/c/clip-farm")

    def test_org_page(self):
        html = ("<html><title>Clip Farm | Content Rewards</title><main><div>Back</div><h1>Clip Farm</h1>"
                "<div>235</div><div>Campaigns</div><div>53.6K members</div>"
                "<div>Clip Farm</div><span>·</span><span>1d</span><div>SoFi</div><div>0</div><div>$3/1K</div>"
                "<div>Clip Farm</div><span>·</span><span>4w</span><div>FOMO x ClipFarm (Private Retainer)</div>"
                "<div>0/60</div><div>$500/mo</div></main></html>")
        cr_library.fetch = lambda *a, **k: _page(html)
        d = cr_library.org("clip-farm")
        self.assertEqual(d["campaign_count"], 235)
        self.assertEqual(d["campaigns_visible"][0]["title"], "SoFi")
        self.assertEqual(d["campaigns_visible"][1]["rate"], "$500/mo")

    def test_campaign_page(self):
        lines = ["Back", "Brand", "Title", "TikTok", "Per 1K views", "$1.00", "Min payout", "$10.00", "Max payout",
                 "$100.00", "Budget", "$6,841", "$3,159 remaining", "Brief", "Vertical 9:16 format",
                 "You need dedicated pages tagging @michaelsartain in bio", "Content requirements",
                 "Share audience demographics", "Top clippers", "Clippers in this campaign earn $147.66 on average.",
                 "1 / 20", "4.5M", "views"]
        html = "<html><title>X | Content Rewards</title>" + "".join(f"<div>{x}</div>" for x in lines) + "</html>"
        cr_library.fetch = lambda *a, **k: _page(html)
        d = cr_library.campaign("abc")
        self.assertEqual(d["platform_rates"]["tiktok"]["per_1k"], "$1.00")
        self.assertEqual(d["total_views"], "4.5M")
        self.assertIn("dedicated pages", " ".join(d["brief"]))
        self.assertEqual(d["participants"], "20")


class TestSocial(unittest.TestCase):
    def test_variants(self):
        v = social_probe.gen_variants("Gymshark Ltd", "gymshark")
        self.assertIn("gymsharkclips", v)
        self.assertIn("gymshark.daily", v)
        self.assertTrue(all(len(x) <= 24 for x in v))

    def test_tiktok_embed_parse(self):
        state = {"source": {"data": {"/embed/@gymshark": {
            "isError": False,
            "userInfo": {"uniqueId": "gymshark", "nickname": "Gymshark", "verified": True, "followerCount": 6700000,
                         "followingCount": 47, "heartCount": 141100000, "signature": "winter arc is here.",
                         "privateAccount": False},
            "videoList": [{"id": "1", "desc": "leg day #gymshark", "playCount": 1700000},
                          {"id": "2", "desc": "new drop", "playCount": 30800}]}}}}
        html = f'<script id="__FRONTITY_CONNECT_STATE__" type="application/json">{json.dumps(state)}</script>'
        social_probe.fetch = lambda *a, **k: _page(html)
        d = social_probe.tiktok_profile("gymshark")
        self.assertEqual(d["followers"], 6700000)
        self.assertEqual(d["recent_views_median"], (1700000 + 30800) / 2)

    def test_exists(self):
        social_probe.fetch_json = lambda *a, **k: {"code": 400, "message": "Something went wrong"}
        self.assertFalse(social_probe.tiktok_exists("nope123")["exists"])
        social_probe.fetch_json = lambda *a, **k: {"embed_type": "profile", "author_name": "Gymshark"}
        self.assertTrue(social_probe.tiktok_exists("gymshark")["exists"])

    def test_scoring(self):
        a = {"handle": "gymsharkclips", "bio": "clips of @gymshark daily", "nickname": "GS clips",
             "recent_videos": [{"caption": "gymshark leg day tips you need"}] * 4}
        b = {"handle": "gymshark.daily", "bio": "", "nickname": "daily",
             "recent_videos": [{"caption": "gymshark leg day tips you need"}] * 4}
        s = social_probe.score_candidate(a, "Gymshark", "gymshark", "gymshark.com", [a, b])
        self.assertGreaterEqual(s["score"], 70)
        self.assertEqual(s["label"], "LIKELY AFFILIATED")
        o = social_probe.score_candidate({"handle": "gymshark"}, "Gymshark", "gymshark", None, [])
        self.assertEqual(o["score"], 100)


class TestCompany(unittest.TestCase):
    def test_dns_map(self):
        answers = {"TXT": ['"facebook-domain-verification=abc"', '"bv-domain-verification=x"',
                           '"v=spf1 include:%{ir}.%{v}.%{d}.spf.has.pphosted.com ~all"', '"weird-token=1"'],
                   "MX": ["10 aspmx.l.google.com."]}
        def fake(name, rtype):
            if name.startswith("_dmarc"):
                return ["v=DMARC1; p=reject"]
            return [x.strip('"') for x in answers[rtype]]
        company_signals.doh = fake
        d = company_signals.dns_stack("gymshark.com")
        self.assertIn("Meta Business Manager (runs/ran Meta ads or commerce)", d["stack_from_txt"])
        self.assertIn("Bazaarvoice (reviews / UGC syndication)", d["stack_from_txt"])
        self.assertIn("Proofpoint (enterprise email security)", d["spf_senders"])
        self.assertEqual(d["mail_provider"], ["Google Workspace"])
        self.assertEqual(d["dmarc_policy"], "reject")

    def test_shopify(self):
        prods = {"products": [{"variants": [{"price": "25.00"}], "created_at": "2026-03-27T14:03:50-07:00",
                               "product_type": "Shoes"},
                              {"variants": [{"price": "100.00"}], "created_at": "2026-04-01T00:00:00Z",
                               "product_type": "Shoes"}]}
        company_signals.fetch_json = lambda *a, **k: prods
        d = company_signals.shopify("allbirds.com")
        self.assertEqual(d["products_visible"], 2)
        self.assertEqual(d["list_price_median"], 62.5)
        self.assertEqual(d["earliest_product_created"], "2026-03")


class TestMath(unittest.TestCase):
    def test_scenario(self):
        s = money_math.scenario(10000, 1.0, 0.10, 10, 0.003, 0.02, 50, 1.0)
        self.assertEqual(s["paid_for_views"], 9_000_000)
        self.assertAlmostEqual(s["effective_cpm_all_in"], 1.11, places=2)
        self.assertEqual(s["SCENARIO_business"]["visits"], 27000)


class TestCommon(unittest.TestCase):
    def test_helpers(self):
        self.assertEqual(_common.domain_from_email("Jane@Acme.co.uk"), "acme.co.uk")
        self.assertEqual(_common.label_from_domain("acme.co.uk"), "acme")
        self.assertEqual(_common.brand_core("The Gym-Shark Co."), "gymshark")


if __name__ == "__main__":
    unittest.main()


class TestV2(unittest.TestCase):
    def test_quote_norm_react_markup(self):
        import ledger
        page = 'earn<!-- --> <!-- -->\u2066$13.15\u2069<!-- --> on average. <span>$</span>19,968 &amp; more'
        self.assertIn(ledger._norm("earn $13.15 on average"), ledger._norm(page))
        self.assertIn(ledger._norm("$19,968 & more"), ledger._norm(page))

    def test_tiktok_id_date(self):
        self.assertEqual(social_probe.tiktok_id_date("6718335390845095173"), "2019-07-27")
        self.assertEqual(social_probe.tiktok_id_date("7253970360440229146"), "2023-07-09")
        self.assertIsNone(social_probe.tiktok_id_date("abc"))

    def test_normalize_url(self):
        import ledger
        a = ledger.normalize_url("https://www.Example.com/a//b/?utm_source=x&b=2&a=1#frag")
        b = ledger.normalize_url("http://example.com/a/b?a=1&b=2")
        self.assertEqual(a, b)

    def test_identity_parse(self):
        import identity
        ent = {"entities": {"Q1": {"labels": {"en": {"value": "Gymshark"}}, "descriptions": {"en": {"value": "x"}},
               "claims": {"P2003": [{"mainsnak": {"datavalue": {"value": "gymshark"}}}],
                          "P2397": [{"mainsnak": {"datavalue": {"value": "UCma7hhYJ3bfEhZgw3xl77ww"}}}],
                          "P571": [{"mainsnak": {"datavalue": {"value": {"time": "+2012-00-00T00:00:00Z"}}}}],
                          "P856": [{"mainsnak": {"datavalue": {"value": "https://www.gymshark.com/"}}}]}}}}
        identity.fetch_json = lambda url, **k: ent if "EntityData" in url else {"entities": {}}
        e = identity.entity("Q1")
        self.assertEqual(e["instagram_handles"], ["gymshark"])
        self.assertEqual(e["inception"], ["2012-00-00"])
        self.assertIn("https://www.youtube.com/channel/UCma7hhYJ3bfEhZgw3xl77ww", e["profile_urls"])

    def test_moments(self):
        import subprocess, tempfile
        vtt = "WEBVTT\n\n"
        for i in range(120):
            m, s = divmod(i * 15, 60)
            line = ("Why do most people fail at building a $10 million brand? The truth is they quit too early. "
                    "That's why consistency wins.") if i % 8 == 0 else f"and so yeah we kind of talked about that thing number {i} for a while you know"
            vtt += f"00:{m:02d}:{s:02d}.000 --> 00:{m:02d}:{s+14 if s+14<60 else 59:02d}.000\n{line}\n\n"
        f = tempfile.NamedTemporaryFile("w", suffix=".vtt", delete=False); f.write(vtt); f.close()
        out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "moments.py"), f.name], capture_output=True, text=True)
        d = json.loads(out.stdout)
        self.assertGreater(d["windows_scored"], 0)
        self.assertIn("median(>=50)", d["clippable_moments_per_hour"])
