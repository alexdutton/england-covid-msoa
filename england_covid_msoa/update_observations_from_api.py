import csv
import itertools
import os
from operator import itemgetter

import csvsort

from .api import get_data_for_msoa

observations_fn = os.path.join("data", "observations.csv")
observations_new_fn = os.path.join("data", "observations.new.csv")

with open(observations_fn) as observations_f, open(
    observations_new_fn, "w"
) as observations_new_f:
    reader = csv.DictReader(observations_f)
    writer = csv.DictWriter(observations_new_f, reader.fieldnames)
    writer.writeheader()

    for msoa, rows in itertools.groupby(reader, key=lambda row: row["msoa"]):
        rows = list(rows)
        rows.extend(get_data_for_msoa(msoa))
        for group, sub_rows in itertools.groupby(
            rows, itemgetter("specimenDate", "observationDate")
        ):
            sub_rows = sorted(sub_rows, key=itemgetter("fetchDate"))
            writer.writerow(sub_rows[-1])

csvsort.csvsort(observations_new_fn, [0, 2, 3])
