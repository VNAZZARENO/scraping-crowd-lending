from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests


def main():

    service = Service('geckodriver.exe') 

    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'  

    download_dir = r"C:\Users\vince\OneDrive\Bureau\Programmation\Python\Market Making Crowd Lending\fici_pdf"  
    os.makedirs(download_dir, exist_ok=True)  

    options.set_preference("browser.download.folderList", 2) 
    options.set_preference("browser.download.dir", download_dir)  
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")  
    options.set_preference("pdfjs.disabled", True)  

    driver = webdriver.Firefox(service=service, options=options)

    login_url = "https://www.pretup.fr/login.php"

    driver.get(login_url)

    time.sleep(1)

    email_input = driver.find_element(By.ID, "user")
    email_input.send_keys("juiced.bellow0l@icloud.com")  # Replace with your actual email

    password_input = driver.find_element(By.ID, "mdp")
    password_input.send_keys("nYpzo1-jyjdif-pimtyg")  # Replace with your actual password

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')  # Adjust if necessary
    login_button.click()

    time.sleep(1)

    projects_url = "https://www.pretup.fr/projets-a-financer" 
    driver.get(projects_url)

    time.sleep(1)


    def load_all_projects(max_clicks=999):
        total_clicks = 0  # To track how many times we try to load more projects
        while total_clicks < max_clicks:  # Set a limit to avoid infinite loop
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "bouton_voir_plus_projets"))
                )

                driver.execute_script("arguments[0].click();", load_more_button)
                total_clicks += 1
                print(f"Clicked 'Voir plus de projets' {total_clicks} time(s)")

                time.sleep(2)

                project_cards = driver.find_elements(By.CLASS_NAME, 'bloc_projet_financer')
                
                if len(project_cards) <= 6 * total_clicks: # Number of projects per load
                    print("No more projects found or reached limit.")
                    break
            except Exception as e:
                print(f"Error loading more projects: {e}")
                break

    def get_url_of_all_projects(website_url, max_clicks=3):
        load_all_projects(max_clicks=max_clicks)
        project_cards = driver.find_elements(By.CLASS_NAME, 'bloc_projet_financer') 
        project_urls = []  

        for card in project_cards:
            try:
                onclick_text = card.get_attribute('onclick')
                project_url = onclick_text.split("'")[1]
                full_url = f"{website_url}{project_url}"
                project_urls.append(full_url)
                print(f"Found project URL: {full_url}")
            except Exception as e:
                print(f"Failed to extract URL from card: {e}")

        
        with open('project_urls.txt', 'r+') as f:
            existing_urls = f.read().splitlines()
            for url in project_urls:
                if url not in existing_urls:
                    f.write(url + '\n')
                    print(f"URL added: {url}")
                else:
                    print(f"URL already present in file: {url}")
        print(f"Total project URLs found: {len(project_urls)}")

        return project_urls


    # Function to download the FICI file using requests and Selenium's session cookies
    def download_fici(url):
        print(f"Navigating to project URL: {url}")
        driver.get(url)
        time.sleep(2)

        try:
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn[href*='telecharger_fici.php']"))
            )
            fici_link = download_button.get_attribute('href')
            print(f'Downloading FICI from: {fici_link}')
            selenium_cookies = driver.get_cookies()
            cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
            response = requests.get(fici_link, cookies=cookies)
            
            if response.status_code == 200:
                pdf_filename = os.path.join(download_dir, f'fici_{url.split("/")[-1]}.pdf')
                with open(pdf_filename, 'wb') as f:
                    f.write(response.content)
                print(f"Successfully downloaded to: {pdf_filename}")
            else:
                print(f"Failed to download FICI from {fici_link}: Status code {response.status_code}")
            time.sleep(2)
            
        except Exception as e:
            print(f"Failed to download FICI from {url}: {e}")


    def scrape_project_text(url, output_dir="project_txt_files"):
        try:
            driver.get(url)
            time.sleep(1)  # Wait for the page to load
            
            project_text = driver.find_element(By.CSS_SELECTOR, "body").text
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            project_id = url.split('-')[-1]
            file_path = os.path.join(output_dir, f"project_{project_id}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(project_text)
            
            print(f"Successfully scraped and saved project {project_id} to {file_path}")

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")


    website_url = "https://www.pretup.fr/"
    project_urls = get_url_of_all_projects(website_url=website_url, max_clicks=1)

    # Uncomment the following lines to load project URLs from a file if needed
    # with open('project_urls.txt', 'r') as f:
    #     project_urls = f.read().splitlines()

    for project_url in project_urls:

        output_dir = "project_txt_files"  
        project_id = project_url.split('-')[-1]
        file_path = os.path.join(output_dir, f"project_{project_id}.txt")
        if os.path.exists(file_path):
            print(f"File already exists for project {project_id}, skipping...")
            continue 
        else:
            # Uncomment if you want to download fici files for further analysis
            # download_fici(project_url)
            scrape_project_text(project_url)
    driver.quit()


if __name__ == "__main__":
    main()