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

    def download_data(self, start_date: str) -> str:
        """
        Perform a full scrape from the given start_date (YYYY-MM-DD) and return feedback.
        """
        try:
            earliest_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            scraper = WeatherScraper(self.base_url, datetime.today(), earliest_date)
            data = scraper.scrape()
            if data:
                self.db.save_data(data, "Winnipeg")
                return f"✅ Download complete. {len(data)} records inserted."
            else:
                return "⚠️ No new data found for the specified range."
        except Exception as e:
            return f"❌ Error: {e}"


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
        Scrape new weather data after the latest DB entry.
        """
        try:
            latest_str = self.db.get_latest_date()
            if not latest_str:
                print("[update_data] No existing data.")
                return

            latest_date = datetime.strptime(latest_str, "%Y-%m-%d").date()
            today = datetime.today().date()

            if latest_date >= today:
                print("[update_data] Already up-to-date.")
                return

            scraper = WeatherScraper(
                base_url=self.base_url,
                start_date=datetime.today(),
                earliest_date=latest_date + timedelta(days=1)
            )
            data = scraper.scrape()
            if data:
                self.db.save_data(data, "Winnipeg")
        except Exception as e:
            print(f"[update_data] Error: {e}")


    def generate_boxplot(self, from_year: int, to_year: int, save_path: str):
        """
        Generate boxplot and save to the given path.
        """
        try:
            with DBCM(self.db.db_name) as cursor:
                cursor.execute('''
                    SELECT sample_date, min_temp, max_temp, avg_temp FROM weather
                    WHERE location = ? AND
                          CAST(substr(sample_date, 1, 4) AS INTEGER) BETWEEN ? AND ?
                    ORDER BY sample_date
                ''', ("Winnipeg", from_year, to_year))
                data = cursor.fetchall()
            if data:
                self.plotter.create_boxplot_from_raw_data(data, save_path=save_path)
        except Exception as e:
            print(f"[generate_boxplot] Error: {e}")

    def generate_lineplot(self, year: int, month: int, save_path: str):
        """
        Generate lineplot for a specific month and year.
        """
        try:
            with DBCM(self.db.db_name) as cursor:
                cursor.execute('''
                    SELECT sample_date, min_temp, max_temp, avg_temp FROM weather
                    WHERE location = ? AND
                          CAST(substr(sample_date, 1, 4) AS INTEGER) = ? AND
                          CAST(substr(sample_date, 6, 2) AS INTEGER) = ?
                    ORDER BY sample_date
                ''', ("Winnipeg", year, month))
                data = cursor.fetchall()
            if data:
                self.plotter.create_lineplot_from_raw_data(data, year, month, save_path=save_path)
        except Exception as e:
            print(f"[generate_lineplot] Error: {e}")

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
