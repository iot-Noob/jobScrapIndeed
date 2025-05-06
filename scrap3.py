import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import toml
import os
import sys
import time
import random

# --- Load and Validate Config ---
found = False
mp = ""

try:
    for root, _, files in os.walk("./"):
        for f in files:
            if f.endswith(".toml"):
                found = True
                mp = os.path.join(root, f)
                break
        if found:
            break

    if not found:
        print("❌ Error: Cannot find config.toml. Please make a config.toml in the same directory.")
        sys.exit(1)

    with open(mp, "r") as f:
        cfg = toml.load(f)

    if "indeed_data" not in cfg:
        raise ValueError("Missing [indeed_data] section in config.toml")
    if "credentials" not in cfg:
        raise ValueError("Missing [credentials] section in config.toml")

    for key in ["url", "signin_url"]:
        val = cfg["indeed_data"].get(key)
        if not val or str(val).strip() == "":
            raise ValueError(f"Missing or empty '{key}' in [indeed_data] section")

    for key in ["email", "password"]:
        val = cfg["credentials"].get(key)
        if not val or str(val).strip() == "":
            raise ValueError(f"Missing or empty '{key}' in [credentials] section")

    print("✅ Config loaded and validated successfully!")

except Exception as e:
    print(f"❌ Failed to load or validate config.toml: {e}")
    sys.exit(1)

# --- Start Chrome in Undetected Mode ---
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
]
options.add_argument(f'user-agent={random.choice(user_agents)}')

driver = uc.Chrome(options=options)
actions = ActionChains(driver)

def random_delay(min_time=1.5, max_time=4.0):
    time.sleep(random.uniform(min_time, max_time))

try:
    driver.get(cfg["indeed_data"]["url"])
    random_delay()

    # Simulate human scrolling
    for _ in range(random.randint(1, 3)):
        driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(300, 800))
        random_delay(0.5, 1.5)

    # Move mouse randomly
    actions.move_by_offset(random.randint(10, 50), random.randint(10, 50)).perform()
    random_delay()

finally:
    print("✅ Script finished. Closing browser in 100 seconds.")
    time.sleep(100)
    driver.quit()
