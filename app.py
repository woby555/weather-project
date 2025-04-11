from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from weather_processor import WeatherProcessor
import os

app = Flask(__name__)
processor = WeatherProcessor()

# Ensure plots directory exists
os.makedirs("static/plots", exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", plot_path=None)

@app.route("/download", methods=["POST"])
def download():
    start_date = request.form["start_date"]
    message = processor.download_data(start_date)
    return render_template("index.html", plot_path=None, message=message)


@app.route("/update", methods=["POST"])
def update():
    processor.update_data()
    return redirect(url_for("index"))

@app.route("/boxplot", methods=["POST"])
def boxplot():
    from_year = int(request.form["from_year"])
    to_year = int(request.form["to_year"])
    output_path = "static/plots/boxplot.png"
    processor.generate_boxplot(from_year, to_year, save_path=output_path)
    return render_template("index.html", plot_path="/" + output_path)

@app.route("/lineplot", methods=["POST"])
def lineplot():
    year = int(request.form["year"])
    month = int(request.form["month"])
    output_path = "static/plots/lineplot.png"
    processor.generate_lineplot(year, month, save_path=output_path)
    return render_template("index.html", plot_path="/" + output_path)

if __name__ == "__main__":
    app.run(debug=True)
