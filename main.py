import contextlib
import csv
import datetime
import itertools
import json
import os
import pprint
import sys
import time
import urllib.parse
import urllib.request

with open("email.txt") as f:
    email = f.read().split()

ua = f"england-covid-msoa (https://github.com/alexsdutton/england-covid-msoa; {email})"


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
    response = urllib.request.urlopen(request)
    return json.load(response)["latest"]["newCasesBySpecimenDate"]


old_filename = os.path.join("data", "combined.csv")
new_filename = os.path.join("data", "combined.new.csv")
partial_filename = os.path.join("data", "combined.partial.csv")


try:
    with contextlib.ExitStack() as exit_stack:
        old_f = exit_stack.enter_context(open(old_filename))

        reader = csv.DictReader(old_f)
        first_row = next(reader)
        first_data = get_data_for_msoa(first_row["msoa11cd"])
        specimen_date = first_data["date"]
        specimen_date = datetime.date(*map(int, specimen_date.split("-"))).isocalendar()
        print(specimen_date)
        specimen_date = f"wk{specimen_date[1]}_{specimen_date[2]}"
        if reader.fieldnames[-1] == specimen_date:
            print("No new data")
            sys.exit(0)

        if os.path.exists(partial_filename):
            partial_f = exit_stack.enter_context(open(partial_filename))
            partial_reader = csv.DictReader(partial_f)
            next(partial_reader)  # Skip the first row
        else:
            partial_reader = []

        new_f = exit_stack.enter_context(open(new_filename, "w"))
        writer = csv.DictWriter(new_f, fieldnames=[*reader.fieldnames, specimen_date])
        writer.writeheader()

        first_row[specimen_date] = str(first_data["rollingSum"])
        writer.writerow(first_row)

        for row, partial_row in itertools.zip_longest(reader, partial_reader):
            if partial_row:
                row[specimen_date] = partial_row[specimen_date]
            else:
                time.sleep(0.2)
                data = get_data_for_msoa(row["msoa11cd"])
                row[specimen_date] = (
                    str(rolling_sum)
                    if (rolling_sum := data["rollingSum"]) != "0-2"
                    else ""
                )
            writer.writerow(row)

except BaseException:
    os.rename(new_filename, partial_filename)
    raise
else:
    os.rename(new_filename, old_filename)
    if os.path.exists(partial_filename):
        os.unlink(partial_filename)
