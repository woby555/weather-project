"""
Description: Weather Processor script for managing weather data scraping, 
database operations, and plotting.
Author: Jake Licmo
Date: 2025-04-04
"""
from datetime import timedelta
from datetime import datetime
from scrape_weather import WeatherScraper
from db_operations import DBOperations, DBCM
from plot_operations import PlotOperations

class WeatherProcessor:
    """
    Main class to handle the weather data processing workflow.
    """
    def __init__(self):
        """
        Initializes the WeatherProcessor with necessary components.
        """
        self.scraper = WeatherScraper
        self.db = DBOperations()
        self.plotter = PlotOperations()
        self.base_url = (
            "http://climate.weather.gc.ca/climate_data/daily_data_e.html"
            "?StationID=27174&timeframe=2&StartYear=1840&EndYear={year}"
            "&Day=1&Year={year}&Month={month}#"
        )

    def show_menu(self):
        """
        Displays the main menu options to the user.
        """
        print("\n===== Weather Data Processor =====")
        print("1. Download weather data (scrape & save to DB)")
        print("2. Export current weather data to CSV")
        print("3. Update weather data")
        print("4. Generate box plot (year range)")
        print("5. Generate line plot (month & year)")
        print("6. Exit")

    def run(self):
        """
        Main loop to run the weather data processing program.
        """
        while True:
            self.show_menu()
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                self.download_data()
            elif choice == '2':
                self.csv_export()
            elif choice == '3':
                self.update_data()
            elif choice == '4':
                self.generate_box_plot()
            elif choice == '5':
                self.generate_line_plot()
            elif choice == '6':
                print("Exiting program.")
                break
            elif choice == 'x':  # hidden purge option
                self.purge_all_data()
            else:
                print("Invalid choice. Please try again.\n")

    def download_data(self):
        """
        Performs a full scrape from a user-defined earliest year and stores data in the DB.
        """
        try:
            earliest_year = int(input("Enter earliest year to start scrape (e.g. 2022): "))
            earliest_date = datetime(earliest_year, 1, 1)
            location = "Winnipeg"

            print(f"Scraping weather data from today back to {earliest_date.strftime('%Y-%m-%d')}...")
            scraper = WeatherScraper(self.base_url, datetime.today(), earliest_date.date())
            raw_data = scraper.scrape()

            if raw_data:
                self.db.save_data(raw_data, location)
                print(f"Download complete. {len(raw_data)} records inserted into the database.")
            else:
                print("No data was scraped.")

        except ValueError:
            print("Invalid input. Please enter a numeric year.")

    def csv_export(self):
        """
        Downloads the full weather data from the specified URL and saves it to the database.
        """
        try:
            file_path = input("Enter the output CSV file path (e.g. weather_data/export.csv): ").strip()
            if not file_path.endswith(".csv"):
                file_path += ".csv"
            self.db.export_to_csv(file_path)
        except Exception as e:
            print(f"Failed to export data: {e}")

    def update_data(self):
        """
        Updates the weather data in the database by scraping new data from the web.
        If no data is found in the DB, prompts user to perform a full scrape instead.
        """
        latest_str = self.db.get_latest_date()
        location = "Winnipeg"

        if not latest_str: # Request full scrape if no data in DB
            print("No existing data found in the database.")
            choice = input("Would you like to perform a full scrape and save to DB? (y/n): ").strip().lower()
            if choice == 'y':
                try:
                    earliest_year = int(input("Enter earliest year to start full scrape (e.g. 2022): "))
                    earliest_date = datetime(earliest_year, 1, 1)

                    print(f"Scraping weather data from today back to {earliest_date.strftime('%Y-%m-%d')}...")
                    scraper = WeatherScraper(self.base_url, datetime.today(), earliest_date.date())
                    raw_data = scraper.scrape()

                    if raw_data:
                        self.db.save_data(raw_data, location)
                        print(f"Full scrape complete. {len(raw_data)} records inserted.")
                    else:
                        print("No data was scraped.")
                except ValueError:
                    print("Invalid year input.")
            else:
                print("Update canceled.")
            return

        try: # Finds the latest date in the DB
            latest_date = datetime.strptime(latest_str, "%Y-%m-%d").date()
        except ValueError:
            print("Could not parse latest date from DB.")
            return

        today = datetime.today().date()

        if latest_date >= today:
            print("Weather data is already up-to-date.")
            return

        print(f"Scraping data from {latest_date + timedelta(days=1)} to {today}...")

        scraper = WeatherScraper(
            base_url=self.base_url,
            start_date=datetime.today(),  # always scrape backwards from today
            earliest_date=latest_date + timedelta(days=1)  # stop when reaching this
        )

        data = scraper.scrape()

        if data:
            self.db.save_data(data, location)
            print(f"{len(data)} new records inserted.")
        else:
            print("No new data found.")

    def generate_box_plot(self):
        """
        Generates a box plot for the mean temperatures over a specified year range.
        """
        try:
            from_year = int(input("Enter starting year (e.g. 2018): "))
            to_year = int(input("Enter ending year (e.g. 2024): "))

            if from_year > to_year:
                print("Starting year cannot be greater than ending year.")
                return

            with DBCM(self.db.db_name) as cursor:
                cursor.execute('''
                    SELECT sample_date, min_temp, max_temp, avg_temp FROM weather
                    WHERE location = ? AND
                        CAST(substr(sample_date, 1, 4) AS INTEGER) BETWEEN ? AND ?
                    ORDER BY sample_date
                ''', ("Winnipeg", from_year, to_year))
                data = cursor.fetchall()

            if not data:
                print("No data available in the specified range.")
                return

            self.plotter.create_boxplot_from_raw_data(data)

        except ValueError:
            print("Invalid input. Please enter valid numeric years.")

    def generate_line_plot(self):
        """
        Generates a line plot for daily mean temperatures for a specified month and year.
        """
        try:
            year = int(input("Enter year (e.g. 2023): "))
            month = int(input("Enter month (1-12): "))

            if not 1 <= month <= 12:
                print("Month must be between 1 and 12.")
                return

            with DBCM(self.db.db_name) as cursor:
                cursor.execute('''
                    SELECT sample_date, min_temp, max_temp, avg_temp FROM weather
                    WHERE location = ? AND
                        CAST(substr(sample_date, 1, 4) AS INTEGER) = ? AND
                        CAST(substr(sample_date, 6, 2) AS INTEGER) = ?
                    ORDER BY sample_date
                ''', ("Winnipeg", year, month))
                data = cursor.fetchall()

            if not data:
                print("No data available for that month and year.")
                return

            self.plotter.create_lineplot_from_raw_data(data, year, month)

        except ValueError:
            print("Invalid input. Please enter numeric values for year and month.")

    def purge_all_data(self):
        """
        Purges all weather data from the database after user confirmation.
        """
        confirm = input("⚠️  DEV: This will permanently delete all weather data. Are you sure? (y/n): ").strip().lower()
        if confirm == 'y':
            self.db.purge_data()
            print("All weather data has been purged from the database.")
        else:
            print("Purge cancelled.")
