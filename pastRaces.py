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

    # Extract all URLs from the race navigation buttons
    urls = extract_urls(driver, By)
    urls.insert(0, url)
    
    print(f"Found {len(urls)} race URLs to scrape")

    # Initialize a list to store DataFrames
    all_dataframes = []

    # Scrape each URL and append the resulting DataFrame to the list
    urls = [url for url in urls if 'Racecourse=S1' not in url]
    for page_url in urls:
        # Navigate to the race page
        driver.get(page_url)
        
        # Extract race number from URL for logging
        race_num = page_url.split('RaceNo=')[-1] if 'RaceNo=' in page_url else '1'
        
        df = scrape_race(driver, page_url, By, pd)
        if not df.empty:  # Only add non-empty DataFrames
            all_dataframes.append(df)
        else:
            print(f"Failed to scrape Race {race_num}")
    
    # Save all DataFrames to a CSV file with separate sheets
    save_to_csv_with_sheets(all_dataframes, file_name, pd)

def extract_urls(driver, By):
    """
    Extracts URLs from the 'top_races' div containing all race links, excluding those with 'ResultsAll'.

    Args:
        driver: Selenium WebDriver instance.
        By: Selenium By module.

    Returns:
        list: A list of URLs (strings) extracted from the links.
    """
    urls = []

    try:
        # Find the top_races div
        top_races_div = driver.find_element(By.CLASS_NAME, "top_races")
        
        # Get all <a> tags within the div
        links = top_races_div.find_elements(By.TAG_NAME, "a")
        
        # Extract URLs from each link
        for link in links:
            url = link.get_attribute('href')
            if url and 'ResultsAll' not in url:  # Ensure the URL is not None and does not contain 'ResultsAll'
                urls.append(url)

        print(f"Found {len(urls)} race links in top_races div (excluding 'ResultsAll')")

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
        
        #Locate race tab data
        race_tab_info = get_race_tab(driver, pd, By)
        if race_tab_info and race_tab_info[0] != 'No Race Details Found':
            # Add race tab info to race_info
            race_info.extend(race_tab_info)
        
        rows.append(race_info)

        #Locate race data
        section = table.find_element(By.CLASS_NAME, 'performance')
        inner_thead = section.find_element(By.TAG_NAME, 'thead')
        headers = [th.text.strip() for th in inner_thead.find_elements(By.TAG_NAME, 'td') if th.text.strip()]
        
        # Add headers for race tab info
        additional_headers = ['Class/Distance', 'Going', 'Course', 'Total Time (sec)', 'Sectional Times']
        headers.extend(additional_headers)

        inner_tbody = section.find_element(By.TAG_NAME, 'tbody')

        for tr in inner_tbody.find_elements(By.TAG_NAME, 'tr'):
            row = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, 'td') if td.value_of_css_property('display') != 'none']
            if row:  # Only append non-empty rows
                # Add empty values for the race tab columns since they only apply to the race info row
                row.extend([''] * len(additional_headers))
                rows.append(row)

        # Create DataFrame from the extracted data
        df = pd.DataFrame(rows, columns=headers)
        return df

    except Exception as e:
        print(f"Error extracting table data: {e}")
        return pd.DataFrame()

def get_race_info(driver, pd, By):
   try:
       # Find element with specific style
       race_detail_element = driver.find_element(By.CLASS_NAME, "raceMeeting_select")
       
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
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        # Skip the empty row (first row)
        # Class and distance are in the second row, first td
        class_distance = rows[1].find_elements(By.TAG_NAME, "td")[0].text
        
        # Going is in the second row
        going = rows[1].find_elements(By.TAG_NAME, "td")[2].text
        
        # Course is in the third row
        course = rows[2].find_elements(By.TAG_NAME, "td")[2].text
        
        # Time is in the fourth row
        time_cells = rows[3].find_elements(By.TAG_NAME, "td")
        # Get all time values (skipping the first two cells which contain labels)
        time_values = [cell.text.strip('()') for cell in time_cells[2:] if cell.text.strip()]
        
        # Get the final time (last value)
        final_time = time_values[-1]
        minutes, seconds = final_time.split(":")
        total_seconds = float(minutes) * 60 + float(seconds)
        
        # Sectional times are in the fifth row
        sectional_cells = rows[4].find_elements(By.TAG_NAME, "td")[2:]
        sectional_times = []
        for cell in sectional_cells:
            main_time = cell.text.split('\n')[0].strip()  # Get the main time before the blue numbers
            if main_time:
                sectional_times.append(main_time)

        results = [class_distance, going, course, total_seconds, sectional_times]
        return results

    except Exception as e:
        print(f"Error extracting race details: {e}")
        return ['No Race Details Found'] + [''] * 11
