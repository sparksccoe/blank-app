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

# Add radio button for choosing between entering playlist name or URL
input_choice = st.sidebar.radio("How would you like to enter the playlist?", ("by name", "by URL"))

# Initialize playlist_id as None
playlist_id = None

# Conditional input based on the user's choice
if input_choice == "by name":
    playlist_name = st.sidebar.text_input("Enter the public Spotify playlist name:")

    # Search for the playlist ID based on the name
    if playlist_name:
        try:
            playlists = sp.search(playlist_name, type="playlist")["playlists"]["items"]
            if playlists:
                playlist_id = playlists[0]["id"]
            else:
                st.write("No playlists found with that name.")
        except Exception as e:
            st.write("Error occurred while searching for the playlist.")
            st.write(f"Error: {e}")
else:
    playlist_url = st.sidebar.text_input("Enter the Spotify playlist URL:")

    # Extract the playlist ID from the URL
    if playlist_url:
        try:
            playlist_id = playlist_url.split("/")[-1].split("?")[0]  # Handles URLs with or without query params
        except Exception as e:
            st.write("Error occurred while extracting the playlist ID.")
            st.write(f"Error: {e}")

# retrieve data from the Spotify API
if playlist_id:
    playlist = sp.playlist(playlist_id)
    playlist_cover = playlist["images"][0]["url"]
    tracks = playlist["tracks"]["items"]
    track_id = [track["track"]["id"] for track in tracks]
    track_names = [track["track"]["name"] for track in tracks]
    track_artists = [", ".join([artist["name"] for artist in track["track"]["artists"]]) for track in tracks]
    track_popularity = [track["track"]["popularity"] for track in tracks]
    track_duration = [track["track"]["duration_ms"] for track in tracks]
    track_album = [track["track"]["album"]["name"] for track in tracks]
    track_preview = [track["track"]["preview_url"] for track in tracks]
    track_image = [track["track"]["album"]["images"][0]["url"] for track in tracks]
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

    # Extract genres by fetching artist details
    track_genres = []
    for track in tracks:
        artist_id = track["track"]["artists"][0]["id"]  # Get the first artist for simplicity
        artist = sp.artist(artist_id)  # Fetch artist information
        genres = artist.get("genres", [])  # Extract genres from artist
        first_genre = genres[0] if genres else "No genre available"  # Get the first genre, or a default if no genres exist
        track_genres.append(first_genre)

    # display the playlist data in a table
    st.write(f"## {playlist['name']}")
    st.image(playlist_cover, width=300)
    if playlist.get('description'):
        st.write(f"**Description:** {playlist['description']}")
    st.write(f"**Number of tracks:** {len(tracks)}")
    # st.write("")
    # st.write("### Tracklist")
    # st.write("| Name | Artist | Release Date | :blue[Popularity] | :green[Danceability] | :orange[Energy] | :red[Happiness] | :violet[Speechiness] | :gray[Tempo] |")
    # for i in range(len(tracks)):
    #     st.write(f"| {track_names[i]} | {track_artists[i]} | {track_release_date[i]} | :blue[{track_popularity[i]}] | :green[{track_danceability[i]}] | :orange[{track_energy[i]}] | :red[{track_valence[i]}] | :violet[{track_speechiness[i]}] | :gray[{track_tempo[i]}] |")

