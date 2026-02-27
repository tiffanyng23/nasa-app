from flask import Flask, render_template
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

# Homepage
@app.route("/")
def explore():
    return render_template("explore.html")

# EARTH
# route to EONET to track global natural events
@app.route("/earth")
def earth_events():
    key = "Ow6qt32sEB5V8P4k7xMFluOM2cEEyGyTrRgQ7B3P"
    date = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(weeks=1)).strftime("%Y-%m-%d")

    # get earth events from the past week
    try:
        response = requests.get(url = "https://eonet.gsfc.nasa.gov/api/v3/events", params={"start": start, "end": date, "api_key":key})
        data = response.json()
        events_data = data["events"]
        print(f"EONET Request: {response.status_code}")
    except requests.exceptions.HTTPError as http_error: #when http request returns an error
        print(f"HTTP Error: {http_error}")
    except requests.exceptions.RequestException as error: #all other errors
        print(f"Error: {error}")

    #extract data: Category ID, Title, Date, Coordinates, Magnitude Value
    earth_events={}
    for event in events_data:
        earth_events[event["id"]] = {"title": event["title"], 
                                    "date": event["geometry"][0]["date"],
                                    "magnitude": event["geometry"][0]["magnitudeValue"],
                                    "type": event["categories"][0]["id"],
                                    "coordinates": event["geometry"][0]["coordinates"]}

    return render_template("earth.html")


# SPACE
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
