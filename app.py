from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from datetime import datetime, timedelta
from json import dumps
from plotly import utils
import pandas as pd
import plotly
import plotly.express as px
import plotly.io as pio
import json
import requests
import spacy
import pytextrank

app = Flask(__name__)

# SPACE
# route to astronomy pictures
@app.route("/")
def weekly_images():
    key = "Ow6qt32sEB5V8P4k7xMFluOM2cEEyGyTrRgQ7B3P"
    date = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(weeks=1)).strftime("%Y-%m-%d")

    #astronomy picture of the day
    try:
        response = requests.get(url = "https://api.nasa.gov/planetary/apod", params = {"end_date": date, "start_date": start, "api_key": key})
        print(f"Status code: {response.status_code}")
    except requests.exceptions.HTTPError as http_error:
        print(f"HTTP Error: {http_error}")
    except requests.exceptions.RequestException as error:
        print(f"Error: {error}")

    #convert to json to get data
    data = response.json()
    
    #extract data
    images_data = {}
    for img in data:

        #extract other data for each image
        images_data[img["date"]] = {"title": img["title"], "image": img["url"], "caption": img["explanation"], "keywords":[]}

        # using TestRank for keyword extraction from image description
        #identify keywords from description to use in NASA image/video library
        text = img["explanation"]
        nlp = spacy.load("en_core_web_sm")
        nlp.add_pipe("textrank")
        summary = nlp(text)

        #save each keyword extracted from pytextrank in a list (new list for each image)
        for phrase in summary._.phrases[:5]:
            images_data[img["date"]]["keywords"].append(phrase.text)

    #reverse order of images so it displays as most recent first
    images = dict(reversed(images_data.items()))

    return render_template("space.html", images_data = images)
