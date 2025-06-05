import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def main():
    email = os.getenv("FREELANCER_EMAIL")
    password = os.getenv("FREELANCER_PASSWORD")
    search_term = os.getenv("SEARCH_KEYWORD", "freelancer")
    max_pages = int(os.getenv("MAX_PAGES", "1"))

    if not email or not password:
        print("Please set FREELANCER_EMAIL and FREELANCER_PASSWORD in environment variables.")
        return

    options = Options()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    jobs = []
    try:
        # Login
        driver.get("https://www.freelancer.com/login")
        wait.until(EC.element_to_be_clickable((By.ID, "emailOrUsername"))).send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for login to complete
        try:
            wait.until(EC.presence_of_element_located((By.ID, "user-menu-toggle")))
        except TimeoutException:
            print("Login failed")
            return

        # Navigate to search results
        search_url = f"https://www.freelancer.com/jobs/{search_term.replace(' ', '-')}/"
        driver.get(search_url)

        current_page = 1
        while current_page <= max_pages:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".JobSearchCard-item")))
            cards = driver.find_elements(By.CSS_SELECTOR, ".JobSearchCard-item")
            for card in cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, ".JobSearchCard-primary-heading-link").text.strip()
                except Exception:
                    title = ""
                try:
                    desc = card.find_element(By.CSS_SELECTOR, ".JobSearchCard-primary-description").text.strip()
                except Exception:
                    desc = ""
                try:
                    price = card.find_element(By.CSS_SELECTOR, ".JobSearchCard-secondary-price").text.strip()
                except Exception:
                    price = ""
                jobs.append([title, desc, price])

            if current_page >= max_pages:
                break
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "a[data-testid='pagination-next']")
                if not next_btn.is_enabled():
                    break
                next_btn.click()
                time.sleep(2)
                current_page += 1
            except Exception:
                break

        if jobs:
            with open("freelancer_jobs.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Title", "Description", "Price"])
                writer.writerows(jobs)
            print(f"Saved {len(jobs)} jobs to freelancer_jobs.csv")
        else:
            print("No jobs found")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
