"""Unit tests for Kraxenweg_web.py voting script."""

import argparse
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import pytest
import tempfile
import yaml

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import Kraxenweg_web as kw


# ---------------------------------------------------------------------------
# get_locators
# ---------------------------------------------------------------------------

class TestGetLocators:
    def test_single_selector(self):
        config = {"vote_selector": "button.vote"}
        result = kw.get_locators(config, "vote")
        assert result == [(By.CSS_SELECTOR, "button.vote")]

    def test_single_xpath(self):
        config = {"vote_xpath": "//button[@class='vote']"}
        result = kw.get_locators(config, "vote")
        assert result == [(By.XPATH, "//button[@class='vote']")]

    def test_multiple_selectors(self):
        config = {"vote_selectors": ["a.vote", "button.vote"]}
        result = kw.get_locators(config, "vote")
        assert result == [(By.CSS_SELECTOR, "a.vote"), (By.CSS_SELECTOR, "button.vote")]

    def test_multiple_xpaths(self):
        config = {"vote_xpaths": ["//a", "//button"]}
        result = kw.get_locators(config, "vote")
        assert result == [(By.XPATH, "//a"), (By.XPATH, "//button")]

    def test_combined_selector_and_xpath(self):
        config = {"vote_selector": "button", "vote_xpath": "//button"}
        result = kw.get_locators(config, "vote")
        assert (By.CSS_SELECTOR, "button") in result
        assert (By.XPATH, "//button") in result

    def test_deduplication(self):
        config = {
            "vote_selector": "button",
            "vote_selectors": ["button", "input"],
        }
        result = kw.get_locators(config, "vote")
        assert result.count((By.CSS_SELECTOR, "button")) == 1
        assert (By.CSS_SELECTOR, "input") in result

    def test_missing_locator_raises_key_error(self):
        with pytest.raises(KeyError, match="Missing locator"):
            kw.get_locators({}, "vote")

    def test_selectors_not_list_raises_value_error(self):
        config = {"vote_selectors": "button"}
        with pytest.raises(ValueError, match="must be a list"):
            kw.get_locators(config, "vote")

    def test_xpaths_not_list_raises_value_error(self):
        config = {"vote_xpaths": "//button"}
        with pytest.raises(ValueError, match="must be a list"):
            kw.get_locators(config, "vote")

    def test_empty_selector_is_skipped(self):
        config = {"vote_selector": "", "vote_xpath": "//button"}
        result = kw.get_locators(config, "vote")
        assert result == [(By.XPATH, "//button")]

    def test_none_value_is_skipped(self):
        config = {"vote_selector": None, "vote_xpath": "//button"}
        result = kw.get_locators(config, "vote")
        assert result == [(By.XPATH, "//button")]

    def test_order_is_selector_selectors_xpath_xpaths(self):
        config = {
            "vote_selector": "a",
            "vote_selectors": ["b"],
            "vote_xpath": "//c",
            "vote_xpaths": ["//d"],
        }
        result = kw.get_locators(config, "vote")
        assert result == [
            (By.CSS_SELECTOR, "a"),
            (By.CSS_SELECTOR, "b"),
            (By.XPATH, "//c"),
            (By.XPATH, "//d"),
        ]


# ---------------------------------------------------------------------------
# load_config_section
# ---------------------------------------------------------------------------

class TestLoadConfigSection:
    def _write_config(self, content: str) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(content)
            return fh.name

    def test_loads_valid_section(self):
        path = self._write_config(
            textwrap.dedent(
                """\
                my_section:
                  link_website: https://example.com
                  cookies: false
                """
            )
        )
        result = kw.load_config_section(path, "my_section")
        assert result["link_website"] == "https://example.com"
        assert result["cookies"] is False

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            kw.load_config_section("/nonexistent/path.yaml", "x")

    def test_missing_section_raises(self):
        path = self._write_config("other_section:\n  key: val\n")
        with pytest.raises(KeyError, match="not found"):
            kw.load_config_section(path, "missing_section")

    def test_non_dict_section_raises(self):
        path = self._write_config("bad_section:\n  - item1\n")
        with pytest.raises(ValueError, match="must contain key/value pairs"):
            kw.load_config_section(path, "bad_section")


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

