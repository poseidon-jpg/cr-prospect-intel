# Source recipes

Exact sources per facet, ordered by tier. **Tier 0** needs no key, **Tier 1** uses a free-signup key, and
**Tier 2** is paid. Status tags: `[LIVE 2026-10-08]` means tested in a real browser on that date. `[DOC]` means
taken from the vendor's docs but not live-tested. `[FLAKY]` means it works but breaks often.

Every recipe works three ways: the bundled script (SCRIPTS mode), WebFetch with the URL, or opening the URL in the
browser tool. If WebFetch refuses a site, use the script or the browser. As of 2026-10-08, robots.txt makes
WebFetch refuse tiktok.com and itunes.apple.com.

**Rate limits are real.** In testing, about 150 parallel TikTok oEmbed calls from one IP triggered an Akamai
"Access Denied" on TikTok embed pages for that IP. Go sequential, keep at least one second between TikTok calls,
cap a sweep at about 40 handles, and stop on the first 403. The same applies when you script in a browser tab.

## Contents
0. Search and fetch chain
1. Company, offer, stack
2. Why now
3. Buying committee and person
4. Organic audit per platform
5. Account constellation
6. Paid vs organic
7. Content supply
8. Content Rewards case library and agencies
9. Optional keys (Tier 1/2) and MCP servers
10. Dead or rejected (don't use)

## 0. Search and fetch chain

SEARCH: the host's WebSearch → keyless remote MCP servers if installed (`https://mcp.exa.ai/mcp`,
`https://search.parallel.ai/mcp`, `https://mcp.firecrawl.dev/v2/mcp`) → a self-hosted SearXNG with
`formats: [html, json]` enabled (`GET http://localhost:8080/search?q=...&format=json`; this is the keyless backend
Perplexica, khoj and local-deep-research use) → `pip install ddgs` (9.16.x, multi-backend, keyless,
scrape-based so it can break) → keyed Tavily (1,000/mo free) or Exa ($10/mo credit). If a query that uses
operators (`site:`, `OR`) comes back empty, retry it as plain words. Many backends ignore operators
(gpt-researcher's planner rule).

FETCH: the host's WebFetch (it summarizes, so ask it for "verbatim text" or "raw JSON") → the scripts'
`_common.fetch` → **Crawl4AI** locally (`pip install crawl4ai`; 84.6k stars, Apache-2.0; use `fit_markdown`, never
its stealth mode) or **Jina Reader self-hosted** (`docker run -p 3000:8081 ghcr.io/jina-ai/reader:oss`, keyless,
so prospect URLs never leave the laptop) → the official Jina MCP `https://mcp.jina.ai/v1` (keyless at rate
limits) or `https://r.jina.ai/<url>` → Playwright MCP / the browser tool (plain browsing, clean profile, never
stealth). Keep the stdlib RSC parser for contentrewards.com. No markdown extractor keeps the structured campaign
fields.

Never send a prospect's email address or personal name to third-party readers (Jina, Firecrawl, Exa) inside a URL.
Only send public company URLs.

## 1. Company, offer, stack (facet A)

| What | Tier 0 source |
|---|---|
| Offer, pricing, ICP | Company homepage, /pricing, /about, /pages/about-us, /collections/all, footer links. Read the actual words customers see. |
| SaaS stack from DNS `[LIVE]` | `https://dns.google/resolve?name=DOMAIN&type=TXT` and `&type=MX`, plus `_dmarc.DOMAIN`. Mapping: `scripts/company_signals.py` TXT_TOKENS. `facebook-domain-verification` means they've set up Meta Business (ads/commerce). `bv-domain-verification` means Bazaarvoice (UGC/reviews). `storyteq` means creative automation at scale. `tiktok-developers-site-verification` means a TikTok integration. A Proofpoint or Mimecast MX means an enterprise IT org. |
| Shopify catalog `[LIVE]` | `https://DOMAIN/products.json?limit=250&page=1` gives product count, list-price band, and `created_at` launch cadence. Headless stores return 403 (gymshark did); that isn't proof they're off Shopify. |
| Hiring `[LIVE greenhouse]` | Greenhouse `https://boards-api.greenhouse.io/v1/boards/SLUG/jobs?content=true` · Lever `https://api.lever.co/v0/postings/SLUG?mode=json` · Ashby `https://api.ashbyhq.com/posting-api/job-board/SLUG` · Workable `https://apply.workable.com/api/v1/widget/accounts/SLUG`. Roles mentioning creator, influencer, UGC, social, TikTok, affiliate or community are buying signals. |
| Domain age | `https://rdap.org/domain/DOMAIN` (registration date) · Wayback first snapshot `https://web.archive.org/cdx/search/cdx?url=DOMAIN&limit=1&output=json` |
| Subdomains | `https://crt.sh/?q=%25.DOMAIN&output=json` (slow). Look for `shop.`, `creators.`, `ambassadors.`, `affiliates.`, `app.`, `rewards.` |
| Site tech, affiliates, ESP | In the homepage HTML look for `static.klaviyo.com` (Klaviyo), `cdn.attn.tv` (Attentive), `impact.com`/`irclickid` (Impact affiliate), `refersion`, `grin.co`, `superfiliate`, `shopmy`, `ltk`, `cdn.shopify.com`. These are hints; confirm before stating. |
| Public company | SEC full-text search `https://efts.sec.gov/LATEST/search-index?q="influencer"&ciks=...` (requires a User-Agent with a contact). 10-K mentions of "creator" or "influencer" signal budget. |
| Scale | Team size from the LinkedIn company snippet (`site:linkedin.com/company "Name"`), press releases, and app store rating counts. Label it an estimate. |

Script: `python3 scripts/company_signals.py DOMAIN --company "Name"` (add `--fast` to skip crt.sh and wayback).
Its `tech` section uses projectdiscovery **httpx `-td`** when installed (MIT, BuiltWith-class detection from
wappalyzergo fingerprints, refreshed weekly). Otherwise it prints the manual HTML signatures to check. Install from
github.com/projectdiscovery/httpx/releases. Note that the Python `httpx` package has a CLI with the same name;
the script tells them apart.

Tier 1: Hunter `/companies/find?domain=` (50 credits/mo), TheCompaniesAPI (500 free credits). Tier 2: Apollo via
its official MCP (paid account), Crunchbase API ($49+/mo).

## 2. Why now (facet B)

- Google News RSS `[DOC]`: `https://news.google.com/rss/search?q="Company"+when:90d&hl=en-US&gl=US&ceid=US:en`.
  Links are Google redirect URLs, so open the original before citing.
- The company newsroom, /blog, /press, changelog, and LinkedIn company posts (via search snippets).
- Funding: press plus the company's own announcement. A database page alone is REPORTED, not CONFIRMED.
- Launches: new products in the Shopify `created_at` data, app store "What's New"
  (`https://itunes.apple.com/lookup?id=APPID`), and new collections.
- Hiring spikes from the ATS (facet A). A first creator or social hire means a channel is being built.
- Events: tour dates, film or album release dates, game launches, sports seasons. These are eventization windows.
- Count a catalyst only if it's dated and tied to a plausible distribution need.

## 3. Buying committee and person (facet C)

**Company identity and official handles first (keyless, verified 2026-10-08):** `python3 scripts/identity.py
"Brand" --domain brand.com`. It uses Wikidata search (`wikidata.org/w/api.php?action=wbsearchentities&search=...`)
and `wikidata.org/wiki/Special:EntityData/QID.json`. Properties: P856 website, P2002 X, P2003 Instagram,
P2397 YouTube channel ID, P7085 TikTok, P2013 Facebook, P4264 LinkedIn company ID, P571 founded, P159 HQ,
P112 founders, P169 CEO, P749 parent, P355 subsidiaries, P249 ticker. For Gymshark it returned every official
handle, matching what we saw on the platforms. Coverage is thin for small brands, so treat it as corroboration.

- Search `site:linkedin.com/in "Company" (CMO OR "VP Marketing" OR "Head of Growth" OR "Head of Social" OR
  "Creator Partnerships" OR "Influencer")`. Use the snippets only and never log in to LinkedIn.
- Check the company team page, press quotes ("said Jane Doe, VP Marketing"), podcast guest appearances, and
  conference speaker pages.
- For the prospect: their title, tenure, previous companies (snippets), and their public posts or talks about
  creators, UGC or influencer marketing. These are discovery ammunition.
- Gravatar `[DOC]`: `https://www.gravatar.com/avatar/MD5(lowercased email)?d=404`. A 200 means a public profile
  exists. Use only to confirm the email is active. Don't harvest anything from it.
- Mark each stakeholder CONFIRMED (company page or the person's own profile) or REPORTED (a single snippet).
- Tier 1: Hunter `/people/find?email=` · PDL person enrich (accept only `likelihood >= 6`).
  Tier 2: Apollo, Prospeo or RocketReach MCP, only with user approval.

## 4. Organic audit per platform (facet D)

Find the official handles first: `identity.py` (Wikidata), the website footer, the link-in-bio,
`site:tiktok.com/@ "Brand"`, and the `sameAs` field in the site's JSON-LD. For local or SMB prospects, the
Overture Maps Places open dataset (monthly releases, CDLA-2.0) carries `websites`, `socials` and `emails` arrays.
Query a small bounding-box slice with DuckDB. Don't download the whole set.

### TikTok
- Existence `[LIVE]`: `https://www.tiktok.com/oembed?url=https://www.tiktok.com/@HANDLE`. A profile returns
  `embed_type:"profile"` with `author_name`. A missing account returns `{"code":400}`.
- Profile and recent views `[LIVE]`: `https://www.tiktok.com/embed/@HANDLE`. The
  `<script id="__FRONTITY_CONNECT_STATE__">` JSON holds `userInfo{followerCount, heartCount, followingCount,
  signature, verified, nickname}` and `videoList[~13]{id, desc, playCount}`. **Dates come from the video ID:**
  `id >> 32` is the creation time in Unix seconds, accurate to the day (verified; Bellingcat's tiktok-timestamp
  uses the same rule). That gives last-post date, posts per week and the median views over the last 30 days, all
  keyless. Pinned videos skew the maximum. Script: `social_probe.py tiktok HANDLE`. In the browser the same page renders followers, likes
  and per-video views.
- Dated full history (opt-in, local) `[FLAKY]`: `social_probe.py tiktok-history HANDLE` wraps
  `yt-dlp --flat-playlist -J --impersonate chrome https://www.tiktok.com/@HANDLE`. It returns 30/90/365-day post
  counts, median views and top posts. Public data, no login. Use it in DEEP and WAR ROOM modes when installed.
  (install with `pip install -U "yt-dlp[default,curl-cffi]"`; yt-dlp issues #17500 and #17403 are open).
- A single video `[LIVE]`: oEmbed with the video URL gives the caption and author.
- Tier 1: ScrapeCreators (`x-api-key`): `/v1/tiktok/profile?handle=`, `/v3/tiktok/profile/videos?handle=&sort_by=latest`,
  `/v1/tiktok/search/keyword?query=`, `/v1/tiktok/search/users`, `/v1/tiktok/video/comments`. Verified on the
  homepage on 2026-10-08: 100 free credits, up to 7,000 more claimable, no card, credits never expire, and cached
  results cost 0. The "10,000 free" figure in other READMEs is outdated. This is the only clean route to TikTok
  keyword and user search. There's no legitimate keyless one; every OSS tool that does it signs requests or uses
  cookies.
  Alternatives: the HasData MCP (`https://mcp.hasdata.com/api/mcp?apis=tiktok`, 1,000 trial credits) and
  EnsembleData (50 units/day free).
- TikTok Shop: open the brand's shop tab in the browser. Tier 2: FastMoss Open API or Kalodata.

### Instagram
- Tier 0: open `https://www.instagram.com/HANDLE/` in the browser tool (public view, low volume) and read
  followers, post count, bio, link-in-bio, the last 12 posts and Reels view counts. You can also search
  `site:instagram.com "HANDLE"`.
- Tier 1: ScrapeCreators `/v1/instagram/profile?handle=` (`social_probe.py instagram HANDLE`). If the team owns an
  IG Business account and a Meta app, Graph API Business Discovery is the first-party route.
- Don't use instaloader with a login, instagrapi, or the private `web_profile_info` endpoint with spoofing.

### YouTube
- `[DOC]` `https://www.youtube.com/@HANDLE` gives the channel ID (`"externalId":"UC..."`) and the subscriber text.
  RSS at `https://www.youtube.com/feeds/videos.xml?channel_id=UC...` gives the latest ~15 uploads with views and
  dates. Script: `social_probe.py youtube @HANDLE`.
- Full inventory: `yt-dlp --flat-playlist -J https://www.youtube.com/@HANDLE/videos` (and `/shorts` and
  `/streams`). It needs Deno 2.3 or later, or Node 22 or later. Tier 1: the Data API `channels.list` plus
  `playlistItems.list` (1 unit each; avoid `search.list`, which costs 100 units).

### X, LinkedIn, Facebook, Threads
- Tier 0: search snippets (`site:x.com/HANDLE`, `site:linkedin.com/company/SLUG`), the browser for public pages,
  and the brand's own embeds. Nitter and xcancel received an X Corp cease-and-desist in August 2026, so don't use
  them.
- Tier 1: xAI `x_search` (`allowed_x_handles`, max 10, returns posts with citations) or the X API (pay-per-use:
  $0.005 per post read, $0.010 per user read). ScrapeCreators covers X, LinkedIn, Facebook and Threads profiles.

### What to record per platform
Followers, posting cadence (posts in the last 30/90 days), the median and top views in the sample, the ratio of top
content to the median, content archetypes (founder, demo, UGC, meme, education, podcast clip, trend), hooks,
recurring faces, CTAs, whether they use paid-partnership labels, and the date of the last post. Missing metrics
are UNKNOWN, never estimated.

## 5. Account constellation (facet E)

Clipping campaigns create networks of dedicated pages. CR briefs often **require** clippers to run dedicated pages
that tag the brand's main account in the bio. For example, the Michael Sartain campaign says "You need dedicated
pages ... tagging his main page in bio". So the strongest public signal is a bio that mentions `@brandhandle`.

1. Generate variants: `social_probe.py variants "Brand" --handle brand` gives brandclips, brand.daily, brandhq,
   thebrand, brandfans, brand_edits and so on (about 120).
2. Check which exist: `social_probe.py constellation "Brand" --handle brand --domain brand.com`. This runs oEmbed
   existence checks, then reads each embed card (bio and captions) and scores it with the rubric in `scoring.md`.
3. Find accounts with unrelated names (theme or fan pages) that variants miss:
   - Search `site:tiktok.com "@brandhandle"`, `site:instagram.com "@brandhandle" clips`, `"brandhandle" clips`, and
     `"#brand" edits`.
   - Search for the founder or creator name plus "clips", "podcast clips" or "highlights" (the clipping-army
     pattern).
   - Check TikTok and Instagram search in the browser for the brand name and look at bios.
   - Feed the handles you find back in with `--extra h1,h2`.
4. Check the CR and Whop side: does the brand or its founder appear as a campaign on contentrewards.com
   (`cr_library.py match --keywords "Brand"`)? If they do, they're an existing customer or already clipping. That
   changes the whole call into an expansion conversation.
5. Report the number of LIKELY and POSSIBLE affiliated accounts, their total followers, their median views
   compared with the official account, and examples with links. Note that a large network with high views means
   they already understand distributed organic, so the angle is scale, measurement and infrastructure.

Optional (WAR ROOM): `pip install maigret`, then `maigret BRANDHANDLE --tags social,video`. This finds where the
brand's handle exists across hundreds of sites. Use it on brand handles only, never on a private person's
username, and expect false positives. Never use Holehe, GHunt or any email-to-account lookup.

Supply-side hint: a TikTok constellation whose captions share one burned-in caption style and hook template,
whose videos are stock footage plus TTS narration, or whose posting times are machine-regular, is probably farm
or faceless output (MoneyPrinterTurbo-class tooling). Note it as an observation and point the AE to the
playbook's "supply side" section.

## 6. Paid vs organic (facet F)

- Meta Ad Library (browser): `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=BRAND`.
  Count active ads, note their start dates and formats, and look for creator-led creative. The API only covers EU
  and UK delivery plus political ads, so for US commercial ads use the UI.
- TikTok Creative Center top ads (browser): `https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en`.
  Search the brand. There's no official API.
- Google Ads Transparency (browser): `https://adstransparency.google.com/?region=US&domain=DOMAIN`.
  Tier 1: SerpApi (250 searches/month).
- Paid-partnership labels on creator posts about the brand mean direct creator spend.
- The `facebook-domain-verification` DNS token means they have set up Meta Business.
- Possible readings: "paid-heavy, organic-thin" (lots of ads, a weak owned feed), "creative supply but no
  distribution", or "organic-native". Never infer spend amounts.

## 7. Content supply (facet G)

- Podcasts `[DOC]`: `https://itunes.apple.com/search?media=podcast&term=NAME` returns `feedUrl`. Parse the RSS for
  episode count, cadence and total hours. Script: `content_supply.py podcasts "Name" --person "Founder"`. The
  `--person` flag greps show notes for guest appearances, which are clippable footage the founder doesn't own but
  can repost.
- YouTube long-form and livestreams: see §4. Count hours where possible.
- Founder media: keynotes, interviews, webinars, Twitch or Kick streams, TV appearances, owned events, athlete or
  ambassador footage, commercials, and existing UGC libraries (Bazaarvoice in DNS or "#brand" UGC).
- Rate supply LOW, MEDIUM, HIGH or EXTREME with the evidence.
- **Clippable moments per hour** (heuristic): get one representative transcript (the show's own transcript,
  or `yt-dlp --write-auto-subs --skip-download --sub-format vtt URL`), then run `python3 scripts/moments.py
  episode.vtt`. Report the range and label it HEURISTIC. Realistic expectation: a handful of strong moments per
  episode-hour. "100 clips from one episode" means re-cuts or the same clip posted from many accounts.

## 8. Content Rewards case library and agencies (facet H)

- Live featured campaigns `[LIVE]`: `https://contentrewards.com/c/discover`. About 50 structured campaigns are
  embedded in the page data (organizer, category, CPM, budget, spend, creators, platforms). Script:
  `cr_library.py discover`.
- Org or agency history `[LIVE]`: `https://contentrewards.com/c/HANDLE` lists every campaign an org has run.
  Verified handles: `clip-farm` (235 campaigns), `the-clip-ship` (206), `clipping-culture` (197),
  `artist-influence` (161), `virality` (122), `propaganda` (112), `cliphaus` (98), `clipix` (49). Script:
  `cr_library.py org clip-farm`.
- Campaign detail `[LIVE]`: `https://contentrewards.com/discover/UUID` shows per-platform CPM, min/max per clip,
  budget spent and remaining, the full brief, total views, participants and top earners. Script:
  `cr_library.py campaign UUID`. Compute effective CPM as spent divided by views/1,000 and label it derived.
- Matching: `cr_library.py match --keywords "fitness,apparel,gym" --category "Consumer Brand"`. Choose the most
  strategically similar cases (same objective, content type, audience or category), not the biggest ones.
- CR facts and pricing: `/pricing`, `/agencies`, `/brands-terms`, `/articles/what-makes-a-great-content-rewards-campaign-brief`.
- robots.txt disallows `/api/`. Don't call it.

## 8b. Browser mode: the rep's own browser (Claude in Chrome / Playwright)

When the agent has a browser tool, it can view public pages the way the rep would by hand. This fills the gaps
APIs can't: TikTok user and keyword search results, Instagram profiles and Reels view counts, X search, Meta Ad
Library, TikTok Creative Center, and CR's rendered pages.
- Human pace: one page at a time, a few seconds apart, about 30 pages per prospect at most. No parallel request
  bursts. In testing, a 150-call burst got the IP blocked by TikTok for a while.
- Read only. Don't click follow, like, message or connect, and don't change any account settings.
- If the rep is logged in, that's their normal browsing, but keep it to viewing. Don't run automated scrolling
  loops through LinkedIn: its user agreement bans automation and accounts get restricted. Use search snippets for
  LinkedIn.
- If a page shows a CAPTCHA or "unusual activity" wall, stop that platform and note "blocked". Don't solve it.

## 9. Optional keys (Tier 1/2) and MCP servers

| Key / server | Gives you | Free tier |
|---|---|---|
| `SCRAPECREATORS_API_KEY` | TikTok, IG, YouTube, X, LinkedIn, FB and Threads public data, TikTok search | 100 credits plus up to 7,000 claimable |
| `HUNTER_API_KEY` or `https://mcp.hunter.io/mcp` | email and company enrichment, verifier | 50 credits/mo |
| `PDL_API_KEY` | identity resolution with a likelihood score | 100/mo (contacts obfuscated) |
| `YOUTUBE_API_KEY` | full channel inventory | 10k units/day |
| `XAI_API_KEY` | live X search with citations | paid per result |
| `SERPAPI_API_KEY` | Google Ads Transparency, SERP | 250/mo |
| Exa / Parallel / Firecrawl remote MCP | better search and extraction | keyless tiers, rate-limited |
| Apollo MCP `https://mcp.apollo.io/mcp` | people and org search and enrichment | paid accounts only |

Never put keys in files inside the skill. Read them from the environment only. For an optional keyless MCP
pack (fetch, DuckDuckGo, Playwright, Wikipedia, GDELT, SEC EDGAR), see `references/mcp-powerups.md`.

## 10. Dead or rejected (don't use)

Clearbit logo/enrichment (shut down December 2025) · Crunchbase free API (gone) · Proxycurl (shut down July 2025
after a LinkedIn lawsuit) · Nitter/xcancel (X C&D, August 2026) · snscrape (unmaintained since 2023) ·
twscrape/twikit/instagrapi/linkedin-api (need logins) · Google Custom Search JSON API (closed to new customers) ·
`@modelcontextprotocol/server-brave-search` (deprecated; use `@brave/brave-search-mcp-server`) ·
duckduckgo_search (renamed to `ddgs`) · Holehe/GHunt (email-to-account and cookie tools) · Camoufox/Scrapling
stealth modes (bot evasion) · Reddit anonymous `.json` (403 for cloud IPs since mid-2026, per secondary reports;
use search snippets and HN Algolia instead).
