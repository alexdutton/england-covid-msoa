import collections
import csv
import itertools
import operator
from datetime import date, timedelta

import csvsort


specimen_dates = set()
msoas = set()

with open('data/observations.csv') as f:
    for row in csv.DictReader(f):
        specimen_dates.add(row['specimenDate'])
        msoas.add(row['msoa'])

csvsort.csvsort('data/observations.csv', ['specimenDate', 'msoa', 'observationDate'], 'data/observations-by-date.csv')

first_specimen_date = date(*map(int, min(specimen_dates).split('-')))
last_specimen_date = date(*map(int, max(specimen_dates).split('-')))

specimen_dates = [
    (first_specimen_date + timedelta(n)).isoformat()
    for n in range((last_specimen_date - first_specimen_date).days + 1)
]

print(specimen_dates)

fieldnames = ['specimenDate'] + sorted(msoas)

totals = collections.defaultdict(int)


with open('data/observations-by-date.csv') as f, open('data/latest.csv', 'w') as g:
    reader = csv.DictReader(f)
    writer = csv.DictWriter(g, fieldnames)

    writer.writeheader()

    for specimen_date, rows in itertools.groupby(reader, operator.itemgetter('specimenDate')):
        row = {
            'specimenDate': specimen_date,
        }
        for msoa, rows in itertools.groupby(rows, operator.itemgetter('msoa')):
            rolling_sum = list(rows)[-1]['rollingSum']
            row[msoa] = rolling_sum or 'S'
            totals[specimen_date] += int(rolling_sum or 0)
        writer.writerow(row)

with open('data/totals.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['date', 'rollingSum'])
    writer.writeheader()
    for date in specimen_dates:
        writer.writerow({'date': date, 'rollingSum': totals[date]})
