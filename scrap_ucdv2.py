import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import random
import time
import toml
import os
import sys
driver = None  # Global singleton
found = False
mp = ""
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
]
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
    if not cfg["indeed_data"]["url"]:
        raise ValueError("Error arry of url is empty in toml")
            
    # Validate [credentials]
    for key in ["email", "password"]:
        val = cfg["credentials"].get(key)
        if not val or str(val).strip() == "":
            raise ValueError(f"Missing or empty '{key}' in [credentials] section")

    print("✅ Config loaded and validated successfully in scrap!")

except Exception as e:
    print(f"❌ Failed to load or validate config.toml: {e}")
    sys.exit()
    

def get_driver():
    global driver
    if not driver:
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        
        # Set random user agent
        selected_ua = random.choice(user_agents)
        options.add_argument(f'user-agent={selected_ua}')
        
        try:
            driver = uc.Chrome(options=options)
            # Set consistent window size with small random variation
            base_width = 1440
            base_height = 900
            driver.set_window_size(
                base_width + random.randint(-100, 100),
                base_height + random.randint(-50, 50)
            )
            print("🚀 New browser instance created")
        except Exception as e:
            print(f"❌ Driver initialization failed: {e}")
            raise
    return driver

def cleanup_driver():
    global driver
    if driver:
        try:
            driver.quit()
            print("🛑 Browser closed properly")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")
        finally:
            driver = None
 


def random_delay(min_time=1.5, max_time=4.0):
    time.sleep(random.uniform(min_time, max_time))

actions = ActionChains(driver)

def get_job_data():
    try:
        global driver
        if not driver:
            get_driver()
        # Wait for job results to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='slider_item']"))
        )

        # Get all job cards
        jobs = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='slider_item']")
        print(f"🎯 Found {len(jobs)} job listings")

        # Scrape job details
        job_list = []
        for index, job in enumerate(jobs):
            try:
                # Human-like interaction pattern
                if index % 3 == 0:
                    actions.move_to_element(job).perform()
                    random_delay(0.2, 0.5)

                # Extract job details
                title = job.find_element(By.CSS_SELECTOR, "span[id^='jobTitle']").text
                company = job.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
                location = job.find_element(By.CSS_SELECTOR, "[data-testid='text-location']").text
                
                # Salary (might not be present)
                salary = "Not specified"
                salary_elements = job.find_elements(By.CSS_SELECTOR, "[data-testid='attribute_snippet_testid']")
                if salary_elements:
                    salary = salary_elements[0].text
                
                # Job description
                description_items = job.find_elements(By.CSS_SELECTOR, "[data-testid='jobsnippet_footer'] li")
                description = "\n".join([item.text for item in description_items])

                # Job URL
                job_url = job.find_element(By.CSS_SELECTOR, "a[id^='job_']").get_attribute("href")

                job_list.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary": salary,
                    "description": description,
                    "url": job_url
                })

            except Exception as e:
                print(f"⚠️ Error processing job {index + 1}: {str(e)}")
                continue

        return job_list

    except Exception as e:
        print(f"🔥 Error in job scraping: {str(e)}")
        return []


def get_job():
    try:
        global driver
        get_driver()  # Initialize driver first
        all_jobs = []
        for url in cfg["indeed_data"]["url"]:
            driver.get(url)  # Now driver is guaranteed to exist
            all_jobs.extend(get_job_data())
        return all_jobs
    finally:
        time.sleep(random.randint(2, 5))
        cleanup_driver()  # Already handles quitting
 