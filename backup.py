from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pickle
import random
import time
import toml
import os
import sys  # for sys.exit(
found = False
mp = ""
try:
    for root, _, files in os.walk("./"):
        for f in files:
            if f.endswith(".toml"):
                found = True
                mp = os.path.join(root, f)
                break  # Stop after finding the first .toml file
        if found:
            break  # Stop searching other folders

    if found:
        with open(mp, "r") as f:
            cfg = toml.load(f)
        if "indeed_data" not in cfg:
            raise ValueError("Missing [indeed_data] section in config.toml")
            
        if "url" not in cfg["indeed_data"] or not cfg["indeed_data"]["url"]:
            raise ValueError("Missing or empty 'url' key in [indeed_data] section of config.toml")
        if  cfg["indeed_data"]["url"]=="" or cfg["indeed_data"]["url"]==None :
            raise ValueError("Missing or empty 'url' key in [indeed_data] section of config.toml")     
        if  cfg["indeed_data"]["signin_url"]=="" or cfg["indeed_data"]["signin_url"]==None :
            raise ValueError("Missing or empty 'url' key in [indeed_data] section of config.toml")
        if not cfg["indeed_data"]["signin_url"]:
            raise ValueError("Missing or empty 'url' key in [indeed_data] section of config.toml")         
    else:
        print("Error: Cannot find config.toml. Please make a config.toml in the same directory.")
        exit()
except Exception as e:
    print(f"error load toml or read due to {e}")
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
    driver.quit()