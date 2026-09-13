import requests

url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"

limit = 100
offset =0
page = 1
while True:
    params = {
        "limit": limit,
        "offset": offset
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
    except requests.exceptions.Timeout as e:
        print("Timeout error:", e)
    except requests.RequestException as e:
        print("Request error:", e)

    except ValueError as e:
        print("Value error:", e)

    print("Page:", page)
    print("Offset:", offset)
    print("Number of records:", len(data["activities"]))
    print("Page metadata:", data["page_meta"])

    for activity in data["activities"]:
        print(activity["activity_id"])

    print("---")
    offset +=limit
    page += 1

    if len(data["activities"]) < limit:
        break






#for activity in data["activities"]:
#    print(activity["activity_id"])


#print(data.keys())