from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import shutil
import tempfile
from pathlib import Path
import argparse
import yaml
from typing import List, Tuple


DEFAULT_CONFIG_PATH = Path(__file__).with_name("vote_config.yaml")


def open_website(link_website):
    try:
        web = webdriver.Firefox()
        web.implicitly_wait(5)
        web.get(link_website)
        time.sleep(1)
        return web
    except Exception as exc:
        raise RuntimeError(f"Website not reachable: {exc}") from exc



def click_element(web, element_x_path, timeout: int = 12):
    try:
        wait = WebDriverWait(web, timeout)
        element = wait.until(
            EC.element_to_be_clickable((By.XPATH, element_x_path))
        )
        element.click()
        return 0
    except (TimeoutException, NoSuchElementException):
        print(f"Element not found/clickable for XPath: {element_x_path}")
        print(f"Current URL: {web.current_url}")
        print(f"Page title: {web.title}")
        return 1


def get_locators(config_values: dict, key_prefix: str) -> List[Tuple[str, str]]:
    locators: List[Tuple[str, str]] = []

    selector_key = f"{key_prefix}_selector"
    selectors_key = f"{key_prefix}_selectors"
    xpath_key = f"{key_prefix}_xpath"
    xpaths_key = f"{key_prefix}_xpaths"

    if selector_key in config_values and config_values[selector_key]:
        locators.append((By.CSS_SELECTOR, config_values[selector_key]))

    if selectors_key in config_values and config_values[selectors_key]:
        selectors = config_values[selectors_key]
        if not isinstance(selectors, list):
            raise ValueError(f"'{selectors_key}' must be a list.")
        for selector in selectors:
            if selector:
                locators.append((By.CSS_SELECTOR, selector))

    if xpath_key in config_values and config_values[xpath_key]:
        locators.append((By.XPATH, config_values[xpath_key]))

    if xpaths_key in config_values and config_values[xpaths_key]:
        xpaths = config_values[xpaths_key]
        if not isinstance(xpaths, list):
            raise ValueError(f"'{xpaths_key}' must be a list.")
        for xpath in xpaths:
            if xpath:
                locators.append((By.XPATH, xpath))

    if not locators:
        raise KeyError(
            f"Missing locator for '{key_prefix}'. Add one of: "
            f"'{selector_key}', '{selectors_key}', '{xpath_key}', '{xpaths_key}'."
        )

    # Preserve order while removing duplicates.
    seen = set()
    deduped_locators: List[Tuple[str, str]] = []
    for locator in locators:
        if locator not in seen:
            seen.add(locator)
            deduped_locators.append(locator)
    return deduped_locators


def click_by_locator(web, by: str, locator: str, timeout: int = 12):
    try:
        wait = WebDriverWait(web, timeout)
        element = wait.until(EC.element_to_be_clickable((by, locator)))
        element.click()
        return 0
    except (TimeoutException, NoSuchElementException):
        print(f"Element not found/clickable for locator type '{by}': {locator}")
        print(f"Current URL: {web.current_url}")
        print(f"Page title: {web.title}")
        return 1


def _try_click_in_current_context(web, by: str, locator: str, timeout: int = 12) -> bool:
    try:
        wait = WebDriverWait(web, timeout)
        element = wait.until(EC.element_to_be_clickable((by, locator)))
        element.click()
        return True
    except (TimeoutException, NoSuchElementException):
        return False


def click_with_fallback(web, locators: List[Tuple[str, str]], timeout: int = 12) -> int:
    # Try the top document first.
    web.switch_to.default_content()
    for by, locator in locators:
        if _try_click_in_current_context(web, by, locator, timeout):
            print(f"Clicked via locator type '{by}': {locator}")
            return 0

    # Then try each iframe for pages that embed poll widgets.
    frames = web.find_elements(By.TAG_NAME, "iframe")
    for frame_index in range(len(frames)):
        try:
            web.switch_to.default_content()
            frames = web.find_elements(By.TAG_NAME, "iframe")
            web.switch_to.frame(frames[frame_index])
        except Exception:
            continue

        for by, locator in locators:
            if _try_click_in_current_context(web, by, locator, timeout):
                print(
                    f"Clicked via iframe {frame_index} locator type '{by}': {locator}"
                )
                web.switch_to.default_content()
                return 0

    web.switch_to.default_content()
    print("Element not found/clickable for all fallback locators.")
    for by, locator in locators:
        print(f"Tried locator type '{by}': {locator}")
    print(f"Current URL: {web.current_url}")
    print(f"Page title: {web.title}")
    return 1


