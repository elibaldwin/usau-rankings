
#     0     ,   1  ,     2  ,    3   ,       4      ,       5
# Tournament,  Date,  Team 1,  Team 2,  Team 1 Score,  Team 2 Score

# https://play.usaultimate.org/teams/events/rankings/#algorithm

import glob
import csv
import datetime
import math
from collections import defaultdict

week_of_season = 1

date_weight_multiplier = 2 if week_of_season == 1 else 2**(1.0/(week_of_season-1))

def game_r_diff(w_score, l_score):
  r = l_score / (w_score - 1)
  diff = 125 + 475 * ( (math.sin(min(1, (1-r)/.5) * 0.4 * math.pi)) / math.sin(0.4*math.pi) )
  return diff

def score_weight(w_score, l_score):
  return min(1.0, math.sqrt((w_score + max(l_score, math.floor((w_score-1)/2))) / 19))

def date_weight2(week_num):
  global date_weight_multiplier
  return 0.5 * date_weight_multiplier**(week_num-1)

def date_weight(date):
  return 0.5


teams = dict() # team name -> rating
team_games = defaultdict(list)

# initialize

with open('2020/aggregate/2020-01-28.csv') as csvfile:
  rd = csv.reader(csvfile)
  next(rd) # get rid of header line
  for row in rd:
    if row[4] in 'FW': # skip forfeited games for now
      continue
    # score, opponent score, opponent, date, tournament
    teams[row[2]] = 1000 # initialize rating at 1000
    team_games[row[2]].append((int(row[4]), int(row[5]), row[3], row[1], row[0]))
    teams[row[3]] = 1000
    team_games[row[3]].append((int(row[5]), int(row[4]), row[2], row[1], row[0]))

def iterate(teams, team_games):
  new_rs = dict()
  for team in teams:
    games = team_games[team] # get all games played by this team
    g_ratings = []
    g_weights = []
    for t_score, o_score, opp, date, _ in games:
      if t_score > o_score: # team won
        dr = game_r_diff(t_score, o_score) 
        g_ratings.append(teams[opp] + dr) # add game rating differential to opponent's rating to get game rating
        g_weights.append(score_weight(t_score, o_score) * date_weight(date)) # multiply score weight and date weight
      else:                 # team lost
        dr = game_r_diff(o_score, t_score)
        g_ratings.append(teams[opp] - dr)
        g_weights.append(score_weight(o_score, t_score) * date_weight(date))
    new_r = sum(r * g for r,g in zip(g_ratings, g_weights)) / sum(g_weights) # weighted average of game ratings
    new_rs[team] = new_r
  # update all ratings to finish the iteration
  for team in teams:
    teams[team] = new_rs[team]

for i in range(100):
  iterate(teams, team_games)

ranks = []
for team in teams:
  ranks.append((teams[team], team))

ranks.sort()
ranks.reverse()

for e in ranks[:25]:
  print(e[1], round(e[0]))




