"""
Description: Main script to demonstrate milestone 1 scripts.
Author: Jake Licmo
Date: 2025-03-28
"""
from datetime import datetime
from scrape_weather import WeatherScraper
from db_operations import DBOperations

BASE_URL = (
    "http://climate.weather.gc.ca/climate_data/daily_data_e.html"
    "?StationID=27174&timeframe=2&StartYear=1840&EndYear={year}"
    "&Day=1&Year={year}&Month={month}#"
)

def main():
    """
    Main function to demonstrate the functionality of 
    the weather scraper and database operations.
    """
    today = datetime.today()
    earliest_date = datetime(2022, 1, 1)

    scraper = WeatherScraper(BASE_URL, today, earliest_date.date())
    raw_data = scraper.scrape()

    db = DBOperations()

    # Purge data example
    # print("Purging old data from the database...")
    # db.purge_data()

   # db.save_data(raw_data)

    print("\nSample data fetched from DB:")
    records = db.fetch_data("Winnipeg")
    for row in records[:15]:
        print(row)

if __name__ == "__main__":
    main()
