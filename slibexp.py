import math

import requests
import json
from howlongtobeatpy import HowLongToBeat
import psycopg2

import os
from dotenv import load_dotenv
load_dotenv()
# Replace with your Steam API key and Steam ID
API_KEY = os.getenv("API_KEY")
STEAM_ID = os.getenv("STEAM_ID")

# Connect to your database
conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    host="localhost",  # Change if using a remote server
    port="5432"
)


# Get owned games from Steam API
def get_steam_library(api_key, steam_id):
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'include_appinfo': True,  # Includes game names and icons
        'include_played_free_games': False  # Includes free-to-play games
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        games = data.get('response', {}).get('games', [])
        return games
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def write_new_json():
    # Fetch your library
    library = get_steam_library(API_KEY, STEAM_ID)

    # Print the library
    for game in library:
        print(f"Game: {game['name']}, Playtime: {game['playtime_forever']} minutes")


    with open('steam_library.json', 'w') as f:
        json.dump(library, f, indent=4)
        print("Library saved to steam_library.json")

def update_gametime():
    #this will be a function that gets the games that i finished but i dont know how many hours i played in them
    #due to the platform and replaces the 0 in hours_played with the how long to beat average time.
    cur = conn.cursor()

    # Query to fetch all games
    cur.execute("SELECT vg_name, hours_played, finished FROM lib;")

    # Fetch all results
    games = cur.fetchall()
    gamehash = {}
    steamlibrary = get_steam_library(API_KEY, STEAM_ID)
    steamhash = {}

    for game in steamlibrary:
        steamhash[game['name']] = math.floor(game['playtime_forever']/60)

    # Print results
    for game in games:
        gamehash[game[0]] = game[1]
    output = ""

    for key, value in steamhash.items():
        if key in gamehash:
            if value > gamehash[key]:
                output += f"UPDATE lib SET hours_played = {value} WHERE vg_name = '{key}'; \n"


    outputlist = []
    for key, value in steamhash.items():
        if key not in gamehash and key != 'Wallpaper Engine':
            outputlist.append([key.replace("'","''"), value])

    if len(outputlist) >= 1:
        output += f"\nINSERT INTO lib(vg_name, hours_played)\nVALUES"

    if len(outputlist) == 1:
        output += f"('{outputlist[0][0]}',{outputlist[0][1]});"
    elif len(outputlist) > 1:
        for i in range(len(outputlist)-2):
            output += f"('{outputlist[i][0]}', {outputlist[i][1]}),\n"
        output += f"('{outputlist[-1][0]}',{outputlist[-1][1]});"

    with open('updatequery.txt', 'w') as f:
        f.write(output)
    # Close connection
    cur.close()
    conn.close()

def add_data_for_lost_hours():
    #this function will add the hours to the games where i lost how many hours it took to take
    #it will just use the how long to beat data in because thats generally accurate
    cur = conn.cursor()
    hltb = HowLongToBeat()

    # Query to fetch all games
    cur.execute("SELECT vg_name FROM lib \nWHERE hours_played = 0 AND finished = true;")
    games = cur.fetchall()

    gamesonly = [g[0] for g in games]
    howlonggames = []
    #game_name main_story
    for game in games:
        howlonggames += hltb.search(game[0])

    output = ""
    for game in howlonggames:
        if game.game_name in gamesonly:
            output+=f"UPDATE lib\nSET hours_played = {math.floor(game.main_story)}\nWHERE vg_name = '{game.game_name}';\n\n"

    with open('missingdata.txt', 'w') as f:
        f.write(output)

    cur.close()
    conn.close()

if __name__ == "__main__":
    #update_gametime()
    #add_data_for_lost_hours()
    pass



