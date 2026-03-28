/**
 * test_vote.js — Unit tests for vote.js helpers (no browser required).
 *
 * Run with:
 *   node --test test_vote.js
 */

"use strict";

const { test, describe } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const { parseArgs, loadConfigSection, getLocators } = require("./vote.js");

// ---------------------------------------------------------------------------
// parseArgs
// ---------------------------------------------------------------------------

describe("parseArgs", () => {
  test("parses --config_section", () => {
    const args = parseArgs(["node", "vote.js", "--config_section", "my_section"]);
    assert.equal(args["config_section"], "my_section");
  });

  test("parses --config_file", () => {
    const args = parseArgs([
      "node",
      "vote.js",
      "--config_section",
      "s",
      "--config_file",
      "/tmp/cfg.json",
    ]);
    assert.equal(args["config_file"], "/tmp/cfg.json");
  });

  test("returns empty object for no args", () => {
    const args = parseArgs(["node", "vote.js"]);
    assert.deepEqual(args, {});
  });

  test("supports single-dash flags", () => {
    const args = parseArgs(["node", "vote.js", "-config_section", "x"]);
    assert.equal(args["config_section"], "x");
  });
});

// ---------------------------------------------------------------------------
// loadConfigSection
// ---------------------------------------------------------------------------

describe("loadConfigSection", () => {
  function writeTmp(content) {
    const file = path.join(os.tmpdir(), `vote_test_${Date.now()}.json`);
    fs.writeFileSync(file, JSON.stringify(content), "utf8");
    return file;
  }

  test("loads a valid section", () => {
    const file = writeTmp({ my_section: { link_website: "https://example.com" } });
    const cfg = loadConfigSection(file, "my_section");
    assert.equal(cfg["link_website"], "https://example.com");
  });

  test("throws when file is missing", () => {
    assert.throws(
      () => loadConfigSection("/nonexistent/path.json", "x"),
      /Config file not found/
    );
  });

  test("throws when section is missing", () => {
    const file = writeTmp({ other: {} });
    assert.throws(
      () => loadConfigSection(file, "missing_section"),
      /not found/
    );
  });

  test("throws when section is an array (not an object)", () => {
    const file = writeTmp({ bad: [1, 2, 3] });
    assert.throws(
      () => loadConfigSection(file, "bad"),
      /must be a JSON object/
    );
  });

  test("throws when section is a string (not an object)", () => {
    const file = writeTmp({ bad: "just a string" });
    assert.throws(
      () => loadConfigSection(file, "bad"),
      /must be a JSON object/
    );
  });
});

// ---------------------------------------------------------------------------
// getLocators
// ---------------------------------------------------------------------------

describe("getLocators", () => {
  test("returns single CSS selector", () => {
    const locators = getLocators({ vote_selector: "button.vote" }, "vote");
    assert.deepEqual(locators, [{ by: "css", value: "button.vote" }]);
  });

  test("returns single XPath", () => {
    const locators = getLocators({ vote_xpath: "//button" }, "vote");
    assert.deepEqual(locators, [{ by: "xpath", value: "//button" }]);
  });

  test("returns multiple selectors", () => {
    const locators = getLocators(
      { vote_selectors: ["a.vote", "button.vote"] },
      "vote"
    );
    assert.deepEqual(locators, [
      { by: "css", value: "a.vote" },
      { by: "css", value: "button.vote" },
    ]);
  });

  test("returns multiple xpaths", () => {
    const locators = getLocators(
      { vote_xpaths: ["//a", "//button"] },
      "vote"
    );
    assert.deepEqual(locators, [
      { by: "xpath", value: "//a" },
      { by: "xpath", value: "//button" },
    ]);
  });

  test("deduplicates identical locators", () => {
    const locators = getLocators(
      { vote_selector: "button", vote_selectors: ["button", "input"] },
      "vote"
    );
    assert.equal(locators.filter((l) => l.value === "button").length, 1);
    assert.ok(locators.some((l) => l.value === "input"));
  });

  test("preserves order: selector → selectors → xpath → xpaths", () => {
    const locators = getLocators(
      {
        vote_selector: "a",
        vote_selectors: ["b"],
        vote_xpath: "//c",
        vote_xpaths: ["//d"],
      },
      "vote"
    );
    assert.deepEqual(locators, [
      { by: "css", value: "a" },
      { by: "css", value: "b" },
      { by: "xpath", value: "//c" },
      { by: "xpath", value: "//d" },
    ]);
  });

  test("throws when no locator is provided", () => {
    assert.throws(() => getLocators({}, "vote"), /Missing locator/);
  });

  test("throws when selectors is not an array", () => {
    assert.throws(
      () => getLocators({ vote_selectors: "button" }, "vote"),
      /must be an array/
    );
  });

  test("throws when xpaths is not an array", () => {
    assert.throws(
      () => getLocators({ vote_xpaths: "//button" }, "vote"),
      /must be an array/
    );
  });

  test("skips empty/null values in arrays", () => {
    const locators = getLocators(
      { vote_selectors: [null, "", "button"], vote_xpath: "//x" },
      "vote"
    );
    assert.ok(!locators.some((l) => l.value === "" || l.value === null));
    assert.ok(locators.some((l) => l.value === "button"));
  });

  test("skips null single selector", () => {
    const locators = getLocators({ vote_selector: null, vote_xpath: "//x" }, "vote");
    assert.deepEqual(locators, [{ by: "xpath", value: "//x" }]);
  });
});
