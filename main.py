import sqlite3
from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

conn = sqlite3.connect('spotify.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS Songs
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   song_name TEXT,
                   popularity INTEGER,
                   type TEXT,
                   artist_id INTEGER,
                   FOREIGN KEY (artist_id) REFERENCES Artists(id))''')

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers = headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token
    
def get_auth_header(token):
    return { "Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers= headers)

    json_result = result.json().get("artists", {}).get("items", [])
    if not json_result:
        print("No artist with this name exists.")
        return None
    
    return json_result[0]
    

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json().get("tracks", [])
    return json_result

   
def insert_song_data(song_data, result):
    sql = '''INSERT INTO Songs (song_name, popularity, type, artist_id)
             VALUES (?, ?, ?, ?)'''
    cursor.execute(sql, (song_data['name'], song_data['popularity'], song_data['type'], result['name']))
    conn.commit()


token = get_token()

cursor.execute("DELETE FROM Songs")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='Songs'")


result = search_for_artist(token, "Mardigal")
if result:

    artist_id = result["id"]
    
    songs = get_songs_by_artist(token, artist_id)
    if songs:
        
        for song in songs:
            insert_song_data(song, result)
        print("Songs inserted successfully.")
    else:
        print("No songs found for the artist.")
else:
    print("Artist not found.")



cursor.execute("SELECT * FROM Songs")
rows = cursor.fetchall()
print("\nSongs Table:")
print("ID | Song Name | Popularity | Type | Artist ID")
for row in rows:
    print(row)

conn.close()






