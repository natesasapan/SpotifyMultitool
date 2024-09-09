import os
from dotenv import load_dotenv
import base64
from requests import post,get
import json
import requests
from PIL import Image
import io

load_dotenv()


def get_token(client_id, client_secret):
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
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?market=US&fields=total%2Citems%28track%28album%28name%2Cimages%28url%29%29%2Cartists%28name%29%2Cname%29%29&limit=50&offset={offset}"
    #url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?market=US&fields=total%2Citems%28track%28album%28name%29%2Cartists%28name%29%2Cname%29%29&limit=50&offset={offset}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    song_total = json.loads(result.content)["total"]
    return json_result, song_total


def get_playlist_name(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}?market=US&fields=name"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["name"]
    return json_result

def print_songs(playlist_json, offset, workbook, sheet, playlist_name):

    for index, song in enumerate(playlist_json, start=1):
        track_name = song["track"]["name"]
        artist_name = song["track"]["artists"][0]["name"]
        if artist_name == "":
            artist_name = "Unknown Artist"

        currentNum = index + offset
        sheetA = ("A%s") %currentNum
        sheetB = ("B%s") %currentNum
        sheet[sheetA] = track_name
        sheet[sheetB] = artist_name        
    
        print(f"{currentNum}. {track_name} by {artist_name}")

        workbook.save(filename=f"{playlist_name}.xlsx")

def parse_input(playlist_id):
    url = playlist_id

    start_index = url.find("playlist/") + len("playlist/")
    end_index = url.find("?", start_index) if "?" in url else len(url)

    playlist_id = url[start_index:end_index]
    return playlist_id

def fetch_album_cover(url):
    response = requests.get(url)
    return Image.open(io.BytesIO(response.content))