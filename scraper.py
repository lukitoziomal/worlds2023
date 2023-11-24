import csv
import requests
from bs4 import BeautifulSoup


GAMES = []
PERFORMANCES = []
GAME_NUMBER = 1


def scrape(stage):
    global GAME_NUMBER
    url = f'https://lol.fandom.com/wiki/2023_Season_World_Championship/Main_Event/Scoreboards{stage}'
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    games = soup.find_all('table', {'class': 'sb'})
    for game in games:
        row = [GAME_NUMBER]

# , {'class': 'to_hasTooltip'}
        # team names
        for t in game.find_all('th', {'class': 'sb-teamname'}):
            row.append(t.find('a').get('title'))

        # winner
        row.append(row[1]) if 'sb-score-winner' in game.find('th', {'class': 'side-blue'})['class'] else row.append(row[2])

        # game length
        length = [t for t in game.find_all('th', {'colspan': '2'}) if len(str(t)) < 30]
        row.append(length[0].get_text())

        # gold
        for g in game.find_all('div', {'class': 'sb-header-Gold'}):
            row.append(g.get_text().strip())

        # kills
        for k in game.find_all('div', {'class': 'sb-header-Kills'}):
            row.append(k.get_text().strip())

        # bans
        for side in game.find_all('div', {'class': 'sb-footer-bans'})[1::2]:
            bans = []
            for b in side.find_all('span', {'class': 'sprite champion-sprite'}):
                bans.append(b['title'])
            row.append(bans)

        # objectives
        # towers - inhibitors - barons - dragons - heralds
        for side in game.find_all('div', {'class': 'sb-footer-stats'}):
            for obj in side.find_all('div'):
                row.append(obj.get_text().strip())

        # performance
        idx = 1
        for i, player in enumerate(game.find_all('div', {'class': 'sb-p'})):
            performance = [
                GAME_NUMBER,
                row[idx],
                player.find('div', {'class': 'sb-p-name'}).get_text(),
                player.find('span', {'class': 'sprite champion-sprite'})['title']
            ]

            for stat in player.find_all('div', {'class': 'sb-p-stat'}):
                for x in stat.get_text().split('/'):
                    performance.append(x)

            performance.append(player.find('div', {'class': 'sb-p-rune'}).find('span')['title'][5:])

            items = [item['title'] for item in player.find_all('span', {'class': 'sprite item-sprite'})[1:] if
                     item['title'] != '']
            performance.append(items)
            PERFORMANCES.append(performance)
            if i == 4:
                idx += 1

        GAMES.append(row)
        GAME_NUMBER += 1


if __name__ == '__main__':
    rounds = [
        '',
        '/Round_3',
        '/Round_4',
        '/Round_5',
        '/Quarterfinals',
        '/Semifinals_and_Finals'
    ]
    for round in rounds:
        scrape(round)

    games_columns = ['gameID', 'team1', 'team2', 'winner', 'duration', 'gold1', 'gold2', 'kills1', 'kills2', 'bans1',
                     'bans2', 'towers1', 'inhibs1', 'barons1', 'dragons1', 'heralds1', 'towers2', 'inhibs2', 'barons2',
                     'dragons2', 'heralds2']
    performances_columns = ['gameID', 'team', 'player', 'champion', 'kills', 'deaths', 'assists', 'cs', 'gold', 'items']
    with open('./games.csv', 'w', newline='', encoding='utf-8') as f1:
        writer = csv.writer(f1)
        writer.writerow(games_columns)
        writer.writerows(GAMES)

    with open('./performances.csv', 'w', newline='', encoding='utf-8') as f2:
        writer = csv.writer(f2)
        writer.writerow(performances_columns)
        writer.writerows(PERFORMANCES)