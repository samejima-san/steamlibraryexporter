#INSERT INTO video_games (game_name, platform, year_played, rating, completed)
#VALUES

import json
import math

with open('steam_library.json', 'r') as f:
    data = json.load(f)

output = (f'INSERT INTO video_games (vg_name, hours_played) \n '
          f'VALUES ')
outputlist = []
for game in data:
    game_name = game['name'].replace("'", "''")
    hours_played = math.floor(game['playtime_forever'] / 60)
    outputlist.append([game_name, hours_played])

for i in range(len(outputlist)-2):
    output += f"('{outputlist[i][0]}', {outputlist[i][1]}), \n"
output += f"('{outputlist[-1][0]}', {outputlist[-1][1]});"

with open('query.txt', 'w') as f:
    f.write(output)
