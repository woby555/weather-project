"""
Description: Python Project Milestone 1 - Weather Scraper
Author: Jake Licmo
Date: 2025-03-28
"""
import requests
from html.parser import HTMLParser
from datetime import datetime, timedelta
import time

class WeatherScraper(HTMLParser):
    """
     Scrapes historical daily weather data (Max, Min, Mean) from Environment Canada's climate data website.
    """

    def __init__(self, base_url, start_date, earliest_date=None):
        """
        Initializes the WeatherScraper with the base URL, start date, and earliest date for scraping.
        :param base_url: The base URL for the weather data page.
        :param start_date: The date to start scraping from.
        :param earliest_date: The earliest date to scrape data for. If None, it will scrape until the current date.
        """
        super().__init__()
        self.base_url = base_url
        self.start_date = start_date
        self.earliest_date = earliest_date
        self.weather_data = {}

        # Flags for parsing
        self.in_row = False # <tr> tags
        self.in_td = False # <td> tags
        self.in_abbr = False # <abbr> tags
        self.temp_values = [] # Temporary storage for temperature values
        self.col_count = 0 # Counter to track which temperature value we are on (Max, Min, Mean)
        self.row_date = None 

        # Date tracking for stopping condition, preventing infinite loops
        self.first_row_date_on_page = None
        self.previous_first_row_date = None # To detect repeated month/year (October 1996)

        # Current request context
        self.current_year = None
        self.current_month = None

    def handle_starttag(self, tag, attrs):
        """
        Handles the the opening HTML tags whiel parsing.
        """
        if tag == "tr": # Tracks the start of a new row
            self.in_row = True
            self.temp_values = []
            self.col_count = 0
            self.row_date = None

        elif tag == "td" and self.in_row: # Prepares to parse temperature data
            self.in_td = True

        elif tag == "abbr" and self.in_row: # Prepares to parse the date from the <abbr> tag
            self.in_abbr = True
            for attr in attrs:
                if attr[0] == "title":
                    try:
                        self.row_date = datetime.strptime(attr[1], "%B %d, %Y")
                    except ValueError:
                        self.row_date = None

    def handle_endtag(self, tag):
        """
        Handles the closing HTML tags while parsing.
        """
        if tag == "tr" and self.in_row:
            if self.row_date and len(self.temp_values) == 3: # Checks if we have processed the 3 temperature values
                if not self.first_row_date_on_page: # Used to stop at the earliest date.
                    self.first_row_date_on_page = self.row_date

                date_str = self.row_date.strftime("%Y-%m-%d")
                self.weather_data[date_str] = {
                    "Max": self.temp_values[0],
                    "Min": self.temp_values[1],
                    "Mean": self.temp_values[2]
                }
                print(f"Saved data for {date_str}: {self.weather_data[date_str]}")
            else:
                print("Skipping row due to missing date or temperature data.")
            self.in_row = False # Reset flags

        elif tag == "td":
            self.in_td = False
        elif tag == "abbr":
            self.in_abbr = False

    def handle_data(self, data):
        """
        Extracts and processes the data within the HTML tags.
        """
        clean_data = data.strip() # Strip whitespace

        if self.in_row and self.in_td and self.col_count < 3:
            if clean_data == "M": # Missing data check
                self.temp_values.append(None)
            else:
                try:
                    self.temp_values.append(float(clean_data)) # Convert to float
                except ValueError:
                    self.temp_values.append(None)
            self.col_count += 1

    def scrape(self):
        """
        Initiates the scraping process, moving backward month-by-month from start_date to earliest_date.

        :return: A dictionary containing the scraped weather data.
        """
        current_date = self.start_date

        while True:
            if self.earliest_date and current_date < self.earliest_date:
                print(f"Reached earliest target date ({self.earliest_date.strftime('%Y-%m-%d')}). Stopping.")
                break

            self.current_year = current_date.year
            self.current_month = current_date.month

            url = self.base_url.format(year=self.current_year, month=self.current_month)
            print(f"Fetching: {url}")
            response = requests.get(url)

            if response.status_code != 200:
                print("Failed to fetch data. Stopping.")
                break

            self.feed(response.text)

            if self.first_row_date_on_page: # Checks if we're looping on the same month/year page.
                if self.previous_first_row_date:
                    if (self.first_row_date_on_page.month == self.previous_first_row_date.month and
                        self.first_row_date_on_page.year == self.previous_first_row_date.year):
                        print(f"Detected repeated month/year ({self.first_row_date_on_page.strftime('%B %Y')}), stopping.")
                        break

                self.previous_first_row_date = self.first_row_date_on_page
            else:
                print("No valid data found on this page. Skipping to previous month.")

            self.first_row_date_on_page = None  # Reset for next page

            # Move to previous month
            first_day_this_month = datetime(self.current_year, self.current_month, 1)
            current_date = first_day_this_month - timedelta(days=1)
            
        return self.weather_data



if __name__ == "__main__":
    today = datetime.today()
    EARLIEST_DATE_EXAMPLE = datetime(2018,1,1)
    BASE_URL = (
        "http://climate.weather.gc.ca/climate_data/daily_data_e.html"
        "?StationID=27174&timeframe=2&StartYear=1840&EndYear={year}"
        "&Day=1&Year={year}&Month={month}#"
    )
    scraper = WeatherScraper(BASE_URL, today, EARLIEST_DATE_EXAMPLE)
    data = scraper.scrape()
    print(data)