from utils import save_to_csv_with_sheets
def scrape_all_pages(driver, url, By, pd, fileName):
    """
    Scrapes all pages linked within the 'racingNum' class, compiles data from each page, 
    and saves it as a CSV file with separate sheets for each page.

    Args:
        driver: Selenium WebDriver instance.
        url (str): Base URL to start scraping from.
        By: Selenium By module.
        pd: pandas module.

    Returns:
        None: Saves the collected data as a CSV file with multiple sheets.
    """
    # Navigate to the base URL
    driver.get(url)

    # Extract all URLs from the 'racingNum' class
    urls = extract_urls_from_racingNum(driver, By)
    urls.insert(0, url)
    
    # Filter out URLs containing 'Racecourse=S1'
    urls = [url for url in urls if 'Racecourse=S1' not in url]

    # Initialize a list to store DataFrames
    all_dataframes = []

    # Scrape each URL and append the resulting DataFrame to the list
    for page_url in urls:
        df = scrape_race(driver, page_url, By, pd)
        if not df.empty:  # Only add non-empty DataFrames
            all_dataframes.append(df)

    # Save all DataFrames to a CSV file with separate sheets
    save_to_csv_with_sheets(all_dataframes, fileName, pd)

def extract_urls_from_racingNum(driver, By):
    """
    Extracts all URLs from <a> tags within elements that have the 'racingNum' class.

    Args:
        driver: Selenium WebDriver instance.
        By: Selenium By module.

    Returns:
        list: A list of URLs (strings) extracted from the <a> tags.
    """
    urls = []

    try:
        # Locate all elements with the class 'racingNum'
        racing_num_elements = driver.find_elements(By.CLASS_NAME, 'racingNum')
        
        # Iterate over each element and find <a> tags within
        for element in racing_num_elements:
            links = element.find_elements(By.TAG_NAME, 'a')
            for link in links:
                url = link.get_attribute('href')
                if url:  # Ensure the URL is not None
                    urls.append(url)

    except Exception as e:
        print(f"Error extracting URLs: {e}")

    return urls


def scrape_race(driver, url, By, pd):
    """
    Scrapes the table with the inner table structure from the provided URL.
    
    Args:
        driver: Selenium WebDriver instance.
        url (str): URL to scrape the table data from.
    
    Returns:
        pd.DataFrame: A pandas DataFrame containing the scraped table data.
    """
    driver.get(url)
    headers = []
    rows = []
    
    race_info = get_race_info(driver, pd, By)
    rows.append(race_info)

    try:
        # Locate the table by its ID
        table = driver.find_element(By.ID, 'racecardlist')
        
        # Locate the inner table
        inner_table = table.find_element(By.TAG_NAME, 'table')

        # Extract table headers from the inner table's <thead>
        inner_thead = inner_table.find_element(By.TAG_NAME, 'thead')
        headers = [th.text.strip() for th in inner_thead.find_elements(By.TAG_NAME, 'td') if th.text.strip()]
        headers.remove("Colour")
        # Extract table rows from the inner table's <tbody>
        inner_tbody = inner_table.find_element(By.TAG_NAME, 'tbody')
        for tr in inner_tbody.find_elements(By.TAG_NAME, 'tr'):
            row = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, 'td') if td.value_of_css_property('display') != 'none']
            if row:  # Only append non-empty rows
                row.pop(2) #Remove colour
                rows.append(row)
        # Create DataFrame from the extracted data
        df = pd.DataFrame(rows, columns=headers)
        return df

    except Exception as e:
        print(f"Error scraping the table: {e}")

        
def get_race_info(driver, pd, By):
   try:
       # Find element with specific style
       race_detail_element = driver.find_element(By.CLASS_NAME, "f_fs13")
       
       if race_detail_element:
           # Filter lines containing 'turf' or 'all weather track'
           filtered_line = [subline.strip() for line in race_detail_element.text.split('\n') 
                           if 'turf' in line.lower() or 'all weather track' in line.lower() 
                           for subline in line.split(',')]
           
           # Return filtered lines with additional empty strings to maintain original return structure
           return ['Race Details'] + filtered_line + [''] * (10 - len(filtered_line))
       
       return ['No Race Details Found'] + [''] * 10
   
   except Exception as e:
       print(f"Error extracting race details: {e}")
       return ['No Race Details Found'] + [''] * 10