# data = {"Image": track_image, "Name": track_names, "Preview": track_preview, "Artist": track_artists, "Release Date": track_release_date, "Popularity": track_popularity, "Duration (ms)": track_duration, "Acoustic": track_acousticness, "Dance": track_danceability, "Energy": track_energy, "Happy": track_valence, "Instrumental": track_instrumentalness, "Key": track_key, "Live": track_liveness, "Loud (Db)": track_loudness, "Speech": track_speechiness, "Tempo": track_tempo}
if playlist_id:
    data = {"Image": track_image, "Name": track_names, "Artist": track_artists, "Release Date": track_release_date, "Popularity": track_popularity, "Duration (ms)": track_duration, "Acoustic": track_acousticness, "Dance": track_danceability, "Energy": track_energy, "Happy": track_valence, "Instrumental": track_instrumentalness, "Key": track_key, "Live": track_liveness, "Loud (Db)": track_loudness, "Speech": track_speechiness, "Tempo": track_tempo}
    df = pd.DataFrame(data)
    num_total_tracks = len(df)
    df.index += 1
    st.write("The table below is scrollable both horizontally and vertically. Each column can be clicked to sort in ascending or descending order. Hovering over a column header will explain what that feature represents.")
    st.data_editor(
        df,
        column_config={
            "Image": st.column_config.ImageColumn(
            "Album Art", help="Click on the album cover to enlarge"
            ),
            "Name": st.column_config.TextColumn(
                "Track Name", help="The name of the track"
            ),
            "Artist": st.column_config.TextColumn(
                "Artist", help="The primary artist or band who performed the track"
            ),
            "Release Date": st.column_config.TextColumn(
                "Release Date", help="The date when the track or album was released"
            ),
            "Popularity": st.column_config.NumberColumn(
                "Popularity", help="The popularity score of the track (0 to 100)"
            ),
            "Duration (ms)": st.column_config.NumberColumn(
                "Duration (ms)", help="The duration of the track in milliseconds"
            ),
            "Acoustic": st.column_config.NumberColumn(
                "Acousticness", help="A measure of the acoustic quality of the track (0 to 1)"
            ),
            "Dance": st.column_config.NumberColumn(
                "Danceability", help="How suitable the track is for dancing (0 to 1)"
            ),
            "Energy": st.column_config.NumberColumn(
                "Energy", help="The intensity and activity level of the track (0 to 1)"
            ),
            "Happy": st.column_config.NumberColumn(
                "Valence", help="A measure of the musical positivity of the track (0 to 1)"
            ),
            "Instrumental": st.column_config.NumberColumn(
                "Instrumentalness", help="The likelihood that the track is instrumental (0 to 1)"
            ),
            "Key": st.column_config.NumberColumn(
                "Key", help="The musical key the track is composed in (0 to 11)"
            ),
            "Live": st.column_config.NumberColumn(
                "Liveness", help="The probability that the track was performed live (0 to 1)"
            ),
            "Loud (Db)": st.column_config.NumberColumn(
                "Loudness", help="The overall loudness of the track in decibels (dB)"
            ),
            "Speech": st.column_config.NumberColumn(
                "Speechiness", help="The presence of spoken words in the track (0 to 1)"
            ),
            "Tempo": st.column_config.NumberColumn(
                "Tempo", help="The tempo of the track in beats per minute (BPM)"
            )
        },
        disabled=True,
    )
    data2 = {"Name": track_names, "ID": track_id}
    df2 = pd.DataFrame(data2)
    selected_audio = st.selectbox("Select a song from the playlist to play its preview:", df2["Name"])
    if selected_audio:
        selected_url = df2[df2["Name"] == selected_audio]["ID"].values[0]
        embed_url = f"https://open.spotify.com/embed/track/{selected_url}"
        st.markdown(f'<iframe src="{embed_url}" width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

     # Features to choose from in the dropdown
    features = ["Popularity", "Duration (ms)", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]
    features_with_descriptions = [
    "Popularity: The popularity score of the track (0 to 100)",
    "Duration (ms): The duration of the track in milliseconds",
    "Acoustic: A measure of the acoustic quality of the track (0 to 1)",
    "Dance: How suitable the track is for dancing (0 to 1)",
    "Energy: The intensity and activity level of the track (0 to 1)",
    "Happy: A measure of the musical positivity of the track (0 to 1)",
    "Instrumental: The likelihood that the track is instrumental (0 to 1)",
    "Key: The musical key the track is composed in (0 to 11)",
    "Live: The probability that the track was performed live (0 to 1)",
    "Loud (Db): The overall loudness of the track in decibels",
    "Speech: The presence of spoken words in the track (0 to 1)",
    "Tempo: The tempo of the track in beats per minute (BPM)"
    ]
    selected_feature_with_description = st.selectbox("Select an audio feature to rank tracks by:", features_with_descriptions)
    # Extract the feature name from the selected option (before the colon)
    selected_feature = selected_feature_with_description.split(":")[0]
    num_tracks = st.slider(f"How many tracks do you want to display?", min_value=1, max_value=num_total_tracks, value=3)
    sorted_df = df.sort_values(by=selected_feature, ascending=False)
    st.write(f"### Top {num_tracks} Tracks by {selected_feature}")
    st.dataframe(sorted_df.head(num_tracks)[["Name", "Artist", selected_feature]], hide_index=True)
    sorted_df_ascending = df.sort_values(by=selected_feature, ascending=True)
    st.write(f"### Lowest {num_tracks} Tracks by {selected_feature}")
    st.dataframe(sorted_df_ascending.head(num_tracks)[["Name", "Artist", selected_feature]], hide_index=True) 


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
