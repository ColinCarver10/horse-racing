from utils import save_to_csv_with_sheets, wait_for_element
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

    # Create a cache to store horse details to avoid repeat requests
    # This will significantly speed up the process if the same horse appears in multiple races
    horse_details_cache = {}

    # Scrape each URL and append the resulting DataFrame to the list
    urls = [url for url in urls if 'Racecourse=S1' not in url]
    for page_url in urls:
        # Navigate to the race page
        driver.get(page_url)
        
        # Extract race number from URL for logging
        race_num = page_url.split('RaceNo=')[-1] if 'RaceNo=' in page_url else '1'
        
        df = scrape_race(driver, page_url, By, pd, horse_details_cache)
        if not df.empty:  # Only add non-empty DataFrames
            all_dataframes.append(df)
        else:
            print(f"Failed to scrape Race {race_num}")
    
    # Save all DataFrames to a CSV file with separate sheets
    save_to_csv_with_sheets(all_dataframes, file_name, pd)
    
    print(f"Scraped details for {len(horse_details_cache)} unique horses")

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

def scrape_race(driver, page_url, By, pd, horse_details_cache=None):
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
        
        # Add headers for race tab info and horse details
        additional_headers = ['Class/Distance', 'Going', 'Course', 'Total Time (sec)', 'Sectional Times', 'Horse Age', 'Horse Sex']
        headers.extend(additional_headers)

        inner_tbody = section.find_element(By.TAG_NAME, 'tbody')
        rows = inner_tbody.find_elements(By.TAG_NAME, 'tr')
        
        # First pass: collect all horse links and their cell text
        horse_data = []
        for tr in rows:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if len(tds) > 2:  # Check if we have enough columns
                try:
                    # Get all cell text first
                    row_text = [td.text.strip() for td in tds if td.value_of_css_property('display') != 'none']
                    horse_link_element = tds[2].find_element(By.TAG_NAME, 'a')
                    horse_link = horse_link_element.get_attribute('href')
                    horse_data.append((horse_link, row_text))
                except Exception as link_err:
                    print(f"No horse link found: {link_err}")
                    horse_data.append((None, row_text))
        
        # Second pass: process rows and get horse details
        processed_rows = []
        for horse_link, row_text in horse_data:
            if row_text:  # Only process non-empty rows
                horse_age = ''
                horse_sex = ''
                
                if horse_link:
                    try:
                        horse_details = extract_horse_details(driver, horse_link, By)
                        horse_age = horse_details.get('age', '')
                        horse_sex = horse_details.get('sex', '')
                    except Exception as detail_err:
                        print(f"Error extracting horse details: {detail_err}")
                
                # Add race tab columns (empty for regular rows) and horse details
                row_text.extend([''] * (len(additional_headers) - 2) + [horse_age, horse_sex])
                processed_rows.append(row_text)
        
        # Create DataFrame from the extracted data
        if processed_rows:
            df = pd.DataFrame(processed_rows, columns=headers)
            return df
        else:
            return pd.DataFrame()

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


def extract_horse_details(driver, horse_url, By):
    """
    Navigates to a horse's details page and extracts age and sex information.
    
    Args:
        driver: Selenium WebDriver instance.
        horse_url (str): URL to the horse's details page.
        By: Selenium By module.
        
    Returns:
        dict: Dictionary containing the horse's age and sex.
    """
    # Store the current page URL to return to after extraction
    current_url = driver.current_url
    
    # Navigate to the horse details page
    driver.get(horse_url)
    horse_details = {}
    
    try:
        # Wait for the page to load - use explicit wait
        horse_info_section = wait_for_element(driver, By.CLASS_NAME, "horseProfile", timeout=5)
        profile_text = horse_info_section.text
        
        # Extract age from the text
        age_line = [line for line in profile_text.split('\n') if 'Country of Origin / Age' in line]
        if age_line:
            age = age_line[0].split('/')[-1].strip()
            horse_details['age'] = age
            
        # Extract sex from the text
        sex_line = [line for line in profile_text.split('\n') if 'Colour / Sex' in line]
        if sex_line:
            sex_parts = sex_line[0].split(':')[-1].strip()
            # Take what's after the last '/' if it exists
            if '/' in sex_parts:
                sex = sex_parts.split('/')[-1].strip()
            else:
                sex = sex_parts
            horse_details['sex'] = sex
            
    except Exception as e:
        print(f"Error extracting horse details: {e}")
    
    finally:
        # Navigate back to the original page
        driver.get(current_url)
    
    return horse_details
