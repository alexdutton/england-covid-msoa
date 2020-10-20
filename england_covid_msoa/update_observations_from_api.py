import csv
import itertools
import json
import os
from operator import itemgetter

import csvsort

from .api import get_data_for_msoa

observations_fn = os.path.join("data", "observations.csv")
observations_new_fn = os.path.join("data", "observations.new.csv")
fetched_fn = os.path.join("data", "fetched.tmp.json")

try:
    with open(fetched_fn) as f:
        fetched = set(json.load(f))
except FileNotFoundError:
    fetched = set()

try:
    with open(observations_fn) as observations_f, open(
        observations_new_fn, "a" if fetched else "w"
    ) as observations_new_f:
        reader = csv.DictReader(observations_f)
        writer = csv.DictWriter(observations_new_f, reader.fieldnames)
        if not fetched:
            writer.writeheader()

        for i, (msoa, rows) in enumerate(
            itertools.groupby(reader, key=lambda row: row["msoa"])
        ):
            print(i)
            rows = list(rows)
            if msoa not in fetched:
                for row in get_data_for_msoa(msoa):
                    writer.writerow(row)
                fetched.add(msoa)
except BaseException:
    # Save what we've got so far
    with open(fetched_fn, "w") as f:
        json.dump(sorted(fetched), f)
    raise
else:
    with open(observations_fn, "a") as observations_f, open(
        observations_new_fn
    ) as observations_new_f:
        reader = csv.DictReader(observations_new_f)
        writer = csv.DictWriter(observations_f, reader.fieldnames)
        for row in reader:
            writer.writerow(row)

    csvsort.csvsort(observations_fn, [0, 2, 3])

    with open(observations_fn) as observations_f, open(
        observations_new_fn, "w"
    ) as observations_new_f:
        reader = csv.DictReader(observations_f)
        writer = csv.DictWriter(observations_new_f, reader.fieldnames)
        writer.writeheader()

        print(reader.fieldnames)

        for msoa, rows in itertools.groupby(reader, itemgetter("msoa")):
            for group, sub_rows in itertools.groupby(
                rows, itemgetter("specimenDate", "observationDate")
            ):
                sub_rows = sorted(sub_rows, key=itemgetter("fetchDate"))
                if len(set(row["rollingSum"] for row in sub_rows)) == 1:
                    # If the value hasn't changed, use the oldest fetch date
                    # so that the data stays stable
                    writer.writerow(sub_rows[0])
                else:
                    # Otherwise, use the newest, as the data has been updated.
                    writer.writerow(sub_rows[-1])

    csvsort.csvsort(observations_fn, [0, 2, 3])

    if os.path.exists(fetched_fn):
        os.unlink(fetched_fn)
    os.rename(observations_new_fn, observations_fn)
