import os
from dotenv import load_dotenv
import spotify_multitool as spm
from openpyxl import Workbook

workbook = Workbook()
sheet = workbook.active

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("URI_REDIR")

token = spm.get_token(client_id,client_secret)

playlist_id = spm.parse_input()

counter = 0
playlist, total_songs = spm.get_songs_from_playlist(token, playlist_id, 0)

playlist_name = spm.get_playlist_name(token, playlist_id)
print(playlist_name)
#print(spm.get_songs_from_playlist(token, playlist_id, 0))


print(f"Copying songs to: {playlist_name}.xlsx")
while (counter < total_songs):
    playlist, total_songs = spm.get_songs_from_playlist(token, playlist_id, counter)
    spm.print_songs(playlist, counter, workbook, sheet, playlist_name)
    counter = counter + 50

