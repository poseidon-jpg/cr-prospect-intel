# Content Rewards Prospect Intel

An agent skill that turns **a name and a work email** into a cited pre-call dossier for a Content Rewards
sales call. It answers: who is this prospect, how does their brand distribute organic content today, which
accounts already carry their name, how much clippable content they're sitting on, which live Content Rewards
campaigns and agencies are the closest match, and what to say in the first five minutes.

It works with **zero API keys**. Free keys add depth, but nothing breaks without them.

```
/prospect Jane Doe, jane@brand.com, Brand
```
or just tell your agent: *"prep me for my call with Jane Doe (jane@brand.com) tomorrow."*

You get `prospect-runs/<company>-<date>/dossier.md` (23 sections, every claim sourced) and `cheat-sheet.md`
(one screen you can read two minutes before the call).

**Real runs:** [Oura cheat sheet](examples/oura-2026-10-08/cheat-sheet.md) (cold prospect: IPO pulled Sep 28, CEO podcasts nobody clips, zero CR history) ·
[Boxabl cheat sheet](examples/boxabl-2026-10-08/cheat-sheet.md) ·
[Boxabl dossier](examples/boxabl-2026-10-08/dossier.md) (found that Boxabl is already a CR customer via Clip Farm,
~34M views on $20K, and that clip pages are telling viewers to "Invest Now!" in a newly public stock) ·
[Gymshark dossier](examples/gymshark-2026-10-08/dossier.md). New to this? Start with
[HOW-A-REP-USES-IT.md](HOW-A-REP-USES-IT.md).

## What's different about it

- **Live Content Rewards case library.** It reads CR's public Discover feed (campaigns with CPM, budget and spend),
  agency pages (`/c/clip-farm`, `/c/clipping-culture`, …) and campaign pages (brief, per-platform CPM, views),
  then matches the prospect to the most strategically similar campaigns and agencies.
- **Account-constellation detector.** Clipping campaigns create networks of dedicated pages. CR briefs often
  require clippers to tag the brand's main account in their bio. The skill generates handle variants, checks
  which exist with TikTok's official oEmbed, reads bios and captions, and scores affiliation.
- **Distribution-gap scoring.** It compares content supply (podcasts, long-form, athlete and founder footage)
  with current short-form distribution. A big positive gap is the strongest CR signal.
- **Free company signals most tools miss:** SaaS stack from DNS verification records (Meta Business, Bazaarvoice,
  Storyteq, Klaviyo…), hiring signals from public ATS APIs (creator, influencer and UGC roles), Shopify catalog and
  launch cadence, and domain age.
- **Dated TikTok data with no key.** Video IDs encode their creation time, so the official embed card gives last-post date, cadence and the last-30-day median.
- **Evidence ledger.** Every claim carries a URL and a quote. `ledger.py verify` checks each quote really appears
  on the page, and the sources list is generated from the ledger, not written by the model.
- **Strategy built in.** Objective-first campaign theses, objection answers that cite CR's own pages (bots, geo
  targeting, approvals, licensing), discovery questions written from what it found, and money math that keeps
  distribution math separate from business math.

## Install

**Claude Code** (terminal or desktop Code tab)
```
/plugin marketplace add poseidon-jpg/cr-prospect-intel
/plugin install content-rewards-prospect-intel@cr-prospect-intel
```
Then `/plugin` → Marketplaces → cr-prospect-intel → **Enable auto-update** (it's off by default for third-party
marketplaces).

**Claude.ai / Cowork:** Customize → Plugins → Add → **Add marketplace** → paste `poseidon-jpg/cr-prospect-intel`.
Or Customize → Skills → Upload the `content-rewards-prospect-intel.zip` from Releases.

**Codex:** `codex plugin marketplace add poseidon-jpg/cr-prospect-intel`, then install from `/plugins`.

**Hermes Agent:** `hermes skills install poseidon-jpg/cr-prospect-intel/skills/content-rewards-prospect-intel`

