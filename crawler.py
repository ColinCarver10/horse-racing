import pandas as pd
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from scrapeRacePage import scrape_all_pages
from trainerJockey import scrape_trainer_jockey
from speedPro import scrape_all_pages_speed_pro
from utils import send_email_with_attachments
from dotenv import load_dotenv
import os
from datetime import datetime

def main(send_email):
    # Initialize WebDriver for Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (optional)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)  # Ensure ChromeDriver is in your PATH

    # Load environment variables
    load_dotenv()

    # Get today's date in YYYY-MM-DD format
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Create folder for today's data.
    folder_path = f'Data/{today_date}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    try:
        print("Attempting racecard scraping...")
        raceUrl = 'https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx'
        raceOutputFile = os.path.join(folder_path, f'race_data_{today_date}.xlsx')
        scrape_all_pages(driver, raceUrl, By, pd, raceOutputFile)
        print("Finished racecard scraping.")

        print("Attempting trainer scraping...")
        trainerUrl = 'https://racing.hkjc.com/racing/information/English/Trainers/TrainerRanking.aspx'
        trainerOutputFile = os.path.join(folder_path, f'trainer_data_{today_date}.xlsx')
        scrape_trainer_jockey(driver, trainerUrl, By, pd, trainerOutputFile)
        print("Finished trainer scraping.")

        print("Attempting jockey scraping...")
        jockeyUrl = 'https://racing.hkjc.com/racing/information/English/Jockey/JockeyRanking.aspx'
        jockeyOutputFile = os.path.join(folder_path, f'jockey_data_{today_date}.xlsx')
        scrape_trainer_jockey(driver, jockeyUrl, By, pd, jockeyOutputFile)
        print("Finished jockey scraping.")

        print("Attempting Speed Pro scraping...")
        speedProUrl = 'https://racing.hkjc.com/racing/speedpro/english/formguide/formguide.html'
        speedProOutputFile = os.path.join(folder_path, f'speed_pro_data_{today_date}.xlsx')
        scrape_all_pages_speed_pro(driver, speedProUrl, By, pd, speedProOutputFile)
        print("Finished Speed Pro scraping.")

        if send_email:
            print("Sending data via email...")
            # Send email with the files
            sender_email = os.getenv('SENDER_EMAIL')
            receiver_email = os.getenv('RECEIVER_EMAIL')
            subject = f"Today's Horse Racing Information - {today_date}"
            body = "Please find attached the scraped data files."
            attachments = [raceOutputFile, trainerOutputFile, jockeyOutputFile, speedProOutputFile]
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



if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Process and optionally send data via email.")
    
    # Add argument for sending email
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Include this flag to send the data via email."
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the main function with the parsed argument
    main(args.send_email)
