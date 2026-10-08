# Optional MCP power-ups

The skill works with no MCP servers at all. These add depth. Install only what the rep wants, as separate
user-installed processes. We don't bundle their code, and some are AGPL.

Rules:
- Pin versions.
- Keyless first.
- Official vendor servers beat random authors. Read the code of any server with fewer than about 100 stars
  before installing it.
- Don't send prospect names to third-party hosted gateways when a local option exists.

## Keyless pack (local, stdio)

Verified current on 2026-10-08. Confirm the package names and versions before pinning.

```json
{
  "mcpServers": {
    "fetch":      { "command": "uvx", "args": ["mcp-server-fetch"] },
    "ddg-search": { "command": "uvx", "args": ["duckduckgo-mcp-server"],
                    "env": { "DDG_FETCH_RPM": "20", "DDG_CACHE_TTL": "300" } },
    "playwright": { "command": "npx", "args": ["-y", "@playwright/mcp@<pin-version>", "--isolated"] },
    "wikipedia":  { "command": "uvx", "args": ["wikipedia-mcp"] }
  }
}
```

| Server | Repo | Why |
|---|---|---|
| fetch (official) | modelcontextprotocol/servers/src/fetch | local page-to-markdown, for when the host's WebFetch refuses a site |
| ddg-search | nickclyde/duckduckgo-mcp-server (1.4k stars, MIT) | keyless search fallback with built-in rate limiting |
| playwright (Microsoft) | microsoft/playwright-mcp (36.8k, Apache-2.0) | JS pages: Meta Ad Library, TikTok Creative Center, CR pages. Use `--isolated` for a clean profile, never a logged-in one |
| wikipedia | Rudra-ravi/wikipedia-mcp (295, MIT) | founders, history and infobox facts |

## Remote keyless (vendor-run, rate-limited)

```json
{
  "mcpServers": {
    "exa":       { "type": "http", "url": "https://mcp.exa.ai/mcp" },
    "firecrawl": { "type": "http", "url": "https://mcp.firecrawl.dev/v2/mcp" },
    "jina":      { "type": "http", "url": "https://mcp.jina.ai/v1" },
    "parallel":  { "type": "http", "url": "https://search.parallel.ai/mcp" }
  }
}
```

## Prospect-type specific

- **Public companies:** SEC EDGAR. cyanheads/secedgar-mcp-server (Apache-2.0, very new, so read it first) or
  stefanoamorelli/sec-edgar-mcp (355 stars, AGPL, sidecar only). Needs an SEC User-Agent with a contact.
- **News:** cyanheads/gdelt-mcp-server (local only). GDELT returns 429 quickly, so cache and back off.
- **UK companies:** aicayzer/companies-house-mcp (MIT) with a free Companies House API key.
- **Social, keyed:** the official ScrapeCreators CLI and MCP (100 free credits, plus up to 7,000 more).

## Rejected (don't install)

| Server | Why |
|---|---|
| nuelcyoung/tiktok-mcp-server | stealth-masked headless TikTok scraping |
| zxl777/youtube-transcript-mcp | proxy fallback to evade blocks |
| string-ai, reefapi, minia2a | anti-bot or CAPTCHA bypass |
| x402 pay-per-call aggregators | unvetted, and they hide who runs the traffic |
| eliasbiondo/reddit-mcp-server | stale, and relies on the now-blocked anonymous Reddit JSON |
| Agent-Reach cookie branches | burner-account cookie scraping; only its zero-config tier is acceptable |
