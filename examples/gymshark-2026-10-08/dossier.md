# Prospect Dossier: Gymshark (example run, company-level)
Prepared 2026-10-08 · Mode DEEP (company-level: no named prospect, to avoid profiling a real individual in a public
example) · Environment HYBRID (browser + WebSearch/WebFetch; the shell was sandboxed) · Built by hand following
the skill's protocol.

> `[n]` = source number (list at the bottom). "Not checked" means we couldn't look, so confirm it on the call.
> Run note: the TikTok constellation sweep sent about 150 parallel oEmbed calls and TikTok's edge returned "Access
> Denied" for the embed pages afterwards. The script now throttles to about 1 request a second and stops on a 403.
> That's why the bio and caption scoring in §7 is incomplete.

## 1. Executive snapshot
- **Who:** UK gymwear brand. FY25 (year to 31 Jul 2025) revenue was £646M, the "13th consecutive year of sales
  growth". Profit before tax fell to £7.0M, which the founder calls "intentional" reinvestment [1]. The company is
  expanding into physical retail (Manhattan flagship, Roosevelt Field, Dubai, Amsterdam) [1] and opening its first
  gym, the Gymshark Lifting Club in Miami's Wynwood district [2].
- **Distribution state:** organic-native at the top: TikTok has 6.7M followers and 141.2M likes [3], Instagram
  8.6M followers [4]. Long-form and Shorts on YouTube are thin: 727K subscribers. The three most recent long-form
  uploads are 2 months, 11 months and 1 year old, and recent Shorts get 10K-50K views [5].
- **Constellation:** 13 TikTok handles built on "gymshark" exist (vault, clips, daily, fan pages, men/women)
  [3b]. Affiliation hasn't been scored yet, and several look like fan pages or repurposed personal pages. This is
  unmanaged distribution around the brand.
- **Wedge:** *already organic-native, so sell scale, control and measurement.* The pitch is to turn athlete and
  launch moments (Onyx drops, Sam Sulek, David Laid, Lift the City, the Miami gym) into briefed, measured,
  geo-targeted clipping, at about $1.50-2.00 per 1K views [6][7], as an efficiency play while profit is under
  pressure. They're hiring an **Influencer Marketing Manager (12-month FTC)** right now [8], so creator ops is
  stretched.
