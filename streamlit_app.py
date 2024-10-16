import streamlit as st

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


import spotipy
from PIL import Image
from spotipy.oauth2 import SpotifyClientCredentials

client_id = '922604ee2b934fbd9d1223f4ec023fba'
client_secret = '1bdf88cb16d64e54ba30220a8f126997'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


import pandas as pd
import plotly.express as px
from datetime import datetime


image = Image.open('data_adventures_logo.png')
st.sidebar.image(image)
st.title("Data Adventures in Music")
st.write('Let’s dive into a Data Adventure with your playlist!')

playlist_name = st.sidebar.text_input("Enter the name of the Spotify playlist:")

# search for the playlist ID based on the name
if playlist_name:
    playlists = sp.search(playlist_name, type="playlist")["playlists"]["items"]
    if playlists:
        playlist_id = playlists[0]["id"]
    else:
        st.write("No playlists found with that name.")
        playlist_id = None
else:
    playlist_id = None

# retrieve data from the Spotify API
if playlist_id:
    playlist = sp.playlist(playlist_id)
    tracks = playlist["tracks"]["items"]
    track_names = [track["track"]["name"] for track in tracks]
    track_artists = [", ".join([artist["name"] for artist in track["track"]["artists"]]) for track in tracks]
    track_popularity = [track["track"]["popularity"] for track in tracks]
    track_duration = [track["track"]["duration_ms"] for track in tracks]
    track_album = [track["track"]["album"]["name"] for track in tracks]
    track_release_date = [track["track"]["album"]["release_date"] for track in tracks]
    track_url = [track["track"]["external_urls"]["spotify"] for track in tracks]
    audio_features = sp.audio_features(track_url)
    track_danceability = [track["danceability"] for track in audio_features]
    track_energy = [track["energy"] for track in audio_features]
    track_loudness = [track["loudness"] for track in audio_features]
    track_acousticness = [track["acousticness"] for track in audio_features]
    track_instrumentalness = [track["instrumentalness"] for track in audio_features]
    track_liveness = [track["liveness"] for track in audio_features]
    track_valence = [track["valence"] for track in audio_features]
    track_tempo = [track["tempo"] for track in audio_features]
    track_signature = [track["time_signature"] for track in audio_features]
    track_speechiness = [track["speechiness"] for track in audio_features]
    track_key = [track["key"] for track in audio_features]

    # display the playlist data in a table
    st.write(f"## {playlist['name']}")
    st.write(f"**Description:** {playlist['description']}")
    st.write(f"**Number of tracks:** {len(tracks)}")
    st.write("")
    st.write("### Tracklist")
    st.write("| Name | Artist | Release Date | :blue[Popularity] | :green[Danceability] | :orange[Energy] | :red[Happiness] | :violet[Speechiness] | :gray[Tempo] |")
    for i in range(len(tracks)):
        st.write(f"| {track_names[i]} | {track_artists[i]} | {track_release_date[i]} | :blue[{track_popularity[i]}] | :green[{track_danceability[i]}] | :orange[{track_energy[i]}] | :red[{track_valence[i]}] | :violet[{track_speechiness[i]}] | :gray[{track_tempo[i]}] |")

    # # analyze the playlist data
    # st.write("")
    # st.write("### Playlist Analysis")

    # # create a dataframe from the playlist data
    # data = {"Name": track_names, "Artist": track_artists, "Album": track_album, "Release Date": track_release_date, "Popularity": track_popularity, "Duration (ms)": track_duration}
    # df = pd.DataFrame(data)

    # # display a histogram of track popularity
    # fig_popularity = px.histogram(df, x="Popularity", nbins=20, title="Track Popularity Distribution")
    # st.plotly_chart(fig_popularity)


    # # add a dropdown menu for bivariate analysis
    # st.write("#### Bivariate Analysis")
    # x_axis = st.selectbox("Select a variable for the x-axis:", ["Popularity", "Duration (ms)","Release Date"])
    # y_axis = st.selectbox("Select a variable for the y-axis:", ["Popularity", "Duration (ms)", "Release Date"])
    # fig_bivariate = px.scatter(df, x=x_axis, y=y_axis, title=f"{x_axis} vs. {y_axis}")
    # st.plotly_chart(fig_bivariate)

    # # add a dropdown menu for multivariate analysis
    # st.write("#### Multivariate Analysis")
    # color_by = st.selectbox("Select a variable to color by:", ["Artist", "Album", "Release Date"])
    # size_by = st.selectbox("Select a variable to size by:", ["Popularity", "Duration (ms)"])
    # fig_multivariate = px.scatter(df, x="Duration (ms)", y="Popularity", color=color_by, size=size_by, hover_name="Name", title="Duration vs. Popularity Colored by Artist")
    # st.plotly_chart(fig_multivariate)

    # # add a summary of the playlist data
    # st.write("")
    # st.write("### Playlist Summary")
    # st.write(f"**Most popular track:** {df.iloc[df['Popularity'].idxmax()]['Name']} by {df.iloc[df['Popularity'].idxmax()]['Artist']} ({df['Popularity'].max()} popularity)")
    # st.write(f"**Least popular track:** {df.iloc[df['Popularity'].idxmin()]['Name']} by {df.iloc[df['Popularity'].idxmin()]['Artist']} ({df['Popularity'].min()} popularity)")
