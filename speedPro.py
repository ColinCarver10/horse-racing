from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils import save_to_csv_with_sheets

def scrape_all_pages_speed_pro(driver, url, By, pd, fileName):
    """
    Scrapes all pages linked within the 'race-nav' class, compiles data from each page, 
    and saves it as an Excel file with separate sheets for each page.

    Args:
        driver: Selenium WebDriver instance.
        url (str): Base URL to start scraping from.
        By: Selenium By module.
        pd: pandas module.

    Returns:
        None: Saves the collected data as an Excel file with multiple sheets.
    """
    # Navigate to the base URL
    driver.get(url)

    # Extract all URLs from the 'race-nav' class
    urls = extract_urls_from_race_nav(driver, By)

    # Initialize a list to store DataFrames
    all_dataframes = []

    # Scrape each URL and append the resulting DataFrame to the list
    for page_url in urls:
        df = scrape_speed_pro_page(driver, page_url, By, pd)
        if not df.empty:  # Only add non-empty DataFrames
            all_dataframes.append(df)

    # Save all DataFrames to an Excel file with separate sheets
    save_to_csv_with_sheets(all_dataframes, fileName, pd)

def scrape_speed_pro_page(driver, url, By, pd):
    """
    Scrapes data from the page with a 'datatable' structure.

    Args:
        driver: Selenium WebDriver instance.
        url (str): URL of the page to scrape.

    Returns:
        pd.DataFrame: A single DataFrame containing all subtables combined.
    """
    driver.get(url)
    master_headers = []
    all_data = []  # Will hold all rows of data

    try:
        main_table = wait_for_element(driver, By.CLASS_NAME, "datatable", timeout=15)

        if not main_table:
            print("Failed to load the datatable.")
            return pd.DataFrame()  # Return an empty DataFrame

        # Extract master headers (first row of the table)
        master_headers = [th.text.strip() for th in main_table.find_elements(By.TAG_NAME, 'th') if th.text.strip()]

        # Identify the rows (subtables are nested below the master headers)
        rows = main_table.find_elements(By.TAG_NAME, 'tr')

        # Initialize variables for tracking subtable start row and current subtable data
        current_subtable = []
        subheaders = []

        # Iterate through the rows to identify and separate subtables
        for row in rows:
            row_data = [td.text.strip() for td in row.find_elements(By.TAG_NAME, 'td')]
            
            if len(row_data) > 0:
                if row.get_attribute("class") == 'comment':
                    current_subtable.append([row_data[0], '', ''] + row_data[1:])
                else:
                    # Append data rows under the current subheader
                    current_subtable.append(row_data)
        
        return pd.DataFrame(current_subtable, columns=master_headers)

    except Exception as e:
        print(f"Error scraping the table: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    
def extract_urls_from_race_nav(driver, By):
    """
    Extracts all URLs from the 'race-nav' class elements on the page.

    Args:
        driver: Selenium WebDriver instance.
        By: Selenium By module.

    Returns:
        list: A list of URLs extracted from the 'race-nav' elements.
    """
    try:
        # Locate the race-nav element
        race_nav_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'race-nav'))
        )
        
        # Extract all anchor tags within the race-nav element
        links = race_nav_element.find_elements(By.TAG_NAME, 'a')
        
        # Get the href attribute from each link
        urls = [link.get_attribute('href') for link in links if link.get_attribute('href') is not None]
        
        return urls
    except TimeoutException:
        print("Timeout while waiting for the race-nav element.")
        return []

def wait_for_element(driver, by, value, timeout=10):
    """
    Waits for an element to be present in the DOM and visible.

    Args:
        driver: Selenium WebDriver instance.
        by: The locator strategy (e.g., By.ID, By.CLASS_NAME).
        value: The value of the locator.
        timeout (int): Maximum wait time in seconds.

    Returns:
        WebElement: The located element.

    Raises:
        TimeoutException: If the element is not found within the timeout.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"Timeout: Element with {by} = {value} not found within {timeout} seconds.")
        return None
