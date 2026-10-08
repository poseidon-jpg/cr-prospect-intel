# Scoring rubrics

Every score shows its sub-scores and the evidence for each one. These scores are judgment aids, not measurements.
Round to the nearest 5 and never imply false precision.

## 1. Organic Distribution Maturity (0-100)

| Dimension | Points | 0 looks like | Full points looks like |
|---|---|---|---|
| Owned consistency | 15 | no posts in 30 days | 4+ posts a week on the main platforms |
| Creative diversity | 10 | one format | 4+ archetypes (founder, demo, UGC, meme, education) |
| Creator participation | 15 | none visible | many creators posting, paid-partnership labels, an ambassador program |
| Distributed or clip accounts | 15 | no constellation | several LIKELY-affiliated accounts with real views |
| Cross-platform coverage | 10 | one platform | TikTok, IG, YouTube Shorts, X active |
| Founder or expert leverage | 10 | a faceless brand | the founder is a recurring face with strong clips |
| Audience-content fit | 10 | comments off-topic or dead | comments show purchase intent and the brand's own vocabulary |
| Recent momentum | 15 | flat or declining | a rising median, recent breakouts |

A brand with 2M followers and 3 weak posts a month can score low. A brand with 50K followers and a 40-account
clip network can score high.

## 2. Content Supply, Current Distribution, Distribution Gap

- **Content Supply (0-100):** hours of long-form (podcast, YouTube, livestream, events) plus founder media plus
  UGC library plus product footage. Bands: LOW <25, MEDIUM 25-49, HIGH 50-79, EXTREME 80+. Example: a weekly
  1-hour podcast for 2 years (about 100 hours) plus a founder on 20 guest shows rates HIGH to EXTREME.
- **Current Distribution (0-100):** how much of that supply actually reaches short-form feeds (clip volume,
  dedicated pages, cadence, reach).
- **Distribution Gap = Supply − Distribution.** A gap of +30 or more is a strong CR signal: they have the fuel but
  not the engine. A negative gap means they already distribute more than they produce, so lead with UGC creation
  or creative supply.

## 3. Cultural Surface Area (qualitative)

Count the independent nodes carrying the brand story: owned social, creators, customers, fan or theme pages, clip
pages, podcasts, press, memes, affiliates, athletes, employees, communities (Reddit, Discord). Report it as
"N of 12 node types active", with examples, and say which nodes are missing. This is a framework for the
conversation, not a metric to defend.

## 4. Content Rewards Fit (0-100)

| Driver | Points |
|---|---|
| Distribution gap or organic opportunity | 20 |
| Source material available (or easy to create) | 15 |
| Category fit with creator-native short-form (CR live categories: entertainment, music, personal brand, tech, apps, gaming, sports, finance, crypto, podcasts, consumer brands, health and wellness) | 15 |
| Narrative opportunity (something worth saying many ways) | 10 |
| A dated catalyst within 90 days | 10 |
| Budget signals (funding, ad volume, team size, price points) | 10 |
| Existing creator or influencer spend to redirect | 10 |
| Measurable outcome available (app, codes, store, search) | 10 |

Subtract up to 20 for blockers: heavily regulated claims (health, finance) that creators can't make freely,
footage they don't own the rights to, brand-safety sensitivity, or no consumer audience. Bands: 75+ high, 50-74
medium, below 50 low. Low fit means say so and suggest what would change it.

## 5. Account constellation affiliation (per account)

This is implemented in `scripts/social_probe.py score_candidate`.

| Signal | Points |
|---|---|
| Handle contains the brand core (or is very similar, ≥0.75) | 15 (10) |
| Bio tags @officialhandle or the brand domain (CR briefs often require this) | 30 |
| Bio mentions the brand name | 15 |
| ≥50% of recent captions mention the brand or @handle (≥20%: 12) | 25 |
| Caption template overlap with another candidate, Jaccard ≥0.25 (≥0.10: 8) | 20 |

Labels: ≥70 LIKELY AFFILIATED · 40-69 POSSIBLY AFFILIATED · 1-39 NAME MATCH ONLY · 0 UNRELATED.
The official handle is always 100. If an unverified display name copies the brand exactly, flag it as a possible
fan page or impersonation and check it manually.

The weights are heuristics from coordinated-behavior research (CooRnet's link-sharing coordination and the
disinfo.eu CIB detection tree). Recalibrate them after labelling 20+ real brands. Always present affiliation
as evidence, not as a statement of who runs an account.

## 6. Identity Confidence (0-100)

+40 work-email domain matches the company site · +20 name and title found on a company page or the person's own
profile · +15 a second independent source (press, podcast, talk) · +15 the photo or role is consistent across
sources · +10 no namesake conflict. Cap at 60 for free-mail addresses without corroboration.
