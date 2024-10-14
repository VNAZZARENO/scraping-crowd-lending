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

    # Specify the path to geckodriver
    service = Service('geckodriver.exe')  # Update with your actual path to geckodriver

    # Create an instance of Options
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'  # Update with the correct path to Firefox

    # Setting preferences to download PDFs without opening them
    download_dir = r"scraping-crowd-lending\fici_pdf"  # Update to your desired download path
    os.makedirs(download_dir, exist_ok=True)  # Ensure the download directory exists

    options.set_preference("browser.download.folderList", 2)  # 2 indicates a custom download location
    options.set_preference("browser.download.dir", download_dir)  # Path for downloads
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")  # MIME type for PDF files
    options.set_preference("pdfjs.disabled", True)  # Disable the built-in PDF viewer so it forces download

    # Initialize the WebDriver with the service and options
    driver = webdriver.Firefox(service=service, options=options)

    # URL of the login page
    login_url = "https://www.pretup.fr/login.php" #Example in this work, must be adapted for other crowd-lending website

    # Go to the login page
    driver.get(login_url)

    # Wait for the login page to load
    time.sleep(1)

    # Find the email input field by its ID and enter the email
    email_input = driver.find_element(By.ID, "user")
    email_input.send_keys("fake_email@gmail.com")  # Replace with your actual email

    # Find the password input field by its ID and enter the password
    password_input = driver.find_element(By.ID, "mdp")
    password_input.send_keys("123456789")  # Replace with your actual password

    # Find the login button (you might need to adjust the selector if it differs) and click it
    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')  # Adjust if necessary
    login_button.click()

    # Wait for the login process to complete
    time.sleep(1)

    # URL of the main project page
    projects_url = "https://www.pretup.fr/projets-a-financer"  # The main page where all the projects are listed. Again this is an example

    # Go to the main project listing page
    driver.get(projects_url)

    # Wait for the page to load
    time.sleep(1)


    # Function to load all projects by clicking "Voir plus de projets" multiple times using JavaScript
    def load_all_projects(max_clicks=999):
        total_clicks = 0  # To track how many times we try to load more projects
        while total_clicks < max_clicks:  # Set a limit to avoid infinite loop
            try:
                # Wait until the "Voir plus de projets" button is clickable
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "bouton_voir_plus_projets"))
                )

                # Use JavaScript to click the button, bypassing any obstruction
                driver.execute_script("arguments[0].click();", load_more_button)
                
                # Log the action
                total_clicks += 1
                print(f"Clicked 'Voir plus de projets' {total_clicks} time(s)")

                # Wait for more projects to load
                time.sleep(2)

                # Check if more projects are loaded by counting the number of project cards
                project_cards = driver.find_elements(By.CLASS_NAME, 'bloc_projet_financer')
                
                # If no new projects are loaded or if total projects haven't changed after clicking, break the loop
                if len(project_cards) <= 6 * total_clicks:
                    print("No more projects found or reached limit.")
                    break

            except Exception as e:
                print(f"Error loading more projects: {e}")
                break

    def get_url_of_all_projects(website_url, max_clicks=3):
        load_all_projects(max_clicks=max_clicks)
        # Extract all project URLs after loading more projects
        project_cards = driver.find_elements(By.CLASS_NAME, 'bloc_projet_financer')  # Find all project cards

        project_urls = []  # List to store project URLs

        for card in project_cards:
            try:
                # Extract the URL from the 'onclick' attribute of the project card
                onclick_text = card.get_attribute('onclick')
                
                # The URL is typically embedded like this: "window.location='URL'"
                project_url = onclick_text.split("'")[1]
                
                # Complete the URL by appending it to the base URL
                full_url = f"{website_url}{project_url}"
                
                # Add the URL to the list
                project_urls.append(full_url)
                
                print(f"Found project URL: {full_url}")
            except Exception as e:
                print(f"Failed to extract URL from card: {e}")

        
        # write the project URLs to a file for later use if not already present in the file
        with open('project_urls.txt', 'r+') as f:
            # Read the existing URLs in the file
            existing_urls = f.read().splitlines()
            
            # Loop through the new URLs and write them if not already present
            for url in project_urls:
                if url not in existing_urls:
                    f.write(url + '\n')
                    print(f"URL added: {url}")
                else:
                    print(f"URL already present in file: {url}")

        print(f"Total project URLs found: {len(project_urls)}")

        return project_urls


    # Function to monitor the download directory
    def wait_for_download(download_dir, timeout=30):
        print("Waiting for download to complete...")
        start_time = time.time()
        while True:
            files = os.listdir(download_dir)
            if any(fname.endswith('.pdf') for fname in files):
                # Confirm that the file is fully downloaded by checking the file size stability
                time.sleep(1)  # A short wait for file stabilization
                return True
            if time.time() - start_time > timeout:
                print("Download timed out!")
                return False
            time.sleep(1)


    # Function to download the FICI file using requests and Selenium's session cookies
    def download_fici(url):
        print(f"Navigating to project URL: {url}")
        
        # Navigate to the project page
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(2)

        try:
            # Find the FICI download link using the button's 'href' or button text
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn[href*='telecharger_fici.php']"))
            )
            
            # Extract the link to the FICI file
            fici_link = download_button.get_attribute('href')

            print(f'Downloading FICI from: {fici_link}')
            
            # Get cookies from the Selenium session
            selenium_cookies = driver.get_cookies()
            
            # Convert the cookies to a format that can be used by the requests library
            cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
            
            # Use requests to download the PDF directly with Selenium's cookies
            response = requests.get(fici_link, cookies=cookies)
            
            if response.status_code == 200:
                pdf_filename = os.path.join(download_dir, f'fici_{url.split("/")[-1]}.pdf')  # Save file with unique name
                with open(pdf_filename, 'wb') as f:
                    f.write(response.content)
                print(f"Successfully downloaded to: {pdf_filename}")
            else:
                print(f"Failed to download FICI from {fici_link}: Status code {response.status_code}")
            
            # Wait a bit before going to the next URL
            time.sleep(2)
            
        except Exception as e:
            print(f"Failed to download FICI from {url}: {e}")


    # Define a function to scrape the text from a project page
    def scrape_project_text(url, output_dir="project_txt_files"):
        try:
            # Go to the project page
            driver.get(url)
            time.sleep(1)  # Wait for the page to load
            
            # Extract relevant text from the page
            # You can modify this depending on how the text is structured on the page.
            # Example: finding all text inside the main content area
            project_text = driver.find_element(By.CSS_SELECTOR, "body").text
            
            # Create an output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Extract project ID or unique name for the file
            project_id = url.split('-')[-1]
            file_path = os.path.join(output_dir, f"project_{project_id}.txt")
            
            # Write the extracted text to a .txt file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(project_text)
            
            print(f"Successfully scraped and saved project {project_id} to {file_path}")

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")


    # Now you have the list of project URLs
    website_url = "https://www.pretup.fr/"

    project_urls = get_url_of_all_projects(website_url=website_url, max_clicks=1) # Change max_clicks to scrape past projects

    # Uncomment the following lines to load project URLs from a file if URL scraping was already done
    # with open('project_urls.txt', 'r') as f:
    #     project_urls = f.read().splitlines()

    # Loop through all project URLs and download the FICI file for each one
    for project_url in project_urls:

        output_dir = "project_txt_files"  # Output directory for saving project text files
        project_id = project_url.split('-')[-1]
        file_path = os.path.join(output_dir, f"project_{project_id}.txt")
        # Check if the file already exists
        if os.path.exists(file_path):
            print(f"File already exists for project {project_id}, skipping...")
            continue # Skip to the next project
        else:
            # download_fici(project_url) # To download PDFs for recent projects
            scrape_project_text(project_url) # To scrape the HTML of URLs

    # Close the browser when done
    driver.quit()


if __name__ == "__main__":
    main()
