/**
 * vote.js — Vote for climate justice using Playwright (Node.js)
 *
 * Usage:
 *   node vote.js --config_section <section> [--config_file <path>]
 *
 * Config file: vote_config.json (JSON, same structure as the Python YAML config).
 * Each top-level key is a config section.  Supported keys per section:
 *
 *   link_website          {string}   URL of the page to vote on  (required)
 *   voting_selector       {string}   CSS selector for the vote option
 *   voting_selectors      {string[]} Multiple CSS selectors (tried in order)
 *   voting_xpath          {string}   XPath for the vote option
 *   voting_xpaths         {string[]} Multiple XPaths (tried in order)
 *   sending_selector      {string}   CSS selector for the submit button
 *   sending_selectors     {string[]} Multiple CSS selectors
 *   sending_xpath         {string}   XPath for the submit button
 *   sending_xpaths        {string[]} Multiple XPaths
 *   cookies               {boolean}  true if a cookie-consent banner must be clicked
 *   cookies_selector      {string}   CSS selector for the accept-cookies button
 *   cookies_selectors     {string[]} Multiple CSS selectors
 *   cookies_xpath         {string}   XPath for the accept-cookies button
 *   cookies_xpaths        {string[]} Multiple XPaths
 *   deleting_cookies      {boolean}  (default true) use a fresh browser context each vote
 *   extreme_mode          {boolean}  (default false) skip random delays
 */

"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const DEFAULT_CONFIG_PATH = path.join(__dirname, "vote_config.json");
const MAX_ERRORS = 10;

// ---------------------------------------------------------------------------
// Config helpers
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = argv.slice(2);
  const result = {};
  for (let i = 0; i < args.length; i++) {
    const key = args[i].replace(/^--?/, "");
    const value = args[i + 1] && !args[i + 1].startsWith("-") ? args[++i] : true;
    result[key] = value;
  }
  return result;
}

function loadConfigSection(configFile, sectionName) {
  if (!fs.existsSync(configFile)) {
    throw new Error(`Config file not found: ${configFile}`);
  }
  const raw = fs.readFileSync(configFile, "utf8");
  const config = JSON.parse(raw);
  if (!(sectionName in config)) {
    throw new Error(`Config section '${sectionName}' not found in ${configFile}.`);
  }
  const section = config[sectionName];
  if (typeof section !== "object" || Array.isArray(section) || section === null) {
    throw new Error(`Config section '${sectionName}' must be a JSON object.`);
  }
  return section;
}

/**
 * Build an ordered, deduplicated list of { by, value } locator objects for
 * a given key prefix (e.g. "voting", "sending", "cookies").
 *
 * Reads four keys from configValues:
 *   <prefix>_selector   – single CSS selector
 *   <prefix>_selectors  – array of CSS selectors
 *   <prefix>_xpath      – single XPath
 *   <prefix>_xpaths     – array of XPaths
 */
function getLocators(configValues, prefix) {
  const locators = [];
  const seen = new Set();

  function add(by, value) {
    if (!value) return;
    const key = `${by}::${value}`;
    if (!seen.has(key)) {
      seen.add(key);
      locators.push({ by, value });
    }
  }

  const single = configValues[`${prefix}_selector`];
  if (single) add("css", single);

  const multi = configValues[`${prefix}_selectors`];
  if (multi !== undefined && multi !== null) {
    if (!Array.isArray(multi))
      throw new Error(`'${prefix}_selectors' must be an array.`);
    for (const s of multi) add("css", s);
  }

  const singleXp = configValues[`${prefix}_xpath`];
  if (singleXp) add("xpath", singleXp);

  const multiXp = configValues[`${prefix}_xpaths`];
  if (multiXp !== undefined && multiXp !== null) {
    if (!Array.isArray(multiXp))
      throw new Error(`'${prefix}_xpaths' must be an array.`);
    for (const x of multiXp) add("xpath", x);
  }

  if (locators.length === 0) {
    throw new Error(
      `Missing locator for '${prefix}'. Add one of: ` +
        `'${prefix}_selector', '${prefix}_selectors', '${prefix}_xpath', '${prefix}_xpaths'.`
    );
  }
  return locators;
}

// ---------------------------------------------------------------------------
// Browser helpers
// ---------------------------------------------------------------------------

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Try to click a locator in the given Playwright Frame.
 * Returns true on success, false on timeout / not-found.
 */
async function tryClickInFrame(frame, locator, timeoutMs) {
  try {
    const { by, value } = locator;
    const selector = by === "xpath" ? `xpath=${value}` : value;
    await frame.click(selector, { timeout: timeoutMs });
    return true;
  } catch {
    return false;
  }
}

