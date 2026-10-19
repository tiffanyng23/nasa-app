import json
import requests
import os
import sqlite3

# this script was created to update the studies table with pubmed ids
# run this script periodically to update newly inserted projects that have publications with their pubmed ids 

conn = sqlite3.connect("nasa.db")
cursor = conn.cursor()

# insert pubmed links
# select all rows that has an empty publications_urls column
cursor.execute(
            "SELECT id, publications FROM studies WHERE publications_urls IS NULL"
    )
all_publications = cursor.fetchall()
url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

for studies_row in all_publications:
    # new list without the osd-id
    publications = studies_row[1:]
    # reset this variable for each row
    row_urls = []
    for pub in publications:
        # retrieve pubmedID
        try:
            term = pub.replace(" ", "+")
            params = {
                "db": "pubmed",
                "term": f"{pub}[Title]",
                "retmode": "json"
            }
            pub_urls = requests.get(url=url, params = params, timeout = 15)
            pub_urls.raise_for_status()
            print(f"study id: {studies_row[0]}")
            print(f"PUBMED ENTREZ code: {response.status_code}")
        except requests.exceptions.HTTPError as http_error:
            print(f"study id: {studies_row[0]}")
            print(f"PUBMED ENTREZ HTTP Error: {http_error}")
        except requests.exceptions.RequestException as error:
            print(f"study id: {studies_row[0]}")
            print(f"PUBMED ENTREZ Error: {error}")
    
        # convert json to dictionary
        pub_dict = pub_urls.json()

        #retrieve pubmed ids
        pmd_id = pub_dict["esearchresult"]["idlist"]

        # add to list of ids for the row
        row_urls.append(pmd_id)

    # control rate of api calls by resting for 2 seconds 
    time.sleep(2)

    # update table with all urls for that row
    cursor.execute(
                """UPDATE studies
                    SET publications_urls = ?
                    WHERE id = ?""",
                    (json.dumps(pmd_id), studies_row[0])
    )
    print(f"pmd_ids inserted in this row: {row_urls}")

print("rows updated successfully")
conn.commit()
conn.close()