import os
from dotenv import load_dotenv
import base64
from requests import post,get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("URI_REDIR")

conf = (client_id, client_secret, redirect_uri)

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers,data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


def get_user_playlists(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists?limit=1&offset=0"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_songs_from_playlist(token, playlist_id, offset):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks??market=US&fields=fields%3Ditems%28added_by.id%2Ctrack%28name%2Chref%2Calbum%28name%2Chref%29%29%29&limit=50&offset={offset}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    song_total = json.loads(result.content)["total"]
    return json_result, song_total

def print_songs(playlist_json, offset):

    for index, song in enumerate(playlist_json, start=1):
        track_name = song["track"]["name"]
        #artist_name = song["track"]["album"]["artists"][0]["name"]
        if "artists" in song["track"]["album"] and song["track"]["album"]["artists"]:
            artist_name = song["track"]["album"]["artists"][0]["name"]
        else:
            artist_name = "Unknown Artist"
    
        print(f"{index + offset}. {track_name} by {artist_name}")

def parse_input():
    print("Please enter the link to the playlist you'd like to copy: ")
    url = input()

    start_index = url.find("playlist/") + len("playlist/")
    end_index = url.find("?", start_index) if "?" in url else len(url)

    playlist_id = url[start_index:end_index]
    return playlist_id

#playlist_id = "130r8tmjyMRtQt1FRk765o"

token = get_token()

playlist_id = parse_input()

counter = 0
playlist, total_songs = get_songs_from_playlist(token, playlist_id, 0)

print("All songs: ")
while (counter < total_songs):
    playlist, total_songs = get_songs_from_playlist(token, playlist_id, counter)
    print_songs(playlist, counter)
    counter = counter + 50