/**
 * Try every locator in the main frame and, as fallback, in all iframes.
 * Returns 0 on success, 1 on failure.
 */
async function clickWithFallback(page, locators, timeoutMs = 12_000) {
  // 1. Try in the main frame.
  for (const loc of locators) {
    if (await tryClickInFrame(page.mainFrame(), loc, timeoutMs)) {
      console.log(`Clicked via ${loc.by}: ${loc.value}`);
      return 0;
    }
  }

  // 2. Try inside each iframe.
  const frames = page.frames();
  for (const frame of frames) {
    if (frame === page.mainFrame()) continue;
    for (const loc of locators) {
      if (await tryClickInFrame(frame, loc, timeoutMs)) {
        console.log(`Clicked via iframe locator ${loc.by}: ${loc.value}`);
        return 0;
      }
    }
  }

  console.log("Element not found/clickable for all fallback locators.");
  for (const loc of locators) {
    console.log(`  Tried ${loc.by}: ${loc.value}`);
  }
  console.log(`  Current URL: ${page.url()}`);
  return 1;
}

// ---------------------------------------------------------------------------
// Main voting loop
// ---------------------------------------------------------------------------

async function process(options) {
  const {
    linkWebsite,
    votingLocators,
    sendingLocators,
    cookies = false,
    cookiesLocators = [],
    deletingCookies = true,
    extremeMode = false,
  } = options;

  const browser = await chromium.launch({ headless: false });
  let errors = 0;

  while (true) {
    // Each iteration gets a fresh browser context (= no stored cookies / storage).
    const context = deletingCookies
      ? await browser.newContext()
      : browser.contexts()[0] ?? (await browser.newContext());

    const page = await context.newPage();

    try {
      console.log(`Opening ${linkWebsite} …`);
      await page.goto(linkWebsite, { waitUntil: "domcontentloaded" });

      if (!extremeMode) await sleep(randInt(1_000, 2_000));

      // Accept cookie banner if needed.
      if (cookies) {
        console.log("Accepting cookies…");
        const errCookies = await clickWithFallback(page, cookiesLocators);
        errors += errCookies;
        if (!extremeMode) await sleep(randInt(500, 1_500));
      }

      // Cast vote.
      console.log("Voting for climate justice…");
      const errVote = await clickWithFallback(page, votingLocators);
      if (errVote) {
        errors += errVote;
        if (errors > MAX_ERRORS)
          throw new Error(`More than ${MAX_ERRORS} errors occurred during execution.`);
        await context.close();
        if (!extremeMode) await sleep(randInt(5_000, 10_000));
        continue;
      }

      // Submit vote.
      if (!extremeMode) await sleep(randInt(1_000, 3_000));
      console.log("Sending vote…");
      const errSend = await clickWithFallback(page, sendingLocators);
      errors += errSend;
    } finally {
      await context.close();
    }

    if (errors > MAX_ERRORS)
      throw new Error(`More than ${MAX_ERRORS} errors occurred during execution.`);
    if (!extremeMode) await sleep(randInt(5_000, 10_000));
  }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

async function main() {
  const args = parseArgs(process.argv);

  const configSection = args["config_section"];
  if (!configSection) {
    console.error(
      "Usage: node vote.js --config_section <section> [--config_file <path>]"
    );
    process.exit(1);
  }
  const configFile = args["config_file"] || DEFAULT_CONFIG_PATH;

  const cfg = loadConfigSection(configFile, configSection);

  const linkWebsite = cfg["link_website"];
  if (!linkWebsite) throw new Error("'link_website' is required in the config section.");

  const hasCookies = Boolean(cfg["cookies"]);
  const votingLocators = getLocators(cfg, "voting");
  const sendingLocators = getLocators(cfg, "sending");
  const cookiesLocators = hasCookies ? getLocators(cfg, "cookies") : [];
  const deletingCookies = cfg["deleting_cookies"] !== false; // default true
  const extremeMode = Boolean(cfg["extreme_mode"]);

  console.log(`Loaded config section '${configSection}'. Voting for climate justice. — Enjoy!`);

  await process({
    linkWebsite,
    votingLocators,
    sendingLocators,
    cookies: hasCookies,
    cookiesLocators,
    deletingCookies,
    extremeMode,
  });
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err.message);
    process.exit(1);
  });
}

// Export helpers for testing.
module.exports = { parseArgs, loadConfigSection, getLocators };
