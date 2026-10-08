# How a Content Rewards rep installs and runs it

## Install (pick one, once)

**A. Claude Code (terminal, best results).** Paste these two lines into Claude Code:
```
/plugin marketplace add poseidon-jpg/cr-prospect-intel
/plugin install content-rewards-prospect-intel@cr-prospect-intel
```


**B. Claude.ai / Cowork (no terminal).**
1. Download `content-rewards-prospect-intel-skill-v0.2.4.zip`.
2. Claude → Settings → Capabilities → Skills → Upload skill → pick the zip.
3. On the same page, under Code execution, set Domain allowlist to **All domains**. Without it the scripts can't reach TikTok, YouTube or contentrewards.com, and the skill falls back to slower web search.

## Run

The rep types one line:
```
/prospect Paolo Tiramani, paolo@boxabl.com, Boxabl
```
or, in plain English: *"Prep me for my call with Paolo Tiramani at Boxabl."*

## What they see (real run, 2026-10-08, ~12 minutes)

```
● Checking the environment…
  mode: SCRIPTS (9/9 endpoints reachable) · yt-dlp found · no API keys (optional)

● Step 1: identity
  Boxabl → Wikidata Q115704993 "American construction company", Las Vegas
  Paolo Tiramani = founder & co-CEO (Inman, 2026-07-20) ✓

● Step 2: research, 8 facets in parallel
  company   DNS: HubSpot, SendGrid, Meta Business Manager, Stripe, M365 · domain since 2013
  news      Nasdaq listing 07-20 at $3.5B · "shares fall 50%" 07-23 · Server Pod 08-20
  tiktok    @boxabl 114.4K followers · last post 08-24 · 0 posts in 30 days
  youtube   @Boxabl ~2 Shorts/week · best 50,950 views (Casita Tour)
  constellation  25 handles checked → 12 exist → 4 likely affiliated, 3 possible
  podcasts  Tiramani: 7 guest spots 2021-2023, none recent
  CR library  MATCH: "Boxabl Official Clipping" by Clip Farm ← already a customer
            $0.50/1K · $19,968 of $85,000 spent · 836 clippers · ~34M views

● Step 3: verifying evidence
  22 claims · 17 quotes re-fetched and confirmed live · 5 derived · 0 failures
  (the verifier caught the view count moving from 33.9M to 34M mid-run and forced an update)

● Step 4: writing
  ✓ dossier.md      (23 sections)
  ✓ cheat-sheet.md  (one screen, for the call)
  ✓ citation lint: pass
```

Then the cheat sheet appears in the chat and both files land in their folder. The real output is in `boxabl-cheat-sheet.md` and `boxabl-dossier.md`.
