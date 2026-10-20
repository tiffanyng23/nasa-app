import json
import requests
import os
import sqlite3
import time

# this script was created to update the studies table with pubmed ids
# run this script periodically to update newly inserted projects that have publications with their pubmed ids 

conn = sqlite3.connect("nasa.db")
cursor = conn.cursor()

# insert pubmed links
# select all rows that has an empty publications_urls column
cursor.execute(
            "SELECT id, publications FROM studies WHERE publications_urls is NULL"
    )
all_publications = cursor.fetchall()
url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

# go through each study 
for project in all_publications:
    print(project)
    # new list without the osd-id
    osd_id = project[0]
    publications = project[1]

    # reset this variable for each row
    project_pmd_ids = []

    # only do pubmed api call if there are publications in that row
    if publications.strip(''):
        # convert publications from a single string to a list of strings
        # clean up formatting
        publications = publications.split(";")
        publications = [pub.lstrip() for pub in publications]
        print(publications)

        # go through each pub in the publications list
        for publication in publications:
            try:
                # api call will search for pubs based on title of publication
                params = {
                    "db": "pubmed",
                    "term": f"'{publication}'[Title]",
                    "retmode": "json",
                    "retmax": 1
                }
                pub_urls = requests.get(url=url, params = params, timeout = 15)
                pub_urls.raise_for_status()
                print(f"study id: {osd_id}")
                print(f"PUBMED ENTREZ code: {pub_urls.status_code}")
            except requests.exceptions.HTTPError as http_error:
                print(f"study id: {osd_id}")
                print(f"PUBMED ENTREZ HTTP Error: {http_error}")
            except requests.exceptions.RequestException as error:
                print(f"study id: {osd_id}")
                print(f"PUBMED ENTREZ Error: {error}")
        
            #retrieve pubmed ids
            pub_dict = pub_urls.json()
            pmd_id = pub_dict["esearchresult"]["idlist"]

            # add to list of ids to insert into the row
            project_pmd_ids.append(pmd_id)

            # control rate of api calls
            time.sleep(2)

        # update table with all pmd_ids for that specific project
        cursor.execute(
                    """UPDATE studies
                        SET publications_urls = ?
                        WHERE id = ?""",
                        (json.dumps(project_pmd_ids), osd_id)
        )

        print(f"pmd_ids inserted in this row: {project_pmd_ids}")
        
print("rows updated successfully")
conn.commit()
conn.close()