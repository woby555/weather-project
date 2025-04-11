from db_operations import DBOperations
from plot_operations import PlotOperations

def main():
    location = "Winnipeg"
    year = 2024
    month = 12  # January

    db = DBOperations()
    fetched_data = db.fetch_data(location)

    plotter = PlotOperations()
    plotter.create_boxplot_from_raw_data(fetched_data)
    plotter.create_lineplot_from_raw_data(fetched_data, year, month)

if __name__ == "__main__":
    main()