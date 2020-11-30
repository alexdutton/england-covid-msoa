import datetime
import time

import dateutil.parser
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

NO_CONTENT = object()

with open("email.txt") as f:
    email = f.read().split()

ua = f"england-covid-msoa (https://github.com/alexsdutton/england-covid-msoa#if-you-run-this-api; {email})"


def get_data_for_msoa(msoa):
    url = "https://api.coronavirus.data.gov.uk/v1/soa?" + urllib.parse.urlencode(
        {"areaType": "msoa", "areaCode": msoa}
    )
    request = urllib.request.Request(
        url=url,
        headers={
            "User-Agent": ua,
            "Accept": "application/json",
            "X-Clacks-Overhead": "GNU Terry Pratchett",
        },
    )
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.headers.get('Retry-After'):
            print(f"Sleeping for {e.headers['Retry-After']} seconds")
            time.sleep(int(e.headers['Retry-After']) + 1)
            response = urllib.request.urlopen(request)
        else:
            response = e
    if response.status == 204:
        return []
    if response.status != 200:
        sys.stderr.write(f"GET {url}\n\n")
        sys.stderr.write(f"{response.status} {response.msg}\n")
        sys.stderr.write("\n".join(f"{k}: {v}" for k, v in response.headers.items()))
        sys.stderr.write("\n\n" + response.read().decode())
        raise ValueError
    data = json.load(response)

    release_date = dateutil.parser.parse(data["release"]).replace(microsecond=0)

    latest_cases = data["latest"]["newCasesBySpecimenDate"]
    new_cases = data["newCasesBySpecimenDate"]

    if isinstance(latest_cases, list):
        # E02004185, unlike every other, somehow has this as an array. idk why.
        assert len(latest_cases) == 1
        latest_cases = latest_cases[0]

    if latest_cases["date"] != new_cases[0]["date"]:
        data["newCasesBySpecimenDate"].insert(0, latest_cases)

    return [
        {
            "msoa": msoa,
            "source": "api",
            "specimenDate": datum["date"],
            "observationDate": release_date.isoformat(),
            "fetchDate": datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
            "rollingSum": ""
            if (rolling_sum := datum["rollingSum"]) in ("0-2", None)
            else str(rolling_sum),
        }
        for datum in data["newCasesBySpecimenDate"]
    ]
