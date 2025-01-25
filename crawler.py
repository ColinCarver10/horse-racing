import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from scrapeRacePage import scrape_all_pages
from trainerJockey import scrape_trainer_jockey
from speedPro import scrape_all_pages_speed_pro

def main():
    # Initialize WebDriver for Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (optional)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)  # Ensure ChromeDriver is in your PATH
    try:
        print("Attempting racecard scraping...")
        raceUrl = 'https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx'
        scrape_all_pages(driver, raceUrl, By, pd)
        print("Finished racecard scraping.")

        print("Attempting trainer scraping...")
        trainerUrl = 'https://racing.hkjc.com/racing/information/English/Trainers/TrainerRanking.aspx'
        scrape_trainer_jockey(driver, trainerUrl, By, pd)
        print("Finished trainer scraping.")

        print("Attempting jockey scraping...")
        jockeyUrl = 'https://racing.hkjc.com/racing/information/English/Jockey/JockeyRanking.aspx'
        scrape_trainer_jockey(driver, jockeyUrl, By, pd)
        print("Finished jockey scraping.")

        print("Attempting Speed Pro scraping...")
        speedProUrl = 'https://racing.hkjc.com/racing/speedpro/english/formguide/formguide.html'
        scrape_all_pages_speed_pro(driver, speedProUrl, By, pd)
        print("Finished Speed Pro scraping.")

    finally:
        # Quit the driver
        driver.quit()


if __name__ == "__main__":
    main()
