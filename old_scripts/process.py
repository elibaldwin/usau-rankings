import glob
import csv

filenames = glob.glob("2020/*.csv")


def strip_seed(s):
  n = s.rindex('(')-1
  return s[:n]

for s in filenames:
  t_name = s[21:-4].replace("-", " ") # tournament name from filename
  print(t_name.title())
  # tournament, date-time, team-1, team-2, team-1-score, team-2-score
  new_data = []
  new_data.append(['tournament', 'date-time', 'team-1', 'team-2', 'team-1-score', 'team-2-score'])
  # 0,1,    2     ,   3   ,    4  ,       5     ,       6     ,   7 ,   8 ,   9   ,   10  ,  11
  # _,_, date-time, team-1, team-2, team-1-score, team-2-score, date, time, team-1, team-2, Score
  with open(s) as csvfile:
    rd = csv.reader(csvfile)
    
    next(rd)
    for row in rd:
      n_row = []
      n_row.append(t_name.title())
      if len(row[2]) == 0: # Came from pool-play table
        date_time_str = '0' + row[7][4:] + '/2020 ' + row[8]
        n_row.append(date_time_str)
        n_row.append(strip_seed(row[3]))
        n_row.append(strip_seed(row[4]))
        score = row[11].split()
        n_row.append(score[0])
        n_row.append(score[2])
      else:                # Came from bracket game
        n_row.append('0' + row[2])
        n_row.append(strip_seed(row[3]))
        n_row.append(strip_seed(row[4]))
        n_row.append(row[5])
        n_row.append(row[6])
      new_data.append(n_row)
  
  with open(f"2020/processed/{t_name.replace(' ','-')}_processed.csv", 'w', newline='') as csvfile:
    wr = csv.writer(csvfile)
    for row in new_data:
      wr.writerow(row)

       
