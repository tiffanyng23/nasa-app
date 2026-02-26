from flask import Flask, render_template
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

# homepage where you select to explore earth or space
@app.route("/")
def explore():
    return render_template("explore.html")

# route to EONET to track global natural events

# route to astronomy pictures
@app.route("/space")
def weekly_images():
    key = "Ow6qt32sEB5V8P4k7xMFluOM2cEEyGyTrRgQ7B3P"
    date = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(weeks=1)).strftime("%Y-%m-%d")

    #astronomy picture of the day
    response = requests.get(url = "https://api.nasa.gov/planetary/apod", params = {"end_date": date, "start_date": start, "api_key": key})
    #convert to json to get data
    data = response.json()

    #extract data
    images_data = {}
    for img in data:
        images_data[img["date"]] = {"title": img["title"], "image": img["url"], "caption": img["explanation"]}

    #reverse order of images so it displays as most recent first
    images = dict(reversed(images_data.items()))


    return render_template("space.html", images_data = images)