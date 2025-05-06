from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import random
import time
import toml
import os
import sys  # for sys.exit(
found = False
mp = ""
try:
    # Search for the first .toml file
    for root, _, files in os.walk("./"):
        for f in files:
            if f.endswith(".toml"):
                found = True
                mp = os.path.join(root, f)
                break
        if found:
            break

    if not found:
        print("Error: Cannot find config.toml. Please make a config.toml in the same directory.")
        sys.exit(1)

    # Load TOML file
    with open(mp, "r") as f:
        cfg = toml.load(f)

    # Check required sections
    if "indeed_data" not in cfg:
        raise ValueError("Missing [indeed_data] section in config.toml")
    if "credentials" not in cfg:
        raise ValueError("Missing [credentials] section in config.toml")

    # Validate [indeed_data]
    for key in ["url", "signin_url"]:
        val = cfg["indeed_data"].get(key)
        if not val or str(val).strip() == "":
            raise ValueError(f"Missing or empty '{key}' in [indeed_data] section")

    # Validate [credentials]
    for key in ["email", "password"]:
        val = cfg["credentials"].get(key)
        if not val or str(val).strip() == "":
            raise ValueError(f"Missing or empty '{key}' in [credentials] section")

    print("✅ Config loaded and validated successfully!")

except Exception as e:
    print(f"❌ Failed to load or validate config.toml: {e}")
    sys.exit()
# Configure Firefox options
options = webdriver.FirefoxOptions()
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/116.0",
]
options.set_preference("general.useragent.override", random.choice(user_agents))
options.set_preference("general.smoothScroll", True)
options.set_preference("browser.privatebrowsing.autostart", False)
options.headless = False  # Visible browser
options.set_preference("privacy.resistFingerprinting", True)  # Better privacy

# Initialize driver once
driver = webdriver.Firefox(options=options)
driver.set_window_size(random.randint(1200, 1600), random.randint(800, 1000))

def random_delay(min_time=1.5, max_time=4.0):
    time.sleep(random.uniform(min_time, max_time))

actions = ActionChains(driver)

try:
    driver.get(cfg["indeed_data"]["url"])
    random_delay()

    # Simulate human scrolling
    for _ in range(random.randint(1, 3)):
        actions.scroll_by_amount(0, random.randint(300, 800)).perform()
        random_delay(0.5, 1.5)

    # Move mouse randomly
    actions.move_by_offset(random.randint(10, 50), random.randint(10, 50)).perform()
    random_delay()

finally:
    time.sleep(100)
    driver.quit()