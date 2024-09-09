import os
import streamlit as st
from dotenv import load_dotenv
import spotify_multitool as spm
from openpyxl import Workbook
import io
import math
import time

def main():
    st.title("Spotify Playlist Exporter")

    # Load environment variables
    load_dotenv()

    # Get Spotify API credentials
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("URI_REDIR")

    # Get Spotify token
    token = spm.get_token(client_id, client_secret)

    # User input for playlist ID
    playlist_id = spm.parse_input(st.text_input("Enter Spotify Playlist ID:"))

    if playlist_id:
        if st.button("Export Playlist"):
            try:
                 # Create a new workbook and get the active sheet
                workbook = Workbook()
                sheet = workbook.active

                # Get playlist information
                playlist_name = spm.get_playlist_name(token, playlist_id)
                st.success("Playlist found!")
                time.sleep(2)
                st.write(f"Exporting playlist: {playlist_name}")

                # Get all songs from the playlist
                counter = 0
                total_songs = 1  # Initialize with a non-zero value
                
                progress_bar = st.progress(0)
                
                while counter < total_songs:
                    playlist, total_songs = spm.get_songs_from_playlist(token, playlist_id, counter)
                    spm.print_songs(playlist, counter, workbook, sheet, playlist_name)
                    counter += 50
                    progress = min(counter / total_songs, 1.0)
                    progress_bar.progress(progress)


                # Save the workbook to a BytesIO object
                excel_file = io.BytesIO()
                workbook.save(excel_file)
                excel_file.seek(0)

                # Offer the Excel file for download
                st.download_button(
                    label="Download Excel file",
                    data=excel_file,
                    file_name=f"{playlist_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.success("Playlist exported successfully!")
            except Exception as e:
                st.error(f"The URL that you entered is incorrect. Please try again. {str(e)}")

if __name__ == "__main__":
    main()