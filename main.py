from datetime import datetime
from scrape_weather import WeatherScraper
from db_operations import DBOperations

BASE_URL = (
    "http://climate.weather.gc.ca/climate_data/daily_data_e.html"
    "?StationID=27174&timeframe=2&StartYear=1840&EndYear={year}"
    "&Day=1&Year={year}&Month={month}#"
)

def transform_data(raw_data, location="Winnipeg"):
    transformed = {} 
    for date_str, temps in raw_data.items():
        transformed[date_str] = {
            'location': location,
            'min_temp': temps.get('Min'),
            'max_temp': temps.get('Max'),
            'avg_temp': temps.get('Mean')
        }
    return transformed

def main():
    # today = datetime.today()
    # earliest_date = datetime(2018, 1, 1)

    # scraper = WeatherScraper(BASE_URL, today, earliest_date)
    # raw_data = scraper.scrape()
    # parsed_data = transform_data(raw_data)

    db = DBOperations()

    # print("Purging old data from the database...")
    # db.purge_data()

    # db.save_data(parsed_data)
    print("\nSample data fetched from DB:")
    records = db.fetch_data("Winnipeg")
    for row in records[:100]:
        print(row)

if __name__ == "__main__":
    main()
