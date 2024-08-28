from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException

def initialize_browser():
    """Initialize the Selenium browser (Chrome) without headless mode"""
    print("Initializing the browser...")
    options = webdriver.ChromeOptions()
    # Remove headless option so you can see the browser
    browser = webdriver.Chrome(options=options)
    print("Browser initialized.")
    return browser

def handle_cookies(browser):
    """Check and close cookie consent if present"""
    try:
        print("Checking for cookie consent dialog...")
        decline_button = browser.find_element('xpath', "//a[contains(@onclick, 'Cookiebot.dialog.submitDecline()')]")
        decline_button.click()
        print("Cookie consent declined.")
        time.sleep(2)  # Wait for the cookie consent to be dismissed
    except NoSuchElementException:
        print("No cookie consent dialog found.")

def click_toggle_button(browser):
    """Find and click the grid toggle button to change the view to list"""
    try:
        print("Looking for the toggle button...")
        button = browser.find_element(By.XPATH, '//*[@id="__nuxt"]/div/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div[2]/div/div/div[3]')
        print("Toggle button found. Clicking...")
        button.click()
        print("Button clicked, waiting for the list view to load...")
    except ElementClickInterceptedException:
        print("Element click intercepted. Trying to handle the obstruction...")
        handle_cookies(browser)
        button.click()  # Try clicking the button again after handling the obstruction

def get_html_from_browser(browser):
    """Get the page's HTML content after clicking the toggle button"""
    print("Extracting HTML content from the browser...")
    return browser.page_source

def extract_artist_names_from_soup(soup):
    """Extract artist names from the parsed HTML"""
    print("Extracting artist names from the parsed HTML...")
    artist_names = set()
    for artist in soup.select('.act-list__content-name'):
        artist_names.add(artist.text.strip())
    print(f"Extracted {len(artist_names)} unique artist names.")
    return artist_names

def save_to_csv(artist_names, filename='../Spotify_playlist_maker\src\mysterylandArtists.csv'):
    """Save the artist names to a CSV file"""
    print(f"Saving artist names to {filename}...")
    sorted_names = sorted(artist_names)  # Sort the artist names alphabetically
    df = pd.DataFrame(sorted_names, columns=['Artist Name'])
    df.to_csv(filename, index=False)
    print(f"Successfully saved {len(sorted_names)} artist names to {filename}.")

def main():
    url = 'https://www.mysteryland.nl/line-up'
    
    # Step 1: Initialize the browser and load the page
    browser = initialize_browser()
    print(f"Loading page: {url}...")
    browser.get(url)
    
    # Step 2: Wait for the page to load and check for any cookie consent dialog
    time.sleep(3)  # Give the page some time to fully load
    handle_cookies(browser)  # Handle cookie consent if present
    
    # Step 3: Click the grid toggle button
    click_toggle_button(browser)
    
    # Step 4: Wait for the list view to render
    time.sleep(3)  # Adjust this time if needed
    
    # Step 5: Get the updated HTML content and parse it with BeautifulSoup
    html_content = get_html_from_browser(browser)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Step 6: Extract artist names
    artist_names = extract_artist_names_from_soup(soup)
    
    # Step 7: Save the artist names to a CSV file
    save_to_csv(artist_names)
    
    # Step 8: Close the browser
    print("Closing the browser...")
    browser.quit()
    print("Browser closed. Script completed.")

# Call the main function to execute the script
if __name__ == "__main__":
    main()
