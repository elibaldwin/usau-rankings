import glob
import csv
from datetime import date

filenames = glob.glob("2020/processed/*.csv")

with open(f"2020/aggregate/{str(date.today())}.csv", 'w', newline='') as csvwr:
  wr = csv.writer(csvwr)
  wr.writerow(['Tournament', 'Date', 'Team 1', 'Team 2', 'Team 1 Score', 'Team 2 Score'])
  for s in filenames:
    with open(s) as csvrd:
      rd = csv.reader(csvrd)
      next(rd)
      for row in rd:
        wr.writerow(row)