# Weather Data Processing (CLI Version)

This project provides a command-line interface (CLI) tool for **scraping, storing, processing, and visualizing historical weather data**.  
It focuses on **Winnipeg weather records** sourced directly from Environment Canada.

## Features
- **Scrape Historical Weather Data**: Automatically parse daily temperature records (min, max, mean) for Winnipeg from Environment Canada’s website.
- **Database Storage**: Save scraped data into a local SQLite database for reliable storage and quick access.
- **Data Updating**: Update existing database records with newer data without duplicating entries.
- **Data Export**: Export stored weather data to CSV format for external analysis.
- **Data Visualization**: Generate boxplots of mean monthly temperatures directly from database records.

## Repository Structure
- `scrape_weather.py` — Scrapes Environment Canada’s weather pages.
- `db_operations.py` — Manages all database-related tasks (create, insert, update, fetch, purge).
- `weather_processor.py` — Core CLI handler: orchestrates user interaction, scraping, database updates, exports, and plotting.
- `plot_operations.py` — Generates boxplots from raw or processed data.

## How to Run

1. **Clone this repository:**
   ```bash
   git clone https://github.com/woby555/weather-project.git
   cd weather-project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Only common packages like `matplotlib`, `requests` are needed.)*

3. **Run the CLI tool:**
   ```bash
   python main.py
   ```

4. **Follow the on-screen prompts to:**
   - Scrape new weather data starting from a custom date
   - Update your local database
   - Export data to CSV
   - Generate and view boxplots of temperature trends

## Example CLI Flow
```
===== Weather Data Processor =====
1. Download weather data (scrape & save to DB)
2. Export current weather data to CSV
3. Update weather data
4. Generate box plot (year range)
5. Generate line plot (month & year)
6. Exit
Enter your choice:
```

## Project Motivation
This project was created to gain real-world experience in:
- Web scraping and data extraction from structured but imperfect HTML sources.
- Building self-contained CLI applications with clear separation between scraping, database operations, and visualization.
- Managing SQLite databases and ensuring safe, consistent updates to stored datasets.
- Providing clean, user-driven workflows without relying on a full GUI.

## Potential Future Enhancements
- Add support for scraping additional Canadian cities beyond Winnipeg.
- Implement retry/backoff mechanisms for scraping sessions to improve reliability.
- Expand database schema to store precipitation, snowfall, or other weather metrics.
- Develop a fully functioning User Interface using Flask.
