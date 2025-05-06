import os
import sys
import time
import random
import pickle
import toml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, 
                                      NoSuchElementException, 
                                      WebDriverException)

# Configuration loading and validation (same as original)
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
        print("Error: Cannot find config.toml.")
        sys.exit(1)

    with open(mp, "r") as f:
        cfg = toml.load(f)

    # Validate configuration
    required_fields = {
        "indeed_data": ["url", "signin_url"],
        "credentials": ["email", "password"]
    }
    for section, fields in required_fields.items():
        if section not in cfg:
            raise ValueError(f"Missing [{section}] in config.toml")
        for field in fields:
            if not cfg[section].get(field):
                raise ValueError(f"Missing {field} in [{section}]")

    print("✅ Config validated successfully!")

except Exception as e:
    print(f"❌ Config error: {e}")
    sys.exit(1)

# Configure Firefox options
options = webdriver.FirefoxOptions()
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)
options.set_preference("privacy.resistFingerprinting", True)
options.headless = False  # Visible for debugging

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/116.0",
]
options.set_preference("general.useragent.override", random.choice(user_agents))

driver = webdriver.Firefox(options=options)
driver.set_window_size(random.randint(1200, 1600), random.randint(800, 1000))
wait = WebDriverWait(driver, 15)
actions = ActionChains(driver)

def random_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

def save_session():
    pickle.dump(driver.get_cookies(), open("indeed_session.pkl", "wb"))
    print("💾 Session saved")

def load_session():
    try:
        cookies = pickle.load(open("indeed_session.pkl", "rb"))
        driver.get(cfg["indeed_data"]["url"])
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-tn-element='accountMenu']")))
        print("🔑 Loaded existing session")
        return True
    except (FileNotFoundError, EOFError, WebDriverException) as e:
        return False

def handle_google_login():
    try:
        # Switch to Google login window
        main_window = driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2))
        new_window = [w for w in driver.window_handles if w != main_window][0]
        driver.switch_to.window(new_window)

        # Handle email entry
        email_field = wait.until(
            EC.visibility_of_element_located((By.ID, "identifierId")))
        email_field.send_keys(cfg["credentials"]["email"])
        driver.find_element(By.ID, "identifierNext").click()
        random_delay()

        # Handle password entry
        password_field = wait.until(
            EC.visibility_of_element_located((By.NAME, "Passwd")))
        password_field.send_keys(cfg["credentials"]["password"])
        driver.find_element(By.ID, "passwordNext").click()
        random_delay(2, 4)

        # Check for login errors
        try:
            error = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[aria-live='assertive']")))
            print(f"❌ Google login failed: {error.text}")
            return False
        except TimeoutException:
            pass

        # Return to main window
        wait.until(EC.number_of_windows_to_be(1))
        driver.switch_to.window(main_window)
        return True

    except Exception as e:
        print(f"❌ Google login error: {str(e)}")
        return False

def indeed_signin():
    try:
        driver.get(cfg["indeed_data"]["signin_url"])
        random_delay()

        # Click Google sign-in button
        google_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[data-tn-element='googleSignInButton']")))
        google_btn.click()
        random_delay()

        if not handle_google_login():
            return False

        # Verify successful login
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-tn-element='accountMenu']")))
        save_session()
        return True

    except Exception as e:
        print(f"❌ Indeed sign-in error: {str(e)}")
        return False

# Main execution flow
try:
    if not load_session():
        print("🔐 No valid session found, starting login...")
        if not indeed_signin():
            print("❌ Failed to establish session")
            sys.exit()
    
    print("✅ Successfully logged in!")
    random_delay()
    # Add your post-login actions here

except Exception as e:
    print(f"❌ Critical error: {str(e)}")
    sys.exit(1)

finally:
    driver.quit()