import pandas as pd
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
# from scrapeRacePage import scrape_all_pages
# from trainerJockey import scrape_trainer_jockey
# from speedPro import scrape_all_pages_speed_pro
from pastRaces import scrape_pastRaces, extract_dates
from utils import send_email_with_attachments, save_to_csv_with_sheets
from dotenv import load_dotenv
import os
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event
import queue
import signal
import sys

# Global exit event
exit_event = Event()

def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals"""
    print("\nReceived exit signal. Gracefully stopping...")
    exit_event.set()
    # Wait a moment for cleanup
    time.sleep(2)
    sys.exit(0)

def format_time(seconds):
    """Format seconds into hours, minutes, seconds"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def create_driver():
    """Create and configure a Chrome WebDriver instance"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-images')  # Disable images to speed up loading
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)  # Set page load timeout
    return driver

def save_worker(save_queue, stop_event):
    """Worker thread for saving files"""
    while not stop_event.is_set() or not save_queue.empty():
        try:
            # Check if we should exit
            if exit_event.is_set():
                break
                
            # Get data from queue with timeout
            data = save_queue.get(timeout=1)
            if data is None:
                continue
                
            file_path, dataframes = data
            # Ensure we have valid dataframes
            if dataframes:
                # Ensure at least one sheet is visible
                has_visible_sheet = False
                for df in dataframes:
                    if not df.empty:
                        has_visible_sheet = True
                        break
                
                if not has_visible_sheet:
                    # If all dataframes are empty, create a dummy sheet
                    dataframes.append(pd.DataFrame({'Note': ['No data available']}))
                
                try:
                    save_to_csv_with_sheets(dataframes, file_path, pd)
                except Exception as e:
                    print(f"Error saving file {file_path}: {e}")
            
            save_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error in save worker: {e}")
            save_queue.task_done()

def scrape_date(date_info, folder_path, pastRacesUrl, lock, save_queue):
    """Scrape data for a single date"""
    date, index, total_dates = date_info
    driver = create_driver()
    try:
        # Check if we should exit
        if exit_event.is_set():
            return False
            
        formatted_date = date.replace('/', '%2F')
        date_url = f"{pastRacesUrl}?RaceDate={formatted_date}"
        date_output_file = os.path.join(folder_path, f'past_races_data_{date.replace("/", "-")}.xlsx')
        
        with lock:
            print(f"\nScraping data for date: {date}")
            print(f"Progress: {index}/{total_dates} dates ({index/total_dates*100:.1f}%)")
            print("Press Ctrl+C to stop the process")
        
        # Get the dataframes from scrape_pastRaces
        dataframes = scrape_pastRaces(driver, date_url, By, pd, date_output_file)  # Pass the file path
        
        # Add to save queue if we have dataframes
        if dataframes and not exit_event.is_set():
            # Ensure we have valid dataframes
            valid_dataframes = []
            for df in dataframes:
                if df is not None and not df.empty:
                    valid_dataframes.append(df)
            
            if valid_dataframes:
                save_queue.put((date_output_file, valid_dataframes))
        
        return True
    except Exception as e:
        with lock:
            print(f"Error scraping date {date}: {e}")
        return False
    finally:
        driver.quit()

def main(send_email, crawl_all_dates, max_workers=4):
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Setting up web driver, please wait...")
    print("Press Ctrl+C at any time to stop the process")
    
    # Load environment variables
    load_dotenv()

    # Get today's date in YYYY-MM-DD format
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Create folder for today's data.
    folder_path = f'Data/{today_date}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Create a queue for saving files and a stop event
    save_queue = queue.Queue()
    stop_event = Event()

    try:
        # print("Attempting racecard scraping...")
        # raceUrl = 'https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx'
        # raceOutputFile = os.path.join(folder_path, f'race_data_{today_date}.xlsx')
        # scrape_all_pages(driver, raceUrl, By, pd, raceOutputFile)
        # print("Finished racecard scraping.")

        # print("Attempting trainer scraping...")
        # trainerUrl = 'https://racing.hkjc.com/racing/information/English/Trainers/TrainerRanking.aspx'
        # trainerOutputFile = os.path.join(folder_path, f'trainer_data_{today_date}.xlsx')
        # scrape_trainer_jockey(driver, trainerUrl, By, pd, trainerOutputFile)
        # print("Finished trainer scraping.")

        # print("Attempting jockey scraping...")
        # jockeyUrl = 'https://racing.hkjc.com/racing/information/English/Jockey/JockeyRanking.aspx'
        # jockeyOutputFile = os.path.join(folder_path, f'jockey_data_{today_date}.xlsx')
        # scrape_trainer_jockey(driver, jockeyUrl, By, pd, jockeyOutputFile)
        # print("Finished jockey scraping.")

        # print("Attempting Speed Pro scraping...")
        # speedProUrl = 'https://racing.hkjc.com/racing/speedpro/english/formguide/formguide.html'
        # speedProOutputFile = os.path.join(folder_path, f'speed_pro_data_{today_date}.xlsx')
        # scrape_all_pages_speed_pro(driver, speedProUrl, By, pd, speedProOutputFile)
        # print("Finished Speed Pro scraping.")

        print("Attempting to extract all past race dates.")
        driver = create_driver()
        allDatesUrl = 'https://racing.hkjc.com/racing/information/English/racing/LocalResults.aspx'
        allDates = extract_dates(driver, By, pd, allDatesUrl)
        if allDates:
            save_to_csv_with_sheets(allDates, 'Data/all-past-dates.xlsx', pd)
        else:
            print("Unable to save past race dates.")

        print("Attempting Past Races scraping...")
        pastRacesUrl = 'https://racing.hkjc.com/racing/information/English/racing/LocalResults.aspx'
        
        if crawl_all_dates:
            # Read all dates from the file
            try:
                dates_df = pd.read_excel('Data/all-past-dates.xlsx')
                dates = dates_df['Dates'].tolist()
                total_dates = len(dates)
                print(f"Found {total_dates} dates to scrape")
                
                start_time = time.time()
                lock = Lock()
                
                # Start save worker
                import threading
                save_thread = threading.Thread(target=save_worker, args=(save_queue, stop_event))
                save_thread.start()
                
                # Prepare date information for parallel processing
                date_info_list = [(date, i+1, total_dates) for i, date in enumerate(dates)]
                
                # Use ThreadPoolExecutor for parallel processing
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [executor.submit(scrape_date, date_info, folder_path, pastRacesUrl, lock, save_queue) 
                             for date_info in date_info_list]
                    
                    # Wait for all tasks to complete or until exit signal
                    for future in as_completed(futures):
                        if exit_event.is_set():
                            print("\nStopping all workers...")
                            executor.shutdown(wait=False)
                            break
                        future.result()  # This will raise any exceptions that occurred
                
                # Wait for all files to be saved
                if not exit_event.is_set():
                    save_queue.join()
                stop_event.set()
                save_thread.join()
                
                if not exit_event.is_set():
                    total_time = time.time() - start_time
                    print(f"\nTotal scraping time: {format_time(total_time)}")
                else:
                    print("\nProcess stopped by user")
                
            except Exception as e:
                print(f"Error during parallel scraping: {e}")
                stop_event.set()
                save_thread.join()
        else:
            # Use the default URL without specific date
            pastRacesOutputFile = os.path.join(folder_path, f'past_races_data_{today_date}.xlsx')
            scrape_pastRaces(driver, pastRacesUrl, By, pd, pastRacesOutputFile)
        
        print("Finished Past Races scraping.")

        if send_email and not exit_event.is_set():
            print("Sending data via email...")
            # Send email with the files
            sender_email = os.getenv('SENDER_EMAIL')
            receiver_email = os.getenv('RECEIVER_EMAIL')
            subject = f"Today's Horse Racing Information - {today_date}"
            body = "Please find attached the scraped data files."
            
            # Get all files in the folder if crawling all dates
            if crawl_all_dates:
                attachments = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx')]
            else:
                attachments = [os.path.join(folder_path, f'past_races_data_{today_date}.xlsx')]
                
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            login = sender_email
            password = os.getenv('EMAIL_PASSWORD')

            print("Sending email with attachments...")
            send_email_with_attachments(
                sender_email, receiver_email, subject, body, attachments, smtp_server, smtp_port, login, password
            )
            print("Email sent successfully.")
        else:
            print("Data will not be sent via email.")

    finally:
        # Quit the driver
        driver.quit()
        stop_event.set()
        exit_event.set()

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Process and optionally send data via email.")
    
    # Add argument for sending email
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Include this flag to send the data via email."
    )
    
    # Add argument for crawling all dates
    parser.add_argument(
        "--crawl-all-dates",
        action="store_true",
        help="Include this flag to crawl all dates from all-past-dates.xlsx"
    )
    
    # Add argument for number of parallel workers
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers to use (default: 4)"
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the main function with the parsed arguments
    main(args.send_email, args.crawl_all_dates, args.workers)
