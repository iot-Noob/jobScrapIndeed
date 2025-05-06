import requests
from bs4 import BeautifulSoup
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape_indeed_jobs(query, location, pages=1):
    base_url = "https://www.indeed.com/jobs"
    jobs = []
    
    for page in range(pages):
        params = {
            "q": query,
            "l": location,
            "start": page * 10  # Pagination (each page has 10 results)
        }
        
        response = requests.get(base_url, params=params, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find job containers (update class based on current structure)
        job_cards = soup.find_all("div", class_="job_seen_beacon")
        
        for job in job_cards:
            title = job.find("h2", class_="jobTitle").text.strip()
            company = job.find("span", class_="companyName").text.strip()
            location = job.find("div", class_="companyLocation").text.strip()
            
            # Salary may not always be present
            salary_tag = job.find("div", class_="metadata salary-snippet-container")
            salary = salary_tag.text.strip() if salary_tag else "Not listed"
            
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "salary": salary
            })
        
        time.sleep(1)  # Avoid overwhelming the server
    
    return jobs

# Example usage
jobs = scrape_indeed_jobs("react js", "Lahore", pages=2)
for job in jobs:
    print(job)