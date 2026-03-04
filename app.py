from flask import Flask, render_template, request
from datetime import datetime, timedelta, timezone
import json
import pytextrank
import requests
import spacy
import pandas as pd
import folium

app = Flask(__name__)

# HOMEPAGE
@app.route("/")
def explore():
    return render_template("explore.html")

# EARTH'S NATURAL EVENTS
@app.route("/events", methods=["POST", "GET"])
def events():
    if request.method == "POST": #after user submits dates
        #gather start and end date from post
        start = request.form.get("start")
        end = request.form.get("end")
        event_type = request.form.get("category") #get selected category
        if event_type == "all": #if user selects all categories, assign all the event types
            categories = "wildfires,volcanoes,severeStorms,drought,dustHaze,earthquakes,floods,landslides,manmade"
        else: #assign user selected event type
            categories = event_type

    else: #page displayed before user selection should have dates set to today
        end = datetime.today().strftime("%Y-%m-%d")
        start = datetime.today().strftime("%Y-%m-%d")
        categories = "wildfires,volcanoes,severeStorms,drought,dustHaze,earthquakes,floods,landslides,manmade"

    #api call to gather eonet data
    try:
        response = requests.get("https://eonet.gsfc.nasa.gov/api/v3/events/geojson", params={"start":start, "end":end, "category":categories})
        print(f"EONET Status Code: {response.status_code}")
    except requests.exceptions.HTTPError as http_error:
        print(f"EONET HTTP Error: {http_error}")
    except requests.exceptions.RequestException as error:
        print(f"EONET Error: {error}")
        
    #convert to json
    data = response.json()
    events_data = data["features"]

    #extract data for table and map
    events = {}
    i=0
    for event in events_data:
        events[i] = {"id": event["properties"]["id"],
                                            "title":event["properties"]["title"], 
                                            "date":datetime.fromisoformat(event["properties"]["date"][0:-1]).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                                            "category": event["properties"]["categories"][0]["id"], 
                                            "longitude": event["geometry"]["coordinates"][0],
                                            "latitude": event["geometry"]["coordinates"][1]}
        i+=1

    #map
    m = folium.Map(location=(20, 0), zoom_start=2, tiles="OpenStreetMap")
    #colour options of markers - based on category
    color_options={"wildfires": "orange", "volcanoes":"darkred", "severeStorms":"darkblue", "manmade":"black", "landslides":"darkgreen", "floods":"lightblue", "earthquakes":"beige", "dustHaze":"gray"}
        
    #add coordintates to map
    for index, event in events.items():
        #popup description for each event
        popup_description=f"<strong>{event['title']}</strong><br>Datetime: {event['date']}<br>Category: {event['category']}"
        folium.CircleMarker(
            location=[float(event["latitude"]), float(event["longitude"])],
            radius=6,
            popup=popup_description, 
            fill=True, 
            color=color_options[event["category"]] 
            ).add_to(m)
        
    #convert to html
    map_html = m._repr_html_()

    #get max day
    today = datetime.today().strftime("%Y-%m-%d")
    #return category to template
    if categories == "wildfires,volcanoes,severeStorms,drought,dustHaze,earthquakes,floods,landslides,manmade":
        categories = "all"

    return render_template("events.html", map_html=map_html, start=start, end=end, today=today, event_type=categories)


# EARTH
# route to EPIC earth pictures
@app.route("/earth")
def earth_images():
    try:
        #extract natural and enhanced images
        response = requests.get(url="https://epic.gsfc.nasa.gov/api/natural")
        print(f"EPIC Natural Status code: {response.status_code}")
    except requests.exceptions.HTTPError as http_error:
        print(f"EPIC HTTP Error: {http_error}")
    except requests.exceptions.RequestException as error:
        print(f"EPIC Error: {error}")

    try:
        #extract natural and enhanced images
        response_enhanced = requests.get(url="https://epic.gsfc.nasa.gov/api/enhanced")
        print(f"EPIC Enhanced Status code: {response_enhanced.status_code}")
    except requests.exceptions.HTTPError as http_error:
        print(f"EPIC HTTP Error: {http_error}")
    except requests.exceptions.RequestException as error:
        print(f"EPIC Error: {error}")

    #convert natural and enhanced image data to json
    data = response.json()
    data_enhanced = response_enhanced.json()

    #extract most recent date of image release for natural images
    year = data[0]["date"][:4]
    month = data[0]["date"][5:7]
    day = data[0]["date"][8:10]
    #extract image urls for both natural 
    image_urls = {}
    for img_nat in data:
        image_urls[img_nat["identifier"]]={"natural":f"https://epic.gsfc.nasa.gov/archive/natural/{year}/{month}/{day}/png/{img_nat["image"]}.png"}

    #extract most recent date for enhanced images
    year_enhanced = data_enhanced[0]["date"][:4]
    month_enhanced = data_enhanced[0]["date"][5:7]
    day_enhanced = data_enhanced[0]["date"][8:10]
    #extract urls for enhanced images
    enhanced_urls = {}
    for img_enhanced in data_enhanced:
        enhanced_urls[img_enhanced["identifier"]]={"enhanced":f"https://epic.gsfc.nasa.gov/archive/enhanced/{year_enhanced}/{month_enhanced}/{day_enhanced}/png/{img_enhanced["image"]}.png"}

    return render_template("earth.html", 
                        image_urls=image_urls, 
                        enhanced_urls = enhanced_urls, 
                        year = year, month=month, day=day,
                        year_enhanced = year_enhanced,
                        month_enhanced = month_enhanced,
                        day_enhanced = day_enhanced)

# SPACE
# route to astronomy pictures
@app.route("/space")
def weekly_images():
    key = "Ow6qt32sEB5V8P4k7xMFluOM2cEEyGyTrRgQ7B3P"
    date = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(days=10)).strftime("%Y-%m-%d")

    #astronomy picture of the day
    try:
        response = requests.get(url = "https://api.nasa.gov/planetary/apod", params = {"end_date": date, "start_date": start, "api_key": key})
        print(f"APOD Status code: {response.status_code}")
    except requests.exceptions.HTTPError as http_error:
        print(f"APOD HTTP Error: {http_error}")
    except requests.exceptions.RequestException as error:
        print(f"APOD Error: {error}")

    #convert to json to get data
    data = response.json()
    
    #extract data
    images_data = {}
    for img in data:

        #extract other data for each image
        images_data[img["date"]] = {"title": img["title"], "image": img["url"], "caption": img["explanation"], "keywords":{}}

        # NLP with PyTestRank for keyword extraction from image description
        #identify keywords from description to use in NASA image/video library
        text = ": ".join([img["title"],img["explanation"]])
        nlp = spacy.load("en_core_web_sm")
        nlp.add_pipe("textrank")
        summary = nlp(text)

        #save each keyword extracted from pytextrank in a list (new list for each image)
        for phrase in summary._.phrases[:8]:
            #extract top 8 keywords from title + description
            word = phrase.text

            #remove quotes for word
            url_word = word.strip('')
            #create url for each keyword to go to NASAs image and video library
            url = f"https://images.nasa.gov/search?q={url_word}&page=1&media=image,video,audio&yearStart=1920&yearEnd=2026"

            #update dictionary with keyword:url key-value pair for each day
            images_data[img["date"]]["keywords"][phrase.text] = url

    #reverse order of images so it displays as most recent first
    images = dict(reversed(images_data.items()))

    return render_template("space.html", images_data = images)

if __name__ == "__main__":
    app.run(debug=True)