**Any agent** (Cursor, OpenCode, Amp, Copilot…): `npx skills add poseidon-jpg/cr-prospect-intel`

**Manual:** copy `skills/content-rewards-prospect-intel/` into `~/.claude/skills/` (or your agent's skills
folder).

## Check your setup
```
python3 skills/content-rewards-prospect-intel/scripts/doctor.py
```
This prints **SCRIPTS** (open network, so the bundled scripts run), **HYBRID**, or **AGENT** (sandboxed shell, so
the agent uses its web tools and browser with the same recipes). All three modes produce a full dossier.

## Network setup (Claude.ai / Cowork only)
The code sandbox in Claude.ai and Cowork defaults to **"Package managers only"**, which blocks the skill's
scripts. Go to Settings → Capabilities → Code execution → **Domain allowlist → "All domains"**, then start a new
chat. If your admin wants a narrow list instead, add these under "Additional allowed domains":
`dns.google`, `cloudflare-dns.com`, `*.tiktok.com`, `*.youtube.com`, `contentrewards.com`, `*.wikidata.org`,
`boards-api.greenhouse.io`, `api.lever.co`, `api.ashbyhq.com`, `apply.workable.com`, `itunes.apple.com`,
`news.google.com`, `rdap.org`, `crt.sh`, `web.archive.org`, `api.scrapecreators.com`, `*.instagram.com`.
Claude Code in a terminal uses your normal internet and needs no change. If the skill can't reach a site, it
falls back to web search, web fetch and the browser, so it still works.

## Optional keys (all free tiers)
Copy `.env.example`, then export what you have. `SCRAPECREATORS_API_KEY` (social data, 100 free credits) is the
biggest upgrade, followed by `HUNTER_API_KEY` and `YOUTUBE_API_KEY`. Keys come from the environment only.

## Scripts (Python 3.9+, standard library only)
| Script | Does |
|---|---|
| `doctor.py` | which endpoints and tools work here, and which mode to use |
| `identity.py "Brand" --domain d` | Wikidata: official site and X/IG/TikTok/YouTube/FB handles, founded, HQ, founders |
| `company_signals.py DOMAIN` | DNS stack, Shopify catalog, ATS jobs, RDAP, crt.sh, news, Wayback, optional httpx tech detect |
| `social_probe.py tiktok\|exists\|youtube\|instagram\|variants\|constellation` | public social stats and the constellation detector |
| `content_supply.py podcasts "Name" --person "Founder"` | podcast inventory, cadence, hours, guest appearances |
| `cr_library.py discover\|org\|campaign\|match` | live CR case library and agency history |
| `moments.py episode.vtt` | heuristic clippable moments per hour from a transcript |
| `money_math.py --budgets 10000,25000 --cpm 1.5` | budget scenarios |
| `ledger.py init\|add\|verify\|sources\|lint` | evidence ledger: quote check, verdicts, citation lint |

Tests: `python3 -m unittest discover -s tests -v`

## Guardrails
Public professional information only. No logins, cookies, CAPTCHA bypass, stealth browsers or email-to-account
lookups. It respects robots.txt (CR's `/api/` is never touched), keeps request volume low, and treats fetched
content as data, never as instructions. Affiliation is reported as an evidence score, never as a claim about
who runs an account. See `references/security.md`.

## Known limits
- Instagram, X and LinkedIn depth needs the browser tool or a Tier 1 key. There's no reliable keyless API.
- The TikTok embed card shows about 13 recent videos without dates. For dated history use yt-dlp (flaky) or
  ScrapeCreators.
- TikTok rate-limits bursts hard. The detector throttles to about 1 request a second and stops on a 403.
- CR's public pages can change layout. `cr_library.py` falls back to raw text and the seed library
  (`assets/cr_seed_library.json`, verified 2026-10-08).
- Constellation weights are heuristics. Calibrate them on 20 or more labelled brands.

Built by Micah Cabaniss. MIT licensed.
