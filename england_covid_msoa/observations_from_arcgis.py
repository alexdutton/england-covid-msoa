import csv
import datetime
import os
import re

import csvsort

observations_fieldnames = [
    "msoa",
    "source",
    "specimenDate",
    "observationDate",
    "fetchDate",
    "rollingSum",
]
observations_source = "arcgis"

observations_fn = os.path.join("data", "observations.csv")
observations_new_fn = os.path.join("data", "observations.new.csv")

with open(observations_new_fn, "w") as observations_new_f:
    observations_writer = csv.DictWriter(observations_new_f, observations_fieldnames)
    observations_writer.writeheader()

    if os.path.exists(observations_fn):
        with open(observations_fn) as observations_f:
            observations_reader = csv.DictReader(observations_f)
            for row in observations_reader:
                if row["source"] != observations_source:
                    observations_writer.writerow(row)

    for fn in sorted(os.listdir("data")):
        if not re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\.csv$", fn):
            continue

        observation_date = datetime.date(int(fn[:4]), int(fn[5:7]), int(fn[8:10]))
        fn = os.path.join("data", fn)

        fetch_date = datetime.datetime.fromtimestamp(os.stat(fn).st_ctime).replace(
            microsecond=0
        )

        with open(fn) as f:
            reader = csv.DictReader(f)

            specimen_date_fieldname = [
                f for f in reader.fieldnames if f.startswith("wk")
            ][0]
            specimen_date = datetime.datetime.strptime(
                "2020 " + specimen_date_fieldname, "%G wk%V_%u"
            ).date()

            for row in reader:
                observations_writer.writerow(
                    {
                        "msoa": row["msoa11cd"],
                        "source": observations_source,
                        "specimenDate": specimen_date.isoformat(),
                        "observationDate": observation_date.isoformat(),
                        "fetchDate": fetch_date.isoformat(),
                        "rollingSum": row[specimen_date_fieldname],
                    }
                )

csvsort.csvsort(observations_new_fn, [0, 2, 3])
os.rename(observations_new_fn, observations_fn)
