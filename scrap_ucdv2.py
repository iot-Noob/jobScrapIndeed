import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver
import pickle
import random
import time
import toml
import os
import sys
from main_logging import logging_func,logging
class WebScraper:
    def __init__(self):
        self.driver = None
        self.cfg = None
        self.found = False
        self.mp = ""
        self.init_configs()
        self.init_driver()
        
    def __del__(self):
        self.cleanup_driver()
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_driver()
    
    @logging_func
    def init_configs(self):
        try:
            for root, _, files in os.walk("./"):
                for f in files:
                    if f.endswith(".toml"):
                        self.found = True
                        self.mp = os.path.join(root, f)
                        break
                if self.found:
                    break

            if not self.found:
                print("Error: Cannot find config.toml. Please make a config.toml in the same directory.")
                sys.exit(1)

            with open(self.mp, "r") as f:
                self.cfg = toml.load(f)

            if "indeed_data" not in self.cfg:
                raise ValueError("Missing [indeed_data] section in config.toml")
            if "credentials" not in self.cfg:
                raise ValueError("Missing [credentials] section in config.toml")

            for key in ["url", "signin_url"]:
                val = self.cfg["indeed_data"].get(key)
                if not val or str(val).strip() == "":
                    raise ValueError(f"Missing or empty '{key}' in [indeed_data] section")
            if not self.cfg["indeed_data"]["url"]:
                raise ValueError("Error: Array of url is empty in toml")

            for key in ["email", "password"]:
                val = self.cfg["credentials"].get(key)
                if not val or str(val).strip() == "":
                    raise ValueError(f"Missing or empty '{key}' in [credentials] section")

            print("✅ Config loaded and validated successfully!")
            logging.info("config load sucess ✅")
        except Exception as e:
            print(f"❌ Failed to load or validate config.toml: {e}")
            sys.exit()
    @logging_func
    def init_driver(self):
        if not self.driver:
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-popup-blocking")

            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
            ]
            options.add_argument(f'user-agent={random.choice(user_agents)}')

            self.driver = uc.Chrome(options=options)
            self.driver.set_window_size(random.randint(1200, 1600), random.randint(800, 1000))
    @logging_func
    def cleanup_driver(self):
        if self.driver:
            try:
                if hasattr(self.driver, 'quit'):
                    self.driver.quit()
                    print("🛑 Browser closed")
            except Exception as e:
                print(f"⚠️ Error closing browser: {e}")
            finally:
                try:
                    self.driver.service.stop()  # Extra stop to ensure kill
                except:
                    pass
                self.driver = None

    def random_delay(self, min_time=1.5, max_time=4.0):
        time.sleep(random.uniform(min_time, max_time))

    def handle_captcha(self):
        try:
            WebDriverWait(self.driver, 20).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title*='Cloudflare Challenge']"))
            )

            solver = RecaptchaSolver(driver=self.driver)
            solver.click_recaptcha_v2(
                iframe=self.driver.find_element(By.CSS_SELECTOR, "iframe[title*='Cloudflare Challenge']")
            )

            self.driver.switch_to.default_content()
            return True
        except Exception as e:
            print(f"CAPTCHA handling failed: {e}")
            return False
    @logging_func
    def get_job_data(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='slider_item']"))
            )

            jobs = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='slider_item']")
            print(f"🎯 Found {len(jobs)} job listings")

    
            for index, job in enumerate(jobs):
                try:
                    actions = ActionChains(self.driver)

                    if index % 3 == 0:
                        actions.move_to_element(job).pause(random.uniform(0.2, 0.5)).perform()
                        self.random_delay(0.2, 0.5)

                    title = job.find_element(By.CSS_SELECTOR, "span[id^='jobTitle']").text
                    company = job.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
                    location = job.find_element(By.CSS_SELECTOR, "[data-testid='text-location']").text

                    salary = "Not specified"
                    salary_elements = job.find_elements(By.CSS_SELECTOR, "[data-testid='attribute_snippet_testid']")
                    if salary_elements:
                        salary = salary_elements[0].text

                    description_items = job.find_elements(By.CSS_SELECTOR, "[data-testid='jobsnippet_footer'] li")
                    description = "\n".join([item.text for item in description_items])

                    job_url = job.find_element(By.CSS_SELECTOR, "a[id^='job_']").get_attribute("href")
                    yield {
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": salary,
                        "description": description,
                        "url": job_url
                    }
           
                except Exception as e:
                    print(f"⚠️ Error processing job {index + 1}: {str(e)}")
                    
                    continue

        

        except Exception as e:
            print(f"🔥 Error in job scraping: {str(e)}")
            return []
    @logging_func
    def get_jobs(self,*args):
        try:
            self.init_driver() 
            urls = args[0] if len(args) == 1 and isinstance(args[0], list) else args
            urls = urls if urls else self.cfg["indeed_data"]["url"]
            for url in urls:
                try:
                    self.handle_captcha()
                    print(f"🎯 Applying for position at job: {url}")
                    self.driver.get(url)
                    self.random_delay(2, 3)

                    for _ in range(random.randint(2, 4)):
                        try:
                            ActionChains(self.driver)\
                                .scroll_by_amount(0, random.randint(300, 800))\
                                .pause(random.uniform(0.8, 1.2))\
                                .perform()
                        except Exception as scroll_error:
                            print(f"⚠️ Scrolling failed: {scroll_error}")
                            continue

                    for jd in self.get_job_data():
                        yield jd

                except Exception as page_error:
                    print(f"⚠️ Error processing URL {url}: {page_error}")
                    continue

 

        finally:
            self.cleanup_driver()
            time.sleep(random.randint(2, 5))

 
