import requests
import re
import csv
from datetime import date
from bs4 import BeautifulSoup


competition_year = 2020
link_source = f"{competition_year}/links_men.txt"
num_to_scrape = 37

with open(link_source) as f:
  links = [s.strip() for s in f.readlines()]

def strip_seed(s):
  n = s.rindex('(')-1
  return s[:n]

def parse_tr(tr_soup, t_name):
  gameID = tr_soup['data-game']
  items = [str(i.get_text()).strip() for i in tr_soup.find_all(class_='adjust-data')]
  date_str = '0' + items[0][4:] + f'/{competition_year}'
  if len(date_str) < 10:
    date_str = date_str[:3] + '0' + date_str[3:]
  res_row = [gameID, t_name, date_str + ' ' + items[1], strip_seed(items[3]), strip_seed(items[4]), items[5], items[6]]
  return res_row

def parse_table(table_soup, t_name):
  res_rows = []
  soup_rows = table_soup.find_all('tr', attrs={'data-game':True})
  for r in soup_rows:
    if str(r.find(attrs={"data-type":"game-status"}).get_text()) != "Final":
      continue
    res_rows.append(parse_tr(r, t_name))
  return res_rows

def parse_bracket_game(b_soup, t_name):
  res_row = []
  res_row.append(str(b_soup['id'])[4:])
  res_row.append(t_name)
  date_str = '0' + str(b_soup.find(class_='date').get_text())
  if 'TBA' not in date_str and date_str.index(' ') < 10:
    date_str = date_str[:3] + '0' + date_str[3:]
  res_row.append(date_str)
  t1 = b_soup.find(class_='top_area')
  t2 = b_soup.find(class_='btm_area')
  res_row.append(strip_seed(str(t1.find(class_='isName').get_text()).strip()))
  res_row.append(strip_seed(str(t2.find(class_='isName').get_text()).strip()))
  res_row.append(str(t1.find(class_='isScore').get_text()).strip())
  res_row.append(str(t2.find(class_='isScore').get_text()).strip())
  return res_row

results = []
for i, link in enumerate(links[:num_to_scrape]):
  if (i % 10 == 0):
    print(f'{i}/{num_to_scrape} done')
    print(len(results), "games scraped")
  print(link)
  r = requests.get(link + "schedule/Men/CollegeMen/" )
  t_name = link[36:-1].replace('-', ' ').strip()

  soup = BeautifulSoup(r.content, 'html.parser')

  # Data Row:
  # GameID, Tournament Name, Date, Team 1, Team 2, Team 1 Score, Team 2 Score

  game_tables = soup.find_all(class_="scores_table")

  for gt in game_tables:
    results += parse_table(gt, t_name)

  bracket_games = soup.find_all('div', 'bracket_game')

  for g in bracket_games:
    if str(g.find(class_="game-status").get_text()) != "Final":
      continue
    results.append(parse_bracket_game(g, t_name))

print(len(results), "games scraped")
with open(f'{competition_year}/scraped/{str(date.today())}.csv', 'w', newline='') as csvfile:
  wr = csv.writer(csvfile)
  wr.writerow(['GameID', 'Tournament Name', 'Date', 'Team 1', 'Team 2', 'Team 1 Score', 'Team 2 Score'])
  for r in results:
    wr.writerow(r)


