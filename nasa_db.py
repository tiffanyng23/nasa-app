import json
import requests
import os
import sqlite3
from datetime import datetime, timezone

#metadata helper functions
# handle metadata that returns strings or lists or are empty
def format_metadata(value):
    # no value
    if value is None:
        return ""
    # check if metadata is a string
    if isinstance(value, list):
        return ", ".join(value)
    # else, no need to format
    return value

# handle empty release dates for public release date metadata
def format_date(value):
    if value is None or value == "":
        return None
    else:
        return datetime.fromtimestamp((value), tz=timezone.utc).strftime("%Y/%m/%d")

# store dataset metadata on sqlite3 (easier to retrieve for subsequent attempts)
conn = sqlite3.connect("nasa.db")
cursor = conn.cursor()

# create table to hold API data (only for first time)
cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS studies (
            id TEXT PRIMARY KEY,
            rest_url TEXT,
            space_program TEXT,
            flight_program TEXT,
            mission_start DATE,
            mission_end DATE,
            mission_name TEXT,
            project_type TEXT,
            project_title TEXT,
            study_title TEXT,
            study_description TEXT,
            study_release_date DATE,
            study_factor TEXT,
            publications TEXT,
            organism TEXT,
            assay_technology TEXT,
            assay_measure TEXT
        )
    """)
conn.commit()
print("table created")

#api request
try:
    #extract all datasets related to search
    response = requests.get(url="https://visualization.osdr.nasa.gov/biodata/api/v2/datasets/")
    response.raise_for_status()
    print(f"Open Science Data code: {response.status_code}")
except requests.exceptions.HTTPError as http_error:
    print(f"Open Science Data HTTP Error: {http_error}")
except requests.exceptions.RequestException as error:
    print(f"Open Science Data  Error: {error}")
    
# convert json to dictionary
osd_dict = response.json()
osd_data = {}
for osd_id, endpoint in osd_dict.items():
    osd_data[osd_id] = endpoint["REST_URL"]

# check if study id is in the database
for osd_id in osd_data.keys():
    cursor.execute(
            "SELECT id FROM studies WHERE id = ?",
            (osd_id,)
    )
    result = cursor.fetchone()

    # id is not in database --> second api request to get metadata
    if result is None:
        try:
            id_response = requests.get(url=f"https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/{osd_id}")
            id_response.raise_for_status()
            print(f"Study Retrieval code: {response.status_code}")
        except requests.exceptions.HTTPError as http_error:
            print(f"Study Retrieval HTTP Error: {http_error}")
        except requests.exceptions.RequestException as error:
            print(f"Study Retrieval  Error: {error}")

        # convert to dictionary
        study_dict = id_response.json()

        # variables to retrieve dictionary data
        study = study_dict[osd_id]
        metadata = study.get("metadata", {})

        # insert metadata into table
        cursor.execute(
                    """INSERT INTO studies (id, rest_url, space_program, flight_program, mission_start, mission_end, mission_name, project_type, project_title, study_title, study_description, study_release_date, study_factor, publications, organism, assay_technology, assay_measure)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, 
                        (
                            osd_id,
                            study.get("REST_URL"),
                            format_metadata(metadata.get("space program")),
                            format_metadata(metadata.get("flight program")),
                            format_metadata(metadata.get("mission", {}).get("start date")),
                            format_metadata(metadata.get("mission", {}).get("end date")),
                            format_metadata(metadata.get("mission", {}).get("name")),
                            format_metadata(metadata.get("project type")),
                            format_metadata(metadata.get("project title")),
                            format_metadata(metadata.get("study title")),
                            format_metadata(metadata.get("study description")),
                            format_date(format_metadata(metadata.get("study public release date"))),
                            format_metadata(metadata.get("study factor type")),
                            format_metadata(metadata.get("study publication title")),
                            format_metadata(metadata.get("organism")),
                            format_metadata(metadata.get("study assay technology type")),
                            format_metadata(metadata.get("study assay measurement type"))
                    )
        )
        print(osd_id)

print("rows inserted")
conn.commit()
conn.close()