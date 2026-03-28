# Fridays Codebase
Codebase for Fridays Niederösterreich

## Existing files
- save email-adresses from excel file to list
- vote for climate justice (including cookie handling and cookie deletion)
- send personal emails (exists, will be there in some time)

## vote_for_climate_justice

Automated Selenium script that votes on websites for climate justice.

### Usage

```bash
python vote_for_climate_justice/Kraxenweg_web.py \
  -config_section windkraft_zwettl_meinbezirk \
  [-config_file vote_for_climate_justice/vote_config.yaml]
```

### Configuration (`vote_config.yaml`)

Each top-level key is a *config section* that describes one voting target.
The following keys are supported:

| Key | Required | Description |
|-----|----------|-------------|
| `link_website` | ✓ | URL of the page to vote on |
| `voting_selector` / `voting_selectors` / `voting_xpath` / `voting_xpaths` | ✓ | Locator(s) for the vote radio-button / option |
| `sending_selector` / `sending_selectors` / `sending_xpath` / `sending_xpaths` | ✓ | Locator(s) for the submit / send button |
| `cookies` | – | `true` if the site shows a cookie-consent banner |
| `cookies_selector` / `cookies_selectors` / `cookies_xpath` / `cookies_xpaths` | if `cookies: true` | Locator(s) for the cookie-accept button |
| `deleting_cookies` | – | `true` (default) to delete the browser profile after each vote so the site cannot recognise a returning voter |
| `extreme_mode` | – | `true` to skip random delays between votes |

The script uses all provided locators as fallbacks in order and also searches inside `<iframe>` elements automatically.

### Running the tests

```bash
cd vote_for_climate_justice
python -m pytest test_Kraxenweg_web.py -v
```
