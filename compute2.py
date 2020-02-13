
#   0   ,     1     ,   2  ,     3  ,    4   ,       5      ,       6
# GameID, Tournament,  Date,  Team 1,  Team 2,  Team 1 Score,  Team 2 Score

# https://play.usaultimate.org/teams/events/rankings/#algorithm

import glob
import csv
from datetime import datetime, date
import math
from collections import defaultdict

n_iter = 1000
week_of_season = 3
competition_year = 2020
season_start = datetime(competition_year, 1, 15)  
compute_date = str(date.today())
compute_date = '2020-02-11'

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

def date_weight(date_string):
  d = datetime.strptime(date_string[:10], '%m/%d/%Y')
  week_diff = math.ceil((d - season_start).days / 7)
  return date_weight2(week_diff)

teams = dict()                 # team -> rating; acts as a set of all teams
team_games = defaultdict(list) # team -> list of games;
team_rws = defaultdict(list)   # team -> list of (rating_diff, weight) pairs corresponding to games
ignored = set()                # set of GameIDs that should be ignored
graph_edges = []
team_win_loss = defaultdict(lambda: [0,0])

with open(f'{competition_year}/scraped/{compute_date}.csv') as csvfile:
  rd = csv.reader(csvfile)
  next(rd) # get rid of header line
  for row in rd:
    if row[5] in 'FWL' or row[6] in 'FWL': # skip forfeited games for now
      continue
    # GameID, score, opponent score, opponent, date, tournament
    score1 = int(row[5])
    score2 = int(row[6])
    # ignore games with score 1-0; considering it equivalent to a forfeit (to avoid divide-by-zero)
    if (score1 == 1 and score2 == 0) or (score1 == 0 and score2 == 1):
      continue
    if score1 > score2:
      r_diff = game_r_diff(score1, score2)
      r_weight = score_weight(score1, score2) * date_weight(row[2])
      team_win_loss[row[3]][0]+=1
      team_win_loss[row[4]][1]+=1
    else:
      r_diff = -game_r_diff(score2, score1)
      r_weight = score_weight(score2, score1) * date_weight(row[2])
      team_win_loss[row[3]][1]+=1
      team_win_loss[row[4]][0]+=1
    teams[row[3]] = 1000 # initialize rating at 1000
    team_games[row[3]].append((int(row[0]), score1, score2, row[4], row[2], row[1]))
    team_rws[row[3]].append((r_diff, r_weight))
    teams[row[4]] = 1000
    team_rws[row[4]].append((-r_diff, r_weight))
    team_games[row[4]].append((int(row[0]), score2, score1, row[3], row[2], row[1]))
    graph_edges.append((row[3], row[4]))

def reset(teams):
  for t in teams:
    teams[t] = 1000

def iterate(teams, team_games, team_rws, ignored):
  # update all ratings
  new_rs = dict() # temp storage for ratings while calculating
  for team in teams:
    rws = team_rws[team]
    games = team_games[team]
    total = 0
    w_total = 0
    for game, rw in zip(games, rws):
      if game[0] not in ignored:
        total += (teams[game[3]] + rw[0]) * rw[1]
        w_total += rw[1]
    new_rs[team] = total / w_total
  for t in new_rs:
    teams[t] = new_rs[t]
  
def check_games(teams, team_games, team_rws, ignored):
  r_team_list = reversed(sorted((teams[t], t) for t in teams))
  for _,team in r_team_list:
    games = team_games[team]
    opps = [g[3] for g in games]
    rs_weighted = [(rw[0] + teams[opp]) * rw[1] for rw, opp in zip(team_rws[team], opps)]
    to_check = sorted(zip(rs_weighted, games))
    n_games_included = len([g for g in games if g[0] not in ignored])
    for _, game in to_check:
      game_id, t_score, o_score, opp, _, _ = game
      if t_score > o_score:
        if teams[team] > teams[opp] + 600 and t_score > o_score * 2 + 1 and n_games_included > 5:
          # no one cares about losers, so losers are allowed to have less than 5 counted games
          # (which is why the following line is commented out)
          #if sum(g[0] not in ignored for g in team_games[opp]) > 5:
          ignored.add(game_id)
          n_games_included -= 1

  
for i in range(n_iter):
  iterate(teams, team_games, team_rws, ignored)

for _ in range(4):
  ignored.clear()
  check_games(teams, team_games, team_rws, ignored)
  #reset(teams)
  for i in range(n_iter):
    iterate(teams, team_games, team_rws, ignored)


ranks = [(teams[t], t) for t in teams]
ranks.sort()
ranks.reverse()

for i, e in enumerate(ranks[:25]):
  w_l = team_win_loss[e[1]]
  print(f"{i+1:{2}}: {e[1]:{32}} {w_l[0]:{2}} - {w_l[1]}      {round(e[0], 2)} ")



with open(f'{competition_year}/rankings/{compute_date}.csv', 'w', newline='') as csvfile:
  wr = csv.writer(csvfile)
  wr.writerow(['Team', 'Rating'])
  for r in ranks:
    wr.writerow([r[1], r[0]])

with open(f'{competition_year}/connections/{compute_date}.csv', 'w', newline='') as csvfile:
  wr = csv.writer(csvfile)
  for e in graph_edges:
    wr.writerow(e)