class TestBuildParser:
    def test_requires_config_section(self):
        parser = kw.build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parses_config_section(self):
        parser = kw.build_parser()
        args = parser.parse_args(["-config_section", "my_section"])
        assert args.config_section == "my_section"

    def test_default_config_file(self):
        parser = kw.build_parser()
        args = parser.parse_args(["-config_section", "x"])
        assert args.config_file == str(kw.DEFAULT_CONFIG_PATH)

    def test_custom_config_file(self):
        parser = kw.build_parser()
        args = parser.parse_args(["-config_section", "x", "-config_file", "/tmp/cfg.yaml"])
        assert args.config_file == "/tmp/cfg.yaml"


# ---------------------------------------------------------------------------
# click_element
# ---------------------------------------------------------------------------

class TestClickElement:
    def _make_driver(self, clickable=True):
        driver = MagicMock()
        element = MagicMock()
        wait_instance = MagicMock()

        if clickable:
            wait_instance.until.return_value = element
        else:
            wait_instance.until.side_effect = TimeoutException()

        with patch("Kraxenweg_web.WebDriverWait", return_value=wait_instance):
            return driver, element, wait_instance

    def test_returns_0_on_success(self):
        driver, element, wait = self._make_driver(clickable=True)
        with patch("Kraxenweg_web.WebDriverWait", return_value=wait):
            result = kw.click_element(driver, "//button")
        assert result == 0
        element.click.assert_called_once()

    def test_returns_1_on_timeout(self):
        driver, element, wait = self._make_driver(clickable=False)
        with patch("Kraxenweg_web.WebDriverWait", return_value=wait):
            result = kw.click_element(driver, "//button")
        assert result == 1

    def test_returns_1_on_no_such_element(self):
        driver = MagicMock()
        wait = MagicMock()
        wait.until.side_effect = NoSuchElementException()
        with patch("Kraxenweg_web.WebDriverWait", return_value=wait):
            result = kw.click_element(driver, "//button")
        assert result == 1


# ---------------------------------------------------------------------------
# click_by_locator
# ---------------------------------------------------------------------------

class TestClickByLocator:
    def test_success_returns_0(self):
        driver = MagicMock()
        element = MagicMock()
        wait = MagicMock()
        wait.until.return_value = element
        with patch("Kraxenweg_web.WebDriverWait", return_value=wait):
            result = kw.click_by_locator(driver, By.CSS_SELECTOR, "button.vote")
        assert result == 0
        element.click.assert_called_once()

    def test_timeout_returns_1(self):
        driver = MagicMock()
        wait = MagicMock()
        wait.until.side_effect = TimeoutException()
        with patch("Kraxenweg_web.WebDriverWait", return_value=wait):
            result = kw.click_by_locator(driver, By.CSS_SELECTOR, "button.vote")
        assert result == 1


# ---------------------------------------------------------------------------
# click_with_fallback
# ---------------------------------------------------------------------------

class TestClickWithFallback:
    def test_success_in_top_document(self):
        driver = MagicMock()
        locators = [(By.CSS_SELECTOR, "button")]
        with patch("Kraxenweg_web._try_click_in_current_context", return_value=True):
            result = kw.click_with_fallback(driver, locators)
        assert result == 0

    def test_failure_when_nothing_clickable(self):
        driver = MagicMock()
        driver.find_elements.return_value = []
        locators = [(By.CSS_SELECTOR, "button")]
        with patch("Kraxenweg_web._try_click_in_current_context", return_value=False):
            result = kw.click_with_fallback(driver, locators)
        assert result == 1

    def test_success_in_iframe(self):
        driver = MagicMock()
        iframe = MagicMock()
        driver.find_elements.return_value = [iframe]
        locators = [(By.CSS_SELECTOR, "button")]

        responses = iter([False, True])  # top fails, iframe succeeds

        with patch(
            "Kraxenweg_web._try_click_in_current_context",
            side_effect=lambda *args, **kwargs: next(responses),
        ):
            result = kw.click_with_fallback(driver, locators)
        assert result == 0


# ---------------------------------------------------------------------------
# delete_cookies
# ---------------------------------------------------------------------------

class TestDeleteCookies:
    def test_returns_1_when_no_driver(self):
        # Make sure 'web' global is absent / None
        kw_globals = kw.__dict__
        original = kw_globals.pop("web", "ABSENT")
        try:
            result = kw.delete_cookies()
            assert result == 1
        finally:
            if original != "ABSENT":
                kw_globals["web"] = original

    def test_deletes_profile_directory(self):
        with tempfile.TemporaryDirectory() as profile_dir:
            driver = MagicMock()
            driver.capabilities = {"moz:profile": profile_dir}
            kw.__dict__["web"] = driver

            result = kw.delete_cookies()

            assert result == 0
            assert not Path(profile_dir).exists()
            assert kw.__dict__.get("web") is None
