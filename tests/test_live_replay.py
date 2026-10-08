"""Regression tests on payloads captured live 2026-10-08 (tests/live_capture). Run: python3 -m unittest discover -s tests"""
import os, subprocess, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))

def run(case):
    return subprocess.run([sys.executable, os.path.join(HERE, "live_capture", "replay.py"), case],
                          capture_output=True, text=True, timeout=120).stdout

class TestLiveReplay(unittest.TestCase):
    def test_identity_disambiguates_namesake(self):
        out = run("identity")
        self.assertIn('"picked": "Q106254248"', out)
        self.assertIn("HIGH: official website matches domain", out)
        self.assertIn("Los Angeles", out)
    def test_dns_stack(self):
        out = run("dns")
        for s in ("Klaviyo", "Google Workspace", "Zapier", "quarantine", "board exists, no open roles"):
            self.assertIn(s, out)
    def test_tiktok_dates(self):
        out = run("tiktok")
        self.assertIn('"last_post_date": "2026-09-29"', out)
    def test_constellation_finds_boxabl_network(self):
        out = run("constellation")
        self.assertIn('"likely_affiliated": [\n      "boxablclips"', out)
        self.assertIn("boxablmoments", out)
        self.assertIn('"exists_but_card_unreachable": [\n    "liquiddeathfan"', out)
