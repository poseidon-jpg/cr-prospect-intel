# Stress test: 2026-10-08

**What was proven:** the shipped scripts (parsers, scoring, rules) ran on **live payloads captured the same day
through a real browser**. The build sandbox has no open internet, so the network layer is replayed from those
captures (`tests/live_capture/`). Everything after the HTTP response is the real code. Reproduce it with
`python3 tests/live_capture/replay.py all`. On a laptop the same scripts make these calls themselves.

**Prospects:**
- Liquid Death: DTC beverage, culture brand, has a namesake
- Boxabl: already a Content Rewards customer through Clip Farm
- Edge cases: free-mail address, nonexistent handle, blocked endpoint, job board with zero roles

## 1. Identity: Liquid Death has a namesake (a 1953 novel)
`identity.py "Liquid Death" --domain liquiddeath.com` → it picked **Q106254248** with match confidence "HIGH: official
website matches domain" and rejected the novel. It returned the HQ (Los Angeles) and every official handle:
x.com/LiquidDeath, instagram.com/liquiddeath, tiktok.com/@liquiddeath, YouTube UCpRMG5MU1RurWtdiRFtPyvQ and
facebook.com/DrinkLiquidDeath. Two keyless calls, no API key.

## 2. Company stack from DNS: liquiddeath.com
- **Mail and security:** Google Workspace mail, DMARC set to quarantine.
- **Marketing stack:** Klaviyo (5 verification tokens, so email/SMS is heavy), MailerLite, Zapier and Airtable.
- **Other software:** Slack, Atlassian, Microsoft 365, Dropbox, Apple, OpenAI and Anthropic (both AI vendors
  verified).
- **Jobs:** the Greenhouse board exists with 0 open roles. The skill reports that, not "no board".

## 3. TikTok without a key: @liquiddeath
- 7.3M followers and 23.7M likes, verified.
- **Every video dated from its ID:** last post 2026-09-29, about 0.8 posts a week over a 91-day sample.
- Views swing between 8K and 4.6M. The hits are the "We want your pee", Liquid Death Energy, Cinnamon Roll Iced
  Tea and MrBeast/Feastables posts.
- Read: huge owned reach, low cadence and a hit-or-miss distribution. That's the opening for distributed clipping.

## 4. Account constellation: Boxabl vs Liquid Death
`constellation "Boxabl" --handle boxabl --domain boxabl.com --max 20` → **10 of 20 variant handles exist.**

| Account | Score | Why |
|---|---|---|
| boxablclips | 75 LIKELY | every caption is "Boxabl Is Taking Over The Housing Industry!"; bio says "Invest Now!" |
| boxablnews | 75 LIKELY | **identical caption template** to boxabldaily (Jaccard 1.00), all posted in the same days of 2023 |
| boxablmoments | 70 LIKELY | bio "best moments from the company @BOXABL"; posts from 2026, consistent with the live Clip Farm campaign |
| boxabldaily | 60 POSSIBLE | same template as boxablnews |
| boxablclip | 30 NAME ONLY | empty account |

Liquid Death, run as a contrast, has 0 affiliated accounts across 16 variants. One fan page exists.

**Why it matters for a sales call:**
- Boxabl's official bio now says it trades on Nasdaq ($BXBL). That's the why-now.
- Boxabl already ran CR campaigns: Boxabl Official Clipping (Clip Farm, 834 creators, $0.50/1K) and
  Boxabl Phase 2.
- **Boxabl call:** an expansion conversation. They have a past templated-account network, so pitch per-clip
  approval and caption-variation rules, plus investor-narrative clipping after the listing.
- **Liquid Death call:** greenfield. They have a massive owned audience, almost nothing distributed, and a
  hit-driven feed.

## 5. Edge cases
| Case | Result |
|---|---|
| jane.doe@gmail.com | flagged free-mail, so no company inferred |
| @boxablpodcast | does not exist (oEmbed 400), reported as such |
| Blocked endpoint | "not reachable", never "not on Shopify" |
| Namesake entity | disambiguated by domain |

## Bugs the stress test found, all fixed in v0.2.2
1. HQ and other single-item Wikidata fields weren't resolved to names (a `_qid` vs `_qids` mismatch). Fixed; it now says "Los Angeles".
2. Klaviyo's real token form `klaviyo-site-verification=` was labelled "unconfirmed". Now confirmed, and Zapier, MailerLite and Airtable were added.
3. A Greenhouse board with 0 roles was reported as "no public board". Now it reads "board exists, no open roles".
4. The handle-variant order spent a 40-check budget on separator permutations. Re-ordered so the most likely forms go first.
5. Accounts that exist but whose card couldn't be read were silently dropped. Now listed as `exists_but_card_unreachable`.
6. Firing 150 TikTok requests in parallel got the IP blocked (earlier run). The script now throttles to about 1.2s per call and stops on a 403.

## Not proven here
- These run on a laptop and were not live-tested end to end: crt.sh, RDAP, Shopify JSON, Google News, iTunes,
  YouTube RSS and the yt-dlp history.
- `moments.py` has only been tested on synthetic transcripts.
- Test plan: `doctor.py`, then one run per prospect above.
