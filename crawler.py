import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from scrapeRacePage import scrape_all_pages
from trainerJockey import scrape_trainer_jockey
from speedPro import scrape_all_pages_speed_pro
from utils import send_email_with_attachments
from dotenv import load_dotenv
import os
from datetime import datetime

def main():
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

    try:
        print("Attempting racecard scraping...")
        raceUrl = 'https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx'
        raceOutputFile = f'race_data_{today_date}.xlsx'
        scrape_all_pages(driver, raceUrl, By, pd, raceOutputFile)
        print("Finished racecard scraping.")

        print("Attempting trainer scraping...")
        trainerUrl = 'https://racing.hkjc.com/racing/information/English/Trainers/TrainerRanking.aspx'
        trainerOutputFile = f'trainer_data_{today_date}.xlsx'
        scrape_trainer_jockey(driver, trainerUrl, By, pd, trainerOutputFile)
        print("Finished trainer scraping.")

        print("Attempting jockey scraping...")
        jockeyUrl = 'https://racing.hkjc.com/racing/information/English/Jockey/JockeyRanking.aspx'
        jockeyOutputFile = f'jockey_data_{today_date}.xlsx'
        scrape_trainer_jockey(driver, jockeyUrl, By, pd, jockeyOutputFile)
        print("Finished jockey scraping.")

        print("Attempting Speed Pro scraping...")
        speedProUrl = 'https://racing.hkjc.com/racing/speedpro/english/formguide/formguide.html'
        speedProOutputFile = f'speed_pro_data_{today_date}.xlsx'
        scrape_all_pages_speed_pro(driver, speedProUrl, By, pd, speedProOutputFile)
        print("Finished Speed Pro scraping.")

    finally:
        # Quit the driver
        driver.quit()


if __name__ == "__main__":
    main()
