from datetime import timedelta
from datetime import datetime
from scrape_weather import WeatherScraper
from db_operations import DBOperations
from plot_operations import PlotOperations
from db_operations import DBCM

class WeatherProcessor:
    def __init__(self):
        self.scraper = WeatherScraper
        self.db = DBOperations()
        self.plotter = PlotOperations()
        self.base_url = (
            "http://climate.weather.gc.ca/climate_data/daily_data_e.html"
            "?StationID=27174&timeframe=2&StartYear=1840&EndYear={year}"
            "&Day=1&Year={year}&Month={month}#"
        )

    def run(self):
        while True:
            self.show_menu()
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                self.download_full_data()
            elif choice == '2':
                self.update_data()
            elif choice == '3':
                self.generate_box_plot()
            elif choice == '4':
                self.generate_line_plot()
            elif choice == '5':
                print("Exiting program.")
                break
            else:
                print("Invalid choice. Please try again.\n")

    def show_menu(self):
        print("\n===== Weather Data Processor =====")
        print("1. Download full weather data")
        print("2. Update weather data")
        print("3. Generate box plot (year range)")
        print("4. Generate line plot (month & year)")
        print("5. Exit")

    def download_full_data(self):
        try:
            file_path = input("Enter the output CSV file path (e.g. weather_data/export.csv): ").strip()
            if not file_path.endswith(".csv"):
                file_path += ".csv"
            self.db.export_to_csv(file_path)
        except Exception as e:
            print(f"Failed to export data: {e}")

    def update_data(self):
        latest_str = self.db.get_latest_date()
        location = "Winnipeg"

        if not latest_str:
            print("No existing data found in DB. Please run a full scrape first.")
            return

        try:
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
        try:
            year = int(input("Enter year (e.g. 2023): "))
            month = int(input("Enter month (1-12): "))

            if not (1 <= month <= 12):
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
