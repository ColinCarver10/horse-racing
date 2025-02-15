from utils import save_to_csv_with_sheets
def scrape_pastRaces(driver, url, By, pd, file_name):
    """
    Scrapes past race data from the provided URL.
    
    Args:
        driver: Selenium WebDriver instance.
        url (str): URL to scrape the trainer ranking data from.
        By: Selenium By module (passed from main).
        pd: pandas module (passed from main).
    
    Returns:
        pd.DataFrame: A pandas DataFrame containing the trainer ranking data.
    """
    driver.get(url)

    # Extract all URLs from the 'racingNum' class
    urls = extract_urls(driver, By)
    urls.insert(0, url)

    # Initialize a list to store DataFrames
    all_dataframes = []

    # Scrape each URL and append the resulting DataFrame to the list
    for page_url in urls:
        df = scrape_race(driver, page_url, By, pd)
        if not df.empty:  # Only add non-empty DataFrames
            all_dataframes.append(df)

    # Save all DataFrames to a CSV file with separate sheets
    save_to_csv_with_sheets(all_dataframes, file_name, pd)

def extract_urls(driver, By):
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
        racing_num_elements = driver.find_elements(By.CLASS_NAME, 'top_races')
        
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

def extract_dates(driver, By, pd, url):
    driver.get(url)

    try:
        date_select_box = driver.find_element(By.TAG_NAME, 'select')
        all_dates = [option.text for option in date_select_box.find_elements(By.TAG_NAME, 'option')]

        if all_dates:
            df = pd.DataFrame(all_dates, columns=["Dates"])
            return [df]
        else:
            print("Unable to extract all past race dates")            
    except Exception as e:
        print(f"Error extracting all past race dates: {e}")

def scrape_race(driver, page_url, By, pd):
    try:
        rows = []
        # Locate the table by its ID
        table = driver.find_element(By.ID, 'innerContent')

        #Locate race date and location
        race_info = get_race_info(driver, pd, By)
        rows.append(race_info)

        #Locate race data
        section = table.find_element(By.CLASS_NAME, 'performance')
        inner_thead = section.find_element(By.TAG_NAME, 'thead')
        headers = [th.text.strip() for th in inner_thead.find_elements(By.TAG_NAME, 'td') if th.text.strip()]

        inner_tbody = section.find_element(By.TAG_NAME, 'tbody')

        for tr in inner_tbody.find_elements(By.TAG_NAME, 'tr'):
            row = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, 'td') if td.value_of_css_property('display') != 'none']
            if row:  # Only append non-empty rows
                rows.append(row)
        # Create DataFrame from the extracted data
        df = pd.DataFrame(rows, columns=headers)
        return df

    except Exception as e:
        print(f"Error extracting table data: {e}")

def get_race_info(driver, pd, By):
   try:
       # Find element with specific style
       race_detail_element = driver.find_element(By.CLASS_NAME, "raceMeeting_select")
       race_tab = get_race_tab(driver, pd, By)
       
       if race_detail_element:
           info = race_detail_element.find_element(By.TAG_NAME, "span").text
           formatted_info = info.replace('Race Meeting:  ', '')
           
           # Return filtered lines with additional empty strings to maintain original return structure
           return ['Race Details'] + [formatted_info] + [''] * (10)
       
       return ['No Race Details Found'] + [''] * 11
   
   except Exception as e:
       print(f"Error extracting race details: {e}")
       return ['No Race Details Found'] + [''] * 11
   
def get_race_tab(driver, pd, By):
    try:
        race_tab = driver.find_element(By.CLASS_NAME, "race_tab")
        table = race_tab.find_element(By.TAG_NAME, "table")

        class_distance = table.find_element(By.XPATH, "//td[contains(text(), 'Class')]").text
        going = table.find_element(By.XPATH, "//td[contains(text(), 'going')]/following-sibling::td[1]").text
        course = table.find_element(By.XPATH, "//td[contains(text(), 'course')]/following-sibling::td[1]").text

        time_str = table.find_element(By.XPATH, "//td[contains(text(), 'course')]/following-sibling::td[3]").text
        time_str = time_str.strip("()")
        minutes, seconds = time_str.split(":")
        total_seconds = int(minutes) * 60 + float(seconds)

        sectional_elements = table.find_elements(By.XPATH, "//tr[td[contains(text(), 'Sectional Time :')]]/td[position()>2]")
        sectional_times = [td.text.split("\n")[0].strip() for td in sectional_elements]

        results = [class_distance, going, course, total_seconds, sectional_times]


    except Exception as e:
       print(f"Error extracting race details: {e}")
       return ['No Race Details Found'] + [''] * 11
