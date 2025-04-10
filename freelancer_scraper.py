import time
import csv
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys

class FreelancerScraper:
    def __init__(self, email, password, search_keyword, max_pages=3):
        """Initialize the scraper with login credentials and search keyword"""
        self.email = email
        self.password = password
        self.search_keyword = search_keyword
        self.max_pages = max_pages  # Maximum number of pages to scrape
        self.base_url = "https://www.freelancer.com/job-search/users/"
        self.driver = None
        self.wait = None
        
        # Create output directory
        self.output_dir = "freelancer_data"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.setup_driver()
        
    def take_screenshot(self, name):
        """Take a screenshot and save it to the output directory"""
        screenshot_path = os.path.join(self.output_dir, f"{name}_{int(time.time())}.png")
        self.driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options"""
        options = Options()
        # Uncomment the line below if you want to run in headless mode
        # options.add_argument('--headless')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        # Set a user agent to appear more like a normal browser
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)  # 15 seconds timeout for wait conditions
        
    def navigate_to_site(self):
        """Navigate to the target website"""
        print("Navigating to the website...")
        self.driver.get(self.base_url)
        time.sleep(3)  # Wait for the page to load
        
    def login(self):
        """Login to the website with provided credentials"""
        try:
            print("Attempting to log in...")
            
            # Try multiple selectors for login button
            try:
                # First approach - look for specifically marked "Log In" links
                login_button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(), 'Log In') or contains(@class, 'login-link')]")
                ))
            except TimeoutException:
                try:
                    # Second approach - look for 'login' in href or class
                    login_button = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(@href, 'login') or contains(@class, 'login')]")
                    ))
                except TimeoutException:
                    # Third approach - look for any login-related text including capitalization variants
                    login_button = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(translate(text(), 'LOGIN', 'login'), 'login') or contains(@data-uitest, 'login')]")
                    ))
            
            # Scroll to the login button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(1)
            
            # Click on the login button
            login_button.click()
            
            # Wait longer for login form to fully appear and stabilize
            time.sleep(3)
            
            # Wait for login form to appear and be ready for input
            try:
                email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "emailOrUsername")))
            except TimeoutException:
                # Try alternative field IDs
                try:
                    email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "email")))
                except TimeoutException:
                    # Try by name or placeholder
                    email_field = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//input[contains(@placeholder, 'Email') or @name='email' or @name='username']")
                    ))
            
            time.sleep(1)  # Extra pause before typing
            email_field.clear()
            email_field.send_keys(self.email)
            print("Entered email")
            
            # Find password field and input password
            try:
                password_field = self.wait.until(EC.element_to_be_clickable((By.ID, "password")))
            except TimeoutException:
                # Try by name or placeholder
                password_field = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='password' or contains(@placeholder, 'Password') or @name='password']")
                ))
            
            time.sleep(1)  # Extra pause before typing
            password_field.clear()
            password_field.send_keys(self.password)
            print("Entered password")
            
            # Wait a moment before submitting
            time.sleep(2)
            
            # Try multiple selectors for submit button
            try:
                submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            except TimeoutException:
                try:
                    # Try buttons with login text
                    submit_button = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Sign')] | //input[@type='submit']")
                    ))
                except TimeoutException:
                    # Try any login-related button
                    submit_button = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'login') or contains(@class, 'submit')] | //input[@type='submit']")
                    ))
            
            # Scroll to submit button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)
            
            submit_button.click()
            print("Clicked login button")
            
            # Wait longer for login to complete
            time.sleep(8)
            print("Login successful!")
            
        except TimeoutException as e:
            print(f"Timed out waiting for login elements to load: {e}")
            print("Taking screenshot of current page...")
            self.take_screenshot("login_error")
        except NoSuchElementException as e:
            print(f"Could not find element: {e}")
            print("Taking screenshot of current page...")
            self.take_screenshot("login_error")
        except Exception as e:
            print(f"Error during login: {e}")
            print("Taking screenshot of current page...")
            self.take_screenshot("login_error")
            
    def perform_search(self):
        """Perform a search with the given keyword"""
        try:
            print(f"Searching for: {self.search_keyword}")
            
            # Wait to make sure the page is fully loaded after login
            time.sleep(3)
            
            # Try multiple approaches to find the search field
            try:
                # First try with placeholder text
                search_field = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='Search Keyword' or @type='search']")
                ))
            except TimeoutException:
                try:
                    # Try with common search field attributes
                    search_field = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//input[contains(@class, 'search') or @name='query' or @name='search']")
                    ))
                except TimeoutException:
                    # Try any input in a form
                    search_field = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//form//input[@type='text' or @type='search']")
                    ))
            
            # Scroll to the search field and focus on it
            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_field)
            time.sleep(1)
            
            # Clear and enter search keyword
            search_field.clear()
            time.sleep(0.5)
            search_field.send_keys(self.search_keyword)
            print(f"Entered search keyword: {self.search_keyword}")
            
            # Try to find the search button
            try:
                # First try with text or type
                search_button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Search') or @type='submit']")
                ))
            except TimeoutException:
                try:
                    # Look for search icon or class
                    search_button = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'search')] | //input[@type='submit']")
                    ))
                except TimeoutException:
                    # Look for any button in the same form
                    form = search_field.find_element(By.XPATH, "./ancestor::form")
                    search_button = form.find_element(By.XPATH, ".//button | .//input[@type='submit']")
            
            # Scroll to search button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(1)
            
            # Click the button
            search_button.click()
            print("Clicked search button")
            
            # Wait for search results to load
            time.sleep(8)
            print("Search completed!")
            
        except TimeoutException as e:
            print(f"Timed out waiting for search elements to load: {e}")
            print("Taking screenshot of current page...")
            self.take_screenshot("search_error")
            # Try submitting with Enter key as fallback
            try:
                search_field.send_keys(Keys.RETURN)
                time.sleep(5)
                print("Used Enter key to submit search as fallback")
            except:
                print("Could not use fallback search method")
        except NoSuchElementException as e:
            print(f"Could not find search element: {e}")
            print("Taking screenshot of current page...")
            self.take_screenshot("search_error")
        except Exception as e:
            print(f"Error during search: {e}")
            print("Taking screenshot of current page...")
            self.take_screenshot("search_error")
            
    def extract_freelancer_data(self):
        """Extract job information from search results across multiple pages"""
        all_job_data = []
        current_page = 1
        
        try:
            print("Extracting job data...")
            
            while current_page <= self.max_pages:
                print(f"Processing page {current_page} of {self.max_pages}...")
                
                # Wait for the page to fully load
                time.sleep(3)
                
                # Take a screenshot of the search results
                self.take_screenshot(f"search_results_page_{current_page}")
                
                # Try different selectors for job cards
                try:
                    # First try with common JobSearchCard classes
                    self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'JobSearchCard') or contains(@class, 'search-result-card')]")))
                    job_cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'JobSearchCard') or contains(@class, 'search-result-card')]")
                except TimeoutException:
                    try:
                        # Try with more general card elements
                        job_cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'card') and .//a[contains(@href, '/projects/')]]")
                    except:
                        # Last resort - try any container with job-like content
                        job_cards = self.driver.find_elements(By.XPATH, "//div[.//h2 or .//h3 or .//div[contains(@class, 'title')]]")
                
                if not job_cards:
                    print("No job cards found on this page.")
                    break
                
                print(f"Found {len(job_cards)} job cards on page {current_page}")
                
                # Process each job card
                for index, card in enumerate(job_cards):
                    try:
                        print(f"Processing job card {index+1}/{len(job_cards)}...")
                        
                        # Extract job title with multiple XPath attempts
                        title = "Not available"
                        title_xpaths = [
                            ".//a[contains(@class, 'JobSearchCard-primary-heading-link')]",
                            ".//a[contains(@class, 'job-title')]",
                            ".//div[contains(@class, 'job-title')]",
                            ".//h2",
                            ".//h3",
                            ".//div[contains(@class, 'title')]",
                            ".//a[contains(@href, '/projects/')]"
                        ]
                        
                        for xpath in title_xpaths:
                            try:
                                title_element = card.find_element(By.XPATH, xpath)
                                title = title_element.text.strip()
                                if title:
                                    break
                            except NoSuchElementException:
                                continue
                        
                        # Extract job description with multiple XPath attempts
                        description = "Not available"
                        description_xpaths = [
                            ".//p[contains(@class, 'JobSearchCard-primary-description')]",
                            ".//div[contains(@class, 'job-description')]",
                            ".//p[contains(@class, 'description')]",
                            ".//div[contains(@class, 'desc')]",
                            ".//p"
                        ]
                        
                        for xpath in description_xpaths:
                            try:
                                desc_elements = card.find_elements(By.XPATH, xpath)
                                if desc_elements:
                                    # Use the longest paragraph as the description
                                    desc_texts = [el.text.strip() for el in desc_elements if el.text.strip()]
                                    if desc_texts:
                                        description = max(desc_texts, key=len)
                                        break
                            except:
                                continue
                        
                        # Extract price range with multiple XPath attempts
                        price = "Not specified"
                        price_xpaths = [
                            ".//div[contains(@class, 'JobSearchCard-primary-price')]",
                            ".//span[contains(@class, 'price')]",
                            ".//div[contains(@class, 'price')]",
                            ".//div[contains(text(), '$')]",
                            ".//span[contains(text(), '$')]"
                        ]
                        
                        for xpath in price_xpaths:
                            try:
                                price_elements = card.find_elements(By.XPATH, xpath)
                                if price_elements:
                                    price_texts = [el.text.strip() for el in price_elements if el.text.strip()]
                                    if price_texts:
                                        # Use the first non-empty price text
                                        price = price_texts[0]
                                        break
                            except:
                                continue
                        
                        # Extract skills with multiple XPath attempts
                        skills = []
                        skills_xpaths = [
                            ".//a[contains(@class, 'JobSearchCard-primary-tagsLink')]",
                            ".//span[contains(@class, 'skill-tag')]",
                            ".//a[contains(@class, 'skill')]",
                            ".//span[contains(@class, 'tag')]",
                            ".//div[contains(@class, 'skills')]//a"
                        ]
                        
                        for xpath in skills_xpaths:
                            try:
                                skills_elements = card.find_elements(By.XPATH, xpath)
                                if skills_elements:
                                    skill_texts = [skill.text.strip() for skill in skills_elements if skill.text.strip()]
                                    if skill_texts:
                                        skills = skill_texts
                                        break
                            except:
                                continue
                        
                        # Add data to list
                        all_job_data.append({
                            'Title': title,
                            'Description': description,
                            'Price': price,
                            'Skills': ', '.join(skills),
                            'Page': current_page
                        })
                        
                        print(f"Successfully extracted data for: {title}")
                        
                    except Exception as e:
                        print(f"Error extracting data from card {index+1}: {e}")
                        continue
                
                print(f"Extracted data from {len(job_cards)} job cards on page {current_page}")
                
                # Check if there's a next page and navigate to it
                if current_page < self.max_pages:
                    try:
                        # Try multiple XPaths for next page button
                        next_button = None
                        next_button_xpaths = [
                            "//a[contains(text(), 'Next')]",
                            "//a[contains(@class, 'next-page')]",
                            "//li[contains(@class, 'pagination-next')]/a",
                            "//a[contains(@rel, 'next')]",
                            "//a[contains(@aria-label, 'Next')]",
                            "//button[contains(text(), 'Next')]"
                        ]
                        
                        for xpath in next_button_xpaths:
                            try:
                                buttons = self.driver.find_elements(By.XPATH, xpath)
                                for btn in buttons:
                                    if btn.is_displayed() and btn.is_enabled():
                                        next_button = btn
                                        break
                                if next_button:
                                    break
                            except:
                                continue
                        
                        if not next_button:
                            print("Could not find next page button. Reached the last page.")
                            break
                        
                        # Check if the next button is disabled
                        disabled = next_button.get_attribute("disabled") == "true" or "disabled" in next_button.get_attribute("class")
                        
                        if not disabled:
                            # Scroll to the next button
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                            time.sleep(1)
                            
                            # Click the next button
                            next_button.click()
                            time.sleep(5)  # Wait for the next page to load
                            current_page += 1
                        else:
                            print("Next page button is disabled. Reached the last page.")
                            break
                            
                    except (NoSuchElementException, ElementClickInterceptedException) as e:
                        print(f"Could not navigate to next page: {e}")
                        break
                else:
                    break
            
            print(f"Total data extracted: {len(all_job_data)} jobs from {current_page} pages")
            return all_job_data
            
        except TimeoutException:
            print("Timed out waiting for search results to load")
            return all_job_data
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return all_job_data
    
    def save_to_csv(self, data, filename=None):
        """Save extracted data to a CSV file"""
        try:
            if not data:
                print("No data to save")
                return
            
            if filename is None:
                # Create filename based on search keyword
                safe_keyword = self.search_keyword.replace(' ', '_')
                filename = os.path.join(self.output_dir, f"freelancer_{safe_keyword}.csv")
                
            # Convert to DataFrame and save to CSV
            df = pd.DataFrame(data)
            
            # Ensure columns are in the desired order
            column_order = ['Title', 'Description', 'Price', 'Skills', 'Page']
            df = df[column_order]
            
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data successfully saved to {filename}")
            
        except Exception as e:
            print(f"Error saving data to CSV: {e}")
    
    def run(self):
        """Run the complete scraping process"""
        try:
            self.navigate_to_site()
            self.login()
            self.perform_search()
            data = self.extract_freelancer_data()
            
            # Take screenshot of results page
            if data:
                print("Taking screenshot of results page...")
                self.take_screenshot("search_results")
                
            self.save_to_csv(data)
        finally:
            # Always close the driver
            if self.driver:
                self.driver.quit()
                print("Browser closed")

if __name__ == "__main__":
    # Replace with your actual login credentials and search term
    email = "your_email@example.com"
    password = "your_password"
    search_term = "web developer"
    
    # Create and run the scraper
    scraper = FreelancerScraper(email, password, search_term)
    scraper.run() 