- **Best first move:** a 30-day test around the next drop: athlete and workout clipping on TikTok, IG Reels and
  YT Shorts, US-weighted (geo requirement like CR's "35%+" campaigns [7]), run by an agency with consumer and
  athlete history.

## 2. Identity resolution: confidence 95/100 (company)
| Field | Value | Evidence |
|---|---|---|
| Company | Gymshark Ltd, gymshark.com | [1][9] |
| Founder/CEO | Ben Francis, holds ~70% after General Atlantic's 21% (2020); reportedly in talks to buy part of it back (FT via SGI, unconfirmed) | [10] REPORTED |
| Other named leaders (dated) | Ash Wilson, men's head of brand; Sam Kane, head of communications; David Laid, creative director (lifting) | [11] (May 2025; titles may have changed) |
| Official handles | TikTok @gymshark ✓ verified · IG @gymshark · YouTube @gymshark (UCma7hhYJ3bfEhZgw3xl77ww) · X @Gymshark and @GymsharkCentral · founded 2012 | [3][4][5] + Wikidata Q56246099 (v0.2 `identity.py`; the handles match the platforms) |
Prospect person: not specified in this example. In a real run, resolve the attendee from the email domain plus
`site:linkedin.com/in "Gymshark"` snippets.

## 3. Company, offer, ICP
- Gymwear and lifting apparel, DTC-first, now omnichannel retail [1]. Premium drops: Onyx (men's performance
  line, relaunched 2025 after 5 years, resale over $600) [11].
- **Stack from DNS (gymshark.com TXT) [9]:** Meta Business verification (`facebook-domain-verification`, so they
  run Meta ads/commerce) · **Bazaarvoice** (`bv-domain-verification`, reviews/UGC syndication) · **Storyteq**
  (creative automation, meaning ad variants at scale) · Mixpanel · Figma · Wrike · Atlassian · Adobe enterprise
  and Adobe Sign · Microsoft 365 · Apple · OpenAI and **Anthropic** domain verification · OneTrust · HackerOne ·
  Zoom · Jamf · Proofpoint mail gateway (SPF). Reading: a mature enterprise marketing org with a paid creative
  machine and a UGC/reviews program.
- Shopify `/products.json`: blocked (CloudFront 403, headless storefront). Price band not checked here; read it
  off the site.
- **Hiring [8]:** 7 open roles on Greenhouse. The buying signal is **"Influencer Marketing Manager (12m FTC)",
  Brand Management, Solihull, updated 2026-08-07.**

## 4. Why now
| Date | Event | Source | Relevance |
|---|---|---|---|
| 2026-04-13 | First gym announced (Miami, Wynwood), "expected to open this summer" | [2] | local and US eventization; endless gym-floor footage |
| 2026-03-12 | FY25: £646M revenue, PBT down to £7.0M "intentional" | [1] | efficiency narrative: cheaper distribution than paid |
| 2026-08-07 | Influencer Marketing Manager role (fixed-term) | [8] | creator ops capacity gap |
| TikTok pin (undated) | "Onyx V1 Returns. July 16th" and "Chapter Four: The Return", pinned with 1.7M and 1.2M views | [3] | drop-based storytelling already works |
| 2025-07-22 | Sam Sulek appears as the newest Gymshark athlete (training with CBum and David Laid) | [12] | the biggest clip-native fitness creator on the roster |
| ongoing | "Winter arc" content series live on TikTok (37K-968K views) | [3] | a seasonal narrative that suits distributed clipping |

## 5. Buying committee (verify current titles)
| Person | Title (as reported) | Why they matter | Likely role | Evidence |
|---|---|---|---|---|
| Ben Francis | Founder/CEO | final say on brand bets | economic buyer (large) | [1][2] CONFIRMED |
| Ash Wilson | Men's head of brand | ran the Onyx relaunch hype | champion for drops | [11] REPORTED (2025) |
| Sam Kane | Head of communications | "community-driven" framing | influencer | [11] REPORTED (2025) |
| David Laid | Creative director, lifting | "oversee athlete recruitment… campaign creation" | content source + champion | [11][13] |
| (Hiring) Influencer Marketing Manager | Brand Management | will run creator programs | user/operator | [8] |

## 6. Organic presence by platform
| Platform | Followers | Cadence | Sampled views | Notes |
|---|---|---|---|---|
| TikTok @gymshark | 6.7M · 141.2M likes | active (winter arc series) | 13 embed videos: 19.7K-1.7M, median ~197K (top 3 pinned) | athlete-led (David Laid, Ryan Terry, Luke Elsman), drop teasers, mindset captions [3] |
| Instagram @gymshark | 8.6M · 1,760 posts | not counted | not checked | highlights: athletes, events (BHM UK '26, Olympia '26) [4] |
| YouTube @gymshark | 727K · 438 videos | latest long-form: 2mo, 11mo, 1y ago | long-form 14K-103K; Shorts 10K-50K | **under-leveraged**: "Sam Sulek signs with Gymshark" Short only 27K [5] |
| X, LinkedIn, Facebook | not checked | | | confirm on call |

## 7. Distribution topology and account constellation (TikTok)
Method: 151 handle variants, then the official oEmbed existence check (100 answered before rate limiting), then
display names [3b].

| Handle | Display name | Read (unscored) |
|---|---|---|
| gymshark | Gymshark | CONFIRMED OFFICIAL |
| gymsharkwomen | Gymshark Women | name match; brand-style name, so check whether it's official, fan or impersonation |
| gymsharkvault | Gymshark Vault | name match; archive or fan-style |
| gymshark.clips / gymsharkclipz | "Gym shark Clips" / "johnfitness" | clip-style names; the second is a personal page using the brand handle |
| gymshark.daily | "jackneelmotion" | personal or repurposed page on a brand handle |
| gymshark_official / gymshark.official | "user47264267351" / "gymshark page" | likely squatters or impersonation; flag |
| realgymshark, thegymshark, gymshark_fan, gymsharkfanpage, gymsharkmen | various | fan or name-squat pattern |

**Read:** a lot of unmanaged surface area. The brand's name is being used as distribution real estate by fans and
squatters, but there's no visible coordinated clip network tagging @gymshark (unscored). That's the gap: the
demand to clip Gymshark content exists, and nobody is directing it. Next step: rerun `constellation` at the
throttled rate to score bios and captions, plus search `site:tiktok.com "@gymshark" clips`.

## 8. Content winners and patterns (TikTok sample, n=13)
- Drop-narrative "chapters" with athletes (Onyx, David Laid) reach 0.78M-1.7M. Mindset or seasonal captions run
  20K-970K. Single-athlete feature posts run 41K-60K [3].
- Pattern (sample-based, not statistical): **serialized drops with a hero athlete beat standalone posts.** That
  suits clipping: many accounts re-cutting the same chapter around launch week.

## 9. Audience and comment intelligence
Not checked (comments need a browser session or a Tier 1 API). Confirm the US vs UK audience split on the call.
That determines the geo requirement.

## 10. Paid vs organic
- Meta Business is verified via DNS [9]. Storyteq suggests high-volume paid creative variants [9].
- Meta Ad Library keyword "gymshark" (US, active): ~1,000 results, but the keyword search includes other
  advertisers [14]. Advertiser-page count not checked.
- Reading: **balanced, with a strong paid machine.** CR's angle isn't "replace paid". It's organic distribution
  density plus licensed winners for paid. CR terms grant brands perpetual, royalty-free rights to approved clips,
  including for ads [15].

## 11. Content supply: EXTREME
| Source | Volume | Clippable? | Rights |
|---|---|---|---|
| Athlete roster content (Sam Sulek, David Laid, CBum collabs, Ryan Terry…) | very large, daily | yes, gym/workout clips are the format | athletes own their channels, so clearance is needed |
| Brand YouTube (438 videos, HIIT IT OFF series) | hundreds of hours | yes | owned |
| Events (Lift the City, Olympia, BHM, store openings, Miami gym) | recurring | yes | owned |
| Founder interviews (WHOOP podcast #295, How I Built This, OMR, BBC's Good Bad Billionaire) | 5+ long-form | yes, founder-story angle | third-party shows, check permissions [16] |

## 12. Scores
| Score | Value | Drivers |
|---|---|---|
| Organic Distribution Maturity | 70 | huge owned TikTok/IG and athlete-led creative; YT Shorts weak; no managed clip network |
| Supply / Distribution / Gap | 90 / 60 / **+30** | athlete and event footage far exceeds what's distributed in short form outside the main accounts |
| Cultural Surface Area | 9/12 node types | owned, athletes, creators, fans, squatter pages, press, events, retail, community. Missing: managed clip pages, podcasts-as-channel, affiliates (not checked) |
| **CR Fit** | **70 (medium-high)** | +gap, +supply, +category fit (fitness/lifestyle), +catalysts, +budget. −rights complexity on athlete footage, −a mature in-house team that may want control |

## 13. The wedge
Gymshark doesn't need to be taught organic. It needs **more of it, cheaper, measured, and pointed at moments.**
The brand's name already drives unmanaged accounts. Make that demand productive: a briefed clipping program on
athlete and event footage, paid per verified view, geo-weighted to the US where they're building retail and a
gym. Approved winners get licensed into the Storyteq/Meta paid machine.

## 14. Campaign theses
**Thesis 1: "The Lift Season" US launch-window ubiquity**
- Outcome: US awareness and foot traffic around the next drop, the NYC stores and the Miami gym.
- Perception: "everyone who lifts seriously is in Gymshark right now."
- Source: athlete workouts (Sulek, Laid), Lift the City and Miami gym footage, drop teasers.
- Mechanic: CPM $1.50-2/1K, per-clip cap around $150, a "35%+ US audience" requirement and a demographics
  screenshot. Brief: dedicated pages tagging @gymshark in the bio, 9:16, 15-60s, captions burned in, disclosure.
- Test: $25K over 30 days. Scale trigger: effective CPM ≤ $2 and branded-search lift in the US during the
  window. Kill trigger: under 40% US audience on approved clips.
- Operator: an agency with athlete and consumer history (see §16).

**Thesis 2: "Founder story" evergreen**: Ben Francis interviews clipped for entrepreneur audiences (pizza
delivery to a £1B brand). Low CPM ($0.75-1), personal-brand style like CR's Daniel Bitton and Michael Sartain
campaigns [6].

**Thesis 3: UGC proof for paid**: per-post UGC try-on and fit content (Bazaarvoice signals an existing UGC
appetite). Winners go to Storyteq variants.

## 15. CR case matches
| Campaign | Organizer | Category | CPM | Spend/Budget | Result | Why analogous |
|---|---|---|---|---|---|---|
| Michael Sartain's Clipping Army | Michael Sartain's Clipper Army | Personal Brand | $1-2 by platform | $6,841 spent | 4.5M views, so about $1.52 eCPM (derived) | dedicated-page brief requiring the main @handle in bio, the exact structure for athlete clipping [6] |
| Backyard Breaks | ClipHouse | Sports | $2 | $50.1K / $60.2K | 226 creators | sports and collectibles consumer, high-spend always-on [17] |
| Topps x Clipfarm | Clip Farm | Consumer Brand | $1 | n/a | 572 participants | a big consumer brand running clipping [18] |
| [35%+GERMANY] STRANGER THAN HEAVEN | Clipping Culture | Gaming | $2.70 | n/a | n/a | proof that geo-targeted requirements work [7] |
| DreamMe [HEALTH] | Reachify | Health & Wellness | $1 | $26.7K / $29.5K | 65 creators | wellness-category spend [17] |

## 16. Agency matches (public campaign history)
| Fit | Agency | Evidence | Why | Caveats |
|---|---|---|---|---|
| Best | **Clip Farm** | 235 campaigns: Topps, Arena Club, Betr, Boxabl, SoFi, Jake Paul | consumer brands plus athlete/sports breadth, retainers available | confirm category exclusivity and capacity directly |
| Secondary | **Clipping Culture** | 197 campaigns, geo-targeted "[35%+COUNTRY]" campaigns | if geo control is the priority | music and gaming lean |
| Self-serve possible | Gymshark in-house | mature social team + new Influencer Marketing Manager | they may want to own the brief and creator pool | ops load is the reason they're hiring |

## 17. Likely objections
| Objection | Why they'll raise it | Answer (cite) | Don't claim |
|---|---|---|---|
| "Off-brand edits will hurt a premium brand" | Onyx is premium | brief-governed approvals, nothing auto-approves, pre-post review [15][19] | every clip on-brand |
| "Athlete footage rights" | the athletes own their channels | use brand-owned footage first. Brand-provided footage gives brand ownership of the clip [15] | that CR clears athlete rights |
| "We need US, not global views" | US is the growth market | geo-requirement campaigns exist (35%+ country) [7] | paid-grade targeting |
| "Bots" | standard | bot-likelihood score before approval, flagged payouts held [19] | "zero bots" |
| "We already have huge organic" | true | it's about scale, measurement and moments, plus licensed winners for paid | that their organic is weak |

## 18. Discovery questions
1. "Your Onyx chapter posts hit 1.2-1.7M on TikTok, but the Sam Sulek signing Short got 27K on YouTube. Is
   YouTube Shorts a priority or a known gap?"
2. "There are at least a dozen TikTok accounts using 'gymshark' in the handle, from 'clips' and 'vault' to
   personal pages. Is any of that yours or your agency's, or is it all unmanaged?"
3. "With the Influencer Marketing Manager role open, is the bottleneck finding creators, briefing them, or paying
   and tracking them?"
4. "For the US push and the Miami gym, what should a lifter in Miami be saying about Gymshark in 90 days that they
   don't say today?"
5. "How do winning organic edits get into your paid creative today?"
6. "Who owns the rights to athlete workout footage you could hand to clippers?"

## 19. Money math (distribution only; `money_math.py --cpm 1.5 --paid-cpm 10`)
| Budget | After 10% fee | Paid-for views @ $1.50 | All-in eCPM | Same views at an assumed $10 paid-social CPM |
|---|---|---|---|---|
| $10K | $9K | 6.0M | $1.67 | $60K |
| $25K | $22.5K | 15.0M | $1.67 | $150K |
| $50K | $45K | 30.0M | $1.67 | $300K |
| $100K | $90K | 60.0M | $1.67 | $600K |
The $10 paid CPM is an assumption for comparison only. Ask what they actually pay. Business-outcome math wasn't
modelled (no AOV or conversion data); ask for branded-search and store-traffic baselines.

## 20. Call strategy
- **Open with:** the YouTube Shorts gap vs TikTok chapters (Q1). It's specific and non-threatening.
- **Establish:** the US launch-window goal and who owns creator ops.
- **Ask early:** Q2 (the handle squatters and fans). It shows homework and opens the "managed vs unmanaged" frame.
- **Don't lead with:** "cheap views" or "your organic needs help".
- **Expansion logic:** start with one drop window, then roll into always-on athlete clipping, add geos (UK, DE),
  then a retainer for dedicated pages.

## 21. One-screen cheat sheet
**Gymshark** · CR Fit 70 · organic-native giant (TikTok 6.7M, IG 8.6M), YT Shorts thin, 13 "gymshark" TikTok
handles unmanaged · hiring an Influencer Marketing Manager · FY25 £646M revenue, PBT £7M.
**Wedge:** scale, control and measure the demand that already exists, around drops and the US push.
**Best analogue:** the Sartain dedicated-page brief ($1.52 eCPM) plus Clip Farm's consumer roster.
**Ask:** Shorts gap · who runs the gymshark* accounts · creator-ops bottleneck. **Anchor:** $25K ≈ 15M paid-for
views at $1.50. **Don't say:** "your organic is weak".

## 22. Unknowns to confirm on the call
US vs UK audience split · whether any gymshark* accounts are managed · rights to athlete footage · current agency
relationships · paid CPM baseline · who owns the CR decision.

## 23. Sources
[1] FashionUnited, "Gymshark reports 13th consecutive year of sales growth in FY25", 2026-03-12. https://fashionunited.uk/news/business/gymshark-reports-13th-consecutive-year-of-sales-growth-in-fy25/2026031286834
[2] Chain Store Age, 2026-04-13. https://chainstoreage.com/athleticwear-brand-gymshark-open-its-first-ever-gym-heres-where
[3] TikTok official embed card, read 2026-10-08. https://www.tiktok.com/embed/@gymshark · [3b] TikTok oEmbed checks, https://www.tiktok.com/oembed?url=https://www.tiktok.com/@HANDLE
[4] Instagram public profile, read 2026-10-08. https://www.instagram.com/gymshark/
[5] YouTube channel pages /videos and /shorts, read 2026-10-08. https://www.youtube.com/@Gymshark
[6] CR campaign page, Michael Sartain's Clipping Army. https://contentrewards.com/discover/86842687-ba2b-4638-a024-995dcf3d25a3
[7] CR org page, Clipping Culture. https://contentrewards.com/c/clipping-culture
[8] Greenhouse job board API. https://boards-api.greenhouse.io/v1/boards/gymshark/jobs · role: https://job-boards.eu.greenhouse.io/gymshark/jobs/4948518101
[9] DNS TXT for gymshark.com. https://dns.google/resolve?name=gymshark.com&type=TXT
[10] SGI Europe, "Gymshark founder in talks to buy back stake from GA" (undated; cites FT). https://www.sgieurope.com/corporate/gymshark-founder-in-talks-to-buy-back-stake-from-ga/122043.article
[11] Glossy, 2025-05-02. https://www.glossy.co/fashion/exclusive-amid-growing-pains-gymshark-opens-first-us-store/
[12] Fitness Volt, 2025-07-22. https://fitnessvolt.com/sam-sulek-chris-bumstead-david-laid-workout
[13] Athletech News, 2023-03-08. https://athletechnews.com/?p=93621
[14] Meta Ad Library keyword search (US, active), 2026-10-08. https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=gymshark
[15] CR Brand Terms §12 (updated 2026-10-04). https://contentrewards.com/brands-terms
[16] WHOOP Podcast 295, Ben Francis. https://www.whoop.com/thelocker/podcast-295-ben-francis-mbe-the-mission-to-create-a-100-year-brand
[17] CR Discover feed, 2026-10-08. https://contentrewards.com/c/discover
[18] CR org page, Clip Farm. https://contentrewards.com/c/clip-farm
[19] CR agencies FAQ. https://contentrewards.com/agencies
