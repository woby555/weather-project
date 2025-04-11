"""
Description: Plot Operations class for creating boxplots and lineplots from weather data.
Author: Jake Licmo
Date: 2025-04-04
"""
from collections import defaultdict
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class PlotOperations:
    """
    Class for creating boxplots and lineplots from weather data.
    """

    def create_boxplot(self, weather_data_by_month, save_path=None):
        """
        Creates a boxplot for the mean temperatures of each month.
        :param weather_data_by_month: Dictionary containing mean temperatures for each month.
        :param save_path: If provided, saves the plot to this file path instead of showing it.
        """
        data = []
        labels = []

        for month in range(1, 13):
            if month in weather_data_by_month:
                data.append(weather_data_by_month[month])
                labels.append(self.month_number_to_name(month))

        plt.figure(figsize=(12, 6))
        plt.boxplot(data, labels=labels)
        plt.title("Monthly Mean Temperature Boxplot")
        plt.xlabel("Month")
        plt.ylabel("Mean Temperature")
        plt.grid(True)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def create_lineplot(self, daily_data, year, month, save_path=None):
        """
        Creates a lineplot for daily mean temperatures for a specific month and year.
        :param daily_data: List of tuples containing date and mean temperature.
        :param year: Year for the data.
        :param month: Month for the data.
        :param save_path: If provided, saves the plot to this file path instead of showing it.
        """
        dates = [date for date, _ in daily_data]
        temps = [temp for _, temp in daily_data]

        plt.figure(figsize=(12, 5))
        plt.plot(dates, temps, marker='o')
        plt.title(f"Daily Mean Temperatures - {self.month_number_to_name(month)} {year}")
        plt.xlabel("Date")
        plt.ylabel("Mean Temperature")
        plt.xticks(rotation=45, fontsize=8)
        plt.grid(True)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def create_boxplot_from_raw_data(self, fetched_data, save_path=None):
        """
        Creates a boxplot from raw data fetched from the database.
        :param fetched_data: List of tuples containing sample date, min temp, max temp, and mean temp.
        :param save_path: File path to save the plot (used in Flask).
        """
        boxplot_data = defaultdict(list)
        for sample_date, _, _, mean_temp in fetched_data:
            if mean_temp is not None:
                try:
                    month = int(sample_date.split("-")[1])
                    boxplot_data[month].append(mean_temp)
                except Exception as e:
                    print(f"Skipping row {sample_date}: {e}")
        self.create_boxplot(boxplot_data, save_path)

    def create_lineplot_from_raw_data(self, fetched_data, year, month, save_path=None):
        """
        Creates a lineplot from raw data fetched from the database.
        :param fetched_data: List of tuples containing sample date, min temp, max temp, and mean temp.
        :param year: Year for the data.
        :param month: Month for the data.
        :param save_path: File path to save the plot (used in Flask).
        """
        daily_data = []
        for sample_date, _, _, mean_temp in fetched_data:
            try:
                date_obj = datetime.strptime(sample_date, '%Y-%m-%d')
                if date_obj.year == year and date_obj.month == month:
                    daily_data.append((sample_date, mean_temp))
            except Exception as e:
                print(f"Invalid date format in row {sample_date}: {e}")
        self.create_lineplot(daily_data, year, month, save_path)

    def month_number_to_name(self, month_number):
        """
        Converts a month number to its corresponding month name.
        :param month_number: Month number (1-12).
        :return: Month name as a string.
        """
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        return months[month_number - 1] if 1 <= month_number <= 12 else "Unknown"
