# Changelog

## 0.2.5 (2026-10-08)
- Cold-prospect example run: `examples/oura-2026-10-08/` (no CR or clipping history).
- Cheat sheet "One campaign idea" replaced with a demo-ready campaign spec: goal, named footage, example hooks, rules, payout, test budget and view math, win/kill thresholds, the live CR page to open on screen, and a close question.
- SKILL.md: hard gate that rejects vague campaign ideas.

## 0.2.4 (2026-10-08)
- Full end-to-end run on Boxabl committed as `examples/boxabl-2026-10-08/` (dossier, cheat sheet, ledger, raw script output).
- ledger.py verify: quote matching now strips React `<!-- -->` comment nodes, bidi isolation marks (U+2066/2069) and HTML entities. Before this, live Content Rewards numbers like "$13.15" failed verification. Regression test added.
- The verifier caught live drift during the run (campaign views 33.9M → 34M within the hour); claims were updated to the re-fetched values.

## 0.2.3: first fully live scripted run (2026-10-08, SCRIPTS mode 9/9)
- Fixed: Wikidata 429. Wikimedia throttles browser-spoofed user agents, so the descriptive tool UA is now used.
- Fixed: CR campaign budget parsing ("$" split from the number), participants ("/ 21") and a derived effective CPM.
- The CR org page campaign list loads client-side, so the output now says to read it with the browser or WebFetch.
- Podcast results are ranked by name match. Wayback is labelled as domain age, not brand age.

## 0.2.2: stress test (see examples/STRESS-TEST-2026-10-08.md)
- Live-captured replay harness and regression tests (Liquid Death, Boxabl, edge cases).
- Fixed: Wikidata single-item fields (HQ) now resolve; confirmed Klaviyo token and added Zapier, MailerLite and Airtable; a Greenhouse board with 0 roles is reported correctly; better handle-variant ordering; `exists_but_card_unreachable` in the constellation output.

## 0.2.1
- `social_probe.py tiktok-history`: opt-in full dated TikTok history via yt-dlp (30/90/365-day posts, median views, top posts).
- Browser mode (recipes §8b): the rep's own browser at human pace for TikTok and IG search, X search and ad libraries.
- Maigret restored as optional, for brand handles only.
- Playbook and SKILL.md wording made neutral.

## 0.2.0 (2026-10-08): underground-alpha pass
Based on 8 more research agents (skill hubs, OSS scraping, OSS enrichment, OSS social tools, deep-research agents,
the clipping supply side, MCP leaderboards, GitHub trend mining). The main session verified the key findings.
- NEW `identity.py`: keyless Wikidata lookup for official website, X/IG/TikTok/YouTube/Facebook handles, founding
  year, HQ and founders. Verified live on Gymshark.
- NEW TikTok video dating: `id >> 32` = creation time. The embed card now yields last-post date, posts per week and
  median views over the last 30 days, still keyless.
- NEW `moments.py`: heuristic clippable-moments-per-hour estimate from any VTT, SRT or TXT transcript.
- NEW optional BuiltWith-class tech detection via projectdiscovery `httpx -td` in `company_signals.py`.
- Ledger: verdicts (supported/unverified/inference/derived), URL-normalized source dedup, `[Sn]`/`[Cnnn]`
  citation contract and a `lint` command (patterns from morphic, local-deep-research and node-DeepResearch).
- Recipes: Crawl4AI and self-hosted Jina Reader extract tiers, a SearXNG JSON search rung, the official Jina MCP,
  Overture Places for SMB handles, the verified ScrapeCreators free tier (100 plus up to 7,000).
- Playbook: the supply-side section (clipper toolchain, volume and quality expectations, geo dubbing, faceless
  supply, red flags).
- Security: ClawHub malware context, a SkillSpector release gate, Playwright `--isolated`.
- Removed: Maigret/Sherlock (account enumeration).
- New `references/mcp-powerups.md`.

## 0.1.0 (2026-10-08)
First release.
