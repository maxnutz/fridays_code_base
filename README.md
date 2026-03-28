# Fridays Codebase
Codebase for Fridays Niederösterreich

## Existing files
- save email-adresses from excel file to list
- vote for climate justice (two independent scripts — Python/Selenium and Node.js/Playwright)
- send personal emails (exists, will be there in some time)

---

## vote_for_climate_justice (Python · Selenium)

Automated Selenium script that votes on websites for climate justice.

### Usage

```bash
python vote_for_climate_justice/Kraxenweg_web.py \
  -config_section windkraft_zwettl_meinbezirk \
  [-config_file vote_for_climate_justice/vote_config.yaml]
```

### Configuration (`vote_config.yaml`)

Each top-level key is a *config section* that describes one voting target.

| Key | Required | Description |
|-----|----------|-------------|
| `link_website` | ✓ | URL of the page to vote on |
| `voting_selector` / `voting_selectors` / `voting_xpath` / `voting_xpaths` | ✓ | Locator(s) for the vote radio-button / option |
| `sending_selector` / `sending_selectors` / `sending_xpath` / `sending_xpaths` | ✓ | Locator(s) for the submit / send button |
| `cookies` | – | `true` if the site shows a cookie-consent banner |
| `cookies_selector` / `cookies_selectors` / `cookies_xpath` / `cookies_xpaths` | if `cookies: true` | Locator(s) for the cookie-accept button |
| `deleting_cookies` | – | `true` (default) to delete the browser profile after each vote so the site cannot recognise a returning voter |
| `extreme_mode` | – | `true` to skip random delays between votes |

### Running the Python tests

```bash
cd vote_for_climate_justice
python -m pytest test_Kraxenweg_web.py -v
```

---

## vote_playwright (Node.js · Playwright)

A new, independent voting script written in **JavaScript / Node.js** using [Playwright](https://playwright.dev/).  
It provides the same features as the Python script but runs Chromium by default.

### Requirements

- Node.js ≥ 18
- `npm install` inside `vote_playwright/`

### Installation

```bash
cd vote_playwright
npm install
```

### Usage

```bash
node vote_playwright/vote.js \
  --config_section windkraft_zwettl_meinbezirk \
  [--config_file vote_playwright/vote_config.json]
```

### Configuration (`vote_config.json`)

Same structure as the Python YAML config, but in JSON format.

| Key | Required | Description |
|-----|----------|-------------|
| `link_website` | ✓ | URL of the page to vote on |
| `voting_selector` / `voting_selectors` / `voting_xpath` / `voting_xpaths` | ✓ | Locator(s) for the vote option |
| `sending_selector` / `sending_selectors` / `sending_xpath` / `sending_xpaths` | ✓ | Locator(s) for the submit button |
| `cookies` | – | `true` if a cookie-consent banner must be dismissed |
| `cookies_selector` / `cookies_selectors` / `cookies_xpath` / `cookies_xpaths` | if `cookies: true` | Locator(s) for the accept-cookies button |
| `deleting_cookies` | – | `true` (default) — uses a fresh browser context per vote so the site cannot track returning voters |
| `extreme_mode` | – | `true` to skip random delays between votes |

### Running the Node.js tests

```bash
cd vote_playwright
node --test test_vote.js
```