def delete_cookies():
    try:
        driver = globals().get("web")
        if driver is None:
            return 1

        capabilities = getattr(driver, "capabilities", {}) or {}
        profile_paths = []

        # Prefer the profile path of the active Selenium session.
        moz_profile = capabilities.get("moz:profile")
        if moz_profile:
            profile_paths.append(Path(moz_profile).expanduser())

        chrome_data = (capabilities.get("chrome") or {}).get("userDataDir")
        if chrome_data:
            profile_paths.append(Path(chrome_data).expanduser())

        edge_data = (capabilities.get("ms:edgeOptions") or {}).get("userDataDir")
        if edge_data:
            profile_paths.append(Path(edge_data).expanduser())

        # Fallback: only target temporary Selenium profile folders.
        if not profile_paths:
            temp_root = Path(tempfile.gettempdir())
            fallback_patterns = [
                "rust_mozprofile*",  # Firefox temporary Selenium profiles
                "scoped_dir*",  # Chromium temporary Selenium profiles
                "webdriver*",  # Generic webdriver temp folders
            ]
            for pattern in fallback_patterns:
                for temp_path in temp_root.glob(pattern):
                    if temp_path.is_dir():
                        profile_paths.append(temp_path)

        # Close the driver first so profile files are not locked.
        try:
            driver.quit()
        except Exception:
            pass

        deleted_any = False
        for profile_path in profile_paths:
            if profile_path.exists():
                shutil.rmtree(profile_path, ignore_errors=False)
                deleted_any = True

        if deleted_any:
            globals()["web"] = None
            return 0
        return 1
    except:
        return 1


def process(
    link_website: str,
    voting_locators: List[Tuple[str, str]],
    sending_locators: List[Tuple[str, str]],
    cookies: bool = False,
    cookies_locators: List[Tuple[str, str]] = None,
    deleting_cookies: bool = False,
    extreme_mode: bool = False,
):
    error = 0
    while True:
        website = open_website(link_website)
        globals()["web"] = website
        # accept/decline cookies if needed
        error_cookies = 0
        if cookies:
            print("Accepting cookies...")
            error_cookies = click_with_fallback(website, cookies_locators)
        if not extreme_mode:
            time.sleep(random.randint(1, 2))
        # vote for climate justice
        print("Voting for climate justice...")
        error_voting = click_with_fallback(website, voting_locators)
        if error_voting:
            error += error_cookies + error_voting
            if deleting_cookies:
                print("Deleting browser-cookies on machine...")
                delete_cookies()
            if not extreme_mode:
                time.sleep(random.randint(5, 10))
            if error > 10:
                raise Exception("More than 10 errors occured during execution.")
            continue
        # send vote
        if not extreme_mode:
            time.sleep(random.randint(1, 3))
        print("Sending vote...")
        error_sending = click_with_fallback(website, sending_locators)
        error += error_cookies + error_voting + error_sending
        # delete cookies if needed
        if deleting_cookies:
            print("Deleting browser-cookies on machine...")
            delete_cookies()
        if not extreme_mode:
            time.sleep(random.randint(5, 10))
        if error > 10:
            raise Exception("More than 10 errors occured during execution.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Vote for climate justice by selecting a config section."
    )
    parser.add_argument(
        "-config_section",
        required=True,
        type=str,
        help="Config section name from vote_config.yaml",
    )
    parser.add_argument(
        "-config_file",
        default=str(DEFAULT_CONFIG_PATH),
        type=str,
        help="Path to YAML config file",
    )
    return parser


def load_config_section(config_file: str, config_section: str) -> dict:
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fp:
        config = yaml.safe_load(fp) or {}

    if config_section not in config:
        raise KeyError(
            f"Config section '{config_section}' not found in {config_path}."
        )

    section = config[config_section] or {}
    if not isinstance(section, dict):
        raise ValueError(
            f"Config section '{config_section}' must contain key/value pairs."
        )
    return section


def main():
    args = build_parser().parse_args()

    config_section = args.config_section
    config_values = load_config_section(args.config_file, config_section)

    link_website = config_values["link_website"]
    cookies = bool(config_values.get("cookies", False))
    voting_locators = get_locators(config_values, "voting")
    sending_locators = get_locators(config_values, "sending")
    if cookies:
        cookies_locators = get_locators(config_values, "cookies")
    else:
        cookies_locators = []
    deleting_cookies = bool(config_values.get("deleting_cookies", True))
    extreme_mode = bool(config_values.get("extreme_mode", False))

    print(
        f"Loaded config section '{config_section}'. Voting for climate justice. - Enjoy!"
        )

    if cookies:
        process(
			link_website=link_website,
			cookies_locators=cookies_locators,
			voting_locators=voting_locators,
			sending_locators=sending_locators,
			cookies=True,
			deleting_cookies=deleting_cookies,
			extreme_mode=extreme_mode,
		)
    else: 
        process(
			link_website=link_website,
			voting_locators=voting_locators,
			sending_locators=sending_locators,
			cookies=False,
			deleting_cookies=deleting_cookies,
			extreme_mode=extreme_mode,
		)


if __name__ == "__main__":
    main()