import csv
import datetime
import json
import os
import urllib.parse
import urllib.request
from urllib.error import HTTPError


def get_url(date: datetime.date, **kwargs):
    dataset = f'MSOA_2011_En_{date.strftime("%Y%m%d")}_WGS84_std'
    base_url = f"https://services1.arcgis.com/0IrmI40n5ZYxTUrV/ArcGIS/rest/services/{dataset}/FeatureServer/0/query"

    query = {
        "f": "json",
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        **{k: str(kwargs[k]) for k in kwargs},
    }

    return f"{base_url}?{urllib.parse.urlencode(query)}"


def get_response_data(date: datetime.date, **kwargs):
    url = get_url(date, **kwargs)
    print(f"Getting data for {date}, {kwargs}")
    response = urllib.request.urlopen(url)
    data = json.load(response)
    if "error" in data:
        raise HTTPError(
            url=url,
            code=data["error"]["code"],
            msg=data["error"]["details"][0],
            hdrs={},
            fp=response,
        )

    return data


def get_data(date: datetime.date, just_the_first=False):
    request_kwargs, offset = {}, 0
    all_data = None
    while not (just_the_first and offset):
        data = get_response_data(date, **request_kwargs)
        if not data["features"]:
            break

        if all_data:
            all_data["features"].extend(data["features"])
        else:
            all_data = data

        offset += len(data["features"])
        request_kwargs["resultOffset"] = offset

    return all_data


def add_data_to_combined(data):
    filename = os.path.join("data", "combined.csv")

    if not os.path.exists(filename):
        with open(filename, "w") as f:
            fieldnames = [
                name
                for field in data["fields"]
                if not (name := field["name"]).lower().startswith("wk")
                and name not in ("msoa11_cd", "Shape__Area", "Shape__Length")
            ]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for feature in data["features"]:
                writer.writerow(
                    {name: feature["attributes"][name] for name in fieldnames}
                )

    new_field_name = next(
        name
        for field in data["fields"]
        if (name := field["name"]).lower().startswith("wk")
    )

    values = {
        feature["attributes"]["msoa11cd"]: feature["attributes"][new_field_name]
        for feature in data["features"]
    }

    with open(filename, "r") as in_f, open(filename + ".tmp", "w") as out_f:
        reader = csv.DictReader(in_f)
        writer = csv.DictWriter(out_f, [*reader.fieldnames, new_field_name])
        writer.writeheader()
        for row in reader:
            row[new_field_name] = values[row["msoa11cd"]]
            writer.writerow(row)

    os.rename(filename + ".tmp", filename)


def save_data(date: datetime.date, data):
    geometry = extract_geometry(data)
    with open(get_filename(date), "w") as f:
        json.dump(data, f, indent=2)
    with open(get_filename(date, ".csv"), "w") as f:
        writer = csv.DictWriter(f, [field["name"] for field in data["fields"]])
        writer.writeheader()
        for feature in data["features"]:
            writer.writerow(
                {
                    k: str(v) if (v := feature["attributes"][k]) else ""
                    for k in feature["attributes"]
                }
            )

    add_data_to_combined(data)

    return geometry


def extract_geometry(data):
    geometry = {}
    for feature in data["features"]:
        geometry[feature["attributes"]["msoa11cd"]] = feature.pop("geometry")
        # for name in ('msoa11_cd', 'Shape__Area', 'Shape__Length'):
        #     del feature['attributes'][name]
    return geometry


def get_filename(date: datetime.date, ext=".json"):
    return os.path.join("data", date.strftime("%Y-%m-%d") + ext)


today = datetime.date.today()
yesterday = today - datetime.timedelta(1)

todays_filename = get_filename(today)
yesterdays_filename = get_filename(yesterday)
geometry_filename = os.path.join("data", "geometry.json")


if not os.path.exists("data"):
    os.mkdir("data")

if not os.path.exists(todays_filename):
    try:
        todays_data = get_data(today)
        geometry = save_data(today, todays_data)
    except HTTPError:
        # Ensure yesterday's data is still there (i.e. today's is there, just not where we expect it)
        yesterdays_data = get_data(
            yesterday, just_the_first=os.path.exists(yesterdays_filename)
        )
        if not os.path.exists(yesterdays_filename):
            geometry = save_data(yesterday, yesterdays_data)

    if not os.path.exists(geometry_filename):
        with open(geometry_filename, "w") as f:
            json.dump(geometry, f, indent=2)
