from utils import save_to_csv_with_sheets
def scrape_trainer_jockey(driver, url, By, pd, file_name):
    """
    Scrapes the trainer ranking table from the provided URL.
    
    Args:
        driver: Selenium WebDriver instance.
        url (str): URL to scrape the trainer ranking data from.
        By: Selenium By module (passed from main).
        pd: pandas module (passed from main).
    
    Returns:
        pd.DataFrame: A pandas DataFrame containing the trainer ranking data.
    """
    driver.get(url)
    headers = []
    rows = []

    try:
        # Locate the table by its ID
        table = driver.find_element(By.ID, 'innerContent')
        
        # Locate the inner table
        inner_table = table.find_elements(By.TAG_NAME, 'table')[1]

        # Extract table headers from the inner table's <thead>
        inner_thead = inner_table.find_element(By.TAG_NAME, 'thead')
        inner_tr = inner_thead.find_elements(By.TAG_NAME, 'tr')[1]
        headers = [td.text.strip() for td in inner_tr.find_elements(By.TAG_NAME, 'td') if td.text.strip()]

        # Extract table rows from the inner table's <tbody>
        inner_tbody = inner_table.find_element(By.TAG_NAME, 'tbody')
        for tr in inner_tbody.find_elements(By.TAG_NAME, 'tr'):
            row = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, 'td') if td.text.strip()]
            if row:  # Only append non-empty rows
                rows.append(row)


        #Save to csv
        df = pd.DataFrame(rows, columns=headers)
        save_to_csv_with_sheets([df], file_name, pd)

    except Exception as e:
        print(f"Error extracting table data: {e}")
