import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from scrapeRacePage import scrape_all_pages
from trainerJockey import scrape_trainer_jockey
from speedPro import scrape_all_pages_speed_pro
from utils import send_email_with_attachments
from dotenv import load_dotenv
import os

def main():
    # Initialize WebDriver for Chrome
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode (optional)
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')

    # driver = webdriver.Chrome(options=options)  # Ensure ChromeDriver is in your PATH

    load_dotenv()
    try:
        print("Attempting racecard scraping...")
        raceUrl = 'https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx'
        raceOutputFile = 'race_data.xlsx'
        # scrape_all_pages(driver, raceUrl, By, pd, raceOutputFile)
        print("Finished racecard scraping.")

        print("Attempting trainer scraping...")
        trainerUrl = 'https://racing.hkjc.com/racing/information/English/Trainers/TrainerRanking.aspx'
        trainerOutputFile = 'trainer_data.xlsx'
        # scrape_trainer_jockey(driver, trainerUrl, By, pd, trainerOutputFile)
        print("Finished trainer scraping.")

        print("Attempting jockey scraping...")
        jockeyUrl = 'https://racing.hkjc.com/racing/information/English/Jockey/JockeyRanking.aspx'
        jockeyOutputFile = 'jockey_data.xlsx'
        # scrape_trainer_jockey(driver, jockeyUrl, By, pd, jockeyOutputFile)
        print("Finished jockey scraping.")

        print("Attempting Speed Pro scraping...")
        speedProUrl = 'https://racing.hkjc.com/racing/speedpro/english/formguide/formguide.html'
        speedProOutputFile = 'speed_pro_data.xlsx'
        # scrape_all_pages_speed_pro(driver, speedProUrl, By, pd, speedProOutputFile)
        print("Finished Speed Pro scraping.")

        # Send email with the files
        sender_email = os.getenv('SENDER_EMAIL')
        receiver_email = os.getenv('RECEIVER_EMAIL')
        subject = "Scraped Data Files"
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

    finally:
        # Quit the driver
        # driver.quit()
        print('done')


if __name__ == "__main__":
    main()
