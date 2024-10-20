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
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from plotly.colors import qualitative


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
    track_tempo = [round(track["tempo"]) for track in audio_features]
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


    # Function to convert duration from milliseconds to minutes:seconds
    def ms_to_minutes_seconds(ms):
        minutes = ms // 60000  # Get minutes
        seconds = (ms % 60000) // 1000  # Get remaining seconds
        return f"{minutes}:{seconds:02d}"  # Format as mm:ss with zero-padded seconds

    # Apply the conversion to the track durations
    track_duration_formatted = [ms_to_minutes_seconds(duration) for duration in track_duration]
    


    # Convert track keys to pitch class notation
    # Map numeric key values to pitch class notation
    key_mapping = {
        -1: 'None',
        0: 'C',
        1: 'C# / Db',
        2: 'D',
        3: 'D# / Eb',
        4: 'E',
        5: 'F',
        6: 'F# / Gb',
        7: 'G',
        8: 'G# / Ab',
        9: 'A',
        10: 'A# / Bb',
        11: 'B'
    }

    # Convert track keys to pitch class notation
    track_keys_converted = [key_mapping[key] for key in track_key]


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
    data = {"Image": track_image, "Name": track_names, "Artist": track_artists, "Genre": track_genres, "Release Date": track_release_date, "Popularity": track_popularity, "Duration": track_duration_formatted, "Acoustic": track_acousticness, "Dance": track_danceability, "Energy": track_energy, "Happy": track_valence, "Instrumental": track_instrumentalness, "Key": track_keys_converted, "Live": track_liveness, "Loud (Db)": track_loudness, "Speech": track_speechiness, "Tempo": track_tempo}
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
            "Genre": st.column_config.TextColumn(
                "Genre", help="Genres are based on the primary artist, as Spotify doesn't provide genre information at the album or track level."
            ),
            "Release Date": st.column_config.TextColumn(
                "Release Date", help="The date when the track or album was released"
            ),
            "Popularity": st.column_config.NumberColumn(
                "Popularity", help="The popularity score of the track (0 to 100)"
            ),
            "Duration": st.column_config.TextColumn(
                "Duration", help="The duration of the track"
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
                "Instrumental", help="The likelihood that the track is instrumental (0 to 1)"
            ),
            "Key": st.column_config.TextColumn(
                "Key", help="The musical key the track is composed in (0 to 11)"
            ),
            "Live": st.column_config.NumberColumn(
                "Liveness", help="The probability that the track was performed live (0 to 1)"
            ),
            "Loud (Db)": st.column_config.NumberColumn(
                "Loudness", help="The average loudness of a track in decibels (dB), useful for comparing the relative loudness of tracks"
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
    features = ["Popularity", "Duration", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]
    features_with_descriptions = [
    "Popularity: The popularity score of the track (0 to 100)",
    "Duration: The duration of the track",
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

    # Playlist track_genres data 
    # Convert track_genres to a DataFrame for easier analysis
    df_genres = pd.DataFrame(track_genres, columns=["Genre"])

    # Count occurrences of each genre
    genre_counts = df_genres["Genre"].value_counts()

    # Calculate the percentage for each genre
    genre_percentages = (genre_counts / genre_counts.sum()) * 100
    # Sort genres by their percentage in descending order
    genre_percentages_sorted = genre_percentages.sort_values(ascending=False)

    # Calculate the cumulative sum and filter to only include genres up to 80%
    cumulative_percentages = genre_percentages_sorted.cumsum()
    top_genres_80 = genre_percentages_sorted[cumulative_percentages <= 80]

    st.write(f"### Main Genres of Songs")
    # Create a horizontal bar chart using Plotly to display top genres contributing to 80%
    fig = px.bar(
        top_genres_80,
        x=top_genres_80.values,
        y=top_genres_80.index,
        orientation='h',  # Horizontal bar chart
        labels={'x': 'Percentage of Songs (%)', 'y': 'Genres'},
        # title='Main Genres of Songs',
    )
    # Customize hovertemplate to show only the percentage
    fig.update_traces(hovertemplate='%{x:.2f}%<extra></extra>')
    # Customize the bar chart's appearance
    fig.update_layout(
        xaxis_title="Percentage of Songs (%)",
        yaxis_title="Genres",
        xaxis=dict(range=[0, 100]),  # Set x-axis range from 0 to 100
        margin=dict(t=0)  # Remove the space at the top of the chart
        # title_x=0  # Center the title
    )

    # Display the bar chart in Streamlit
    st.plotly_chart(fig, theme="streamlit")

    # Calculate the average popularity
    if track_popularity:
        average_popularity = sum(track_popularity) / len(track_popularity)
    else:
        average_popularity = 0

    # Display the average popularity
    st.write(f"The average popularity of the songs in this playlist is: {int(average_popularity)} / 100")
    # Show horizontal progress bar for average popularity (scaled between 0 and 100)
    st.progress(int(average_popularity))
    # Create a DataFrame to hold track names and popularity
    df_popularity = pd.DataFrame({
        'Track': track_names,
        'Popularity': track_popularity
    })
    # Define the bins for popularity (0-10%, 10-20%, etc.)
    bins = [i for i in range(0, 101, 10)]  # Create bins for every 10%
    # Assign each track to a bin
    df_popularity['Popularity Bin'] = pd.cut(df_popularity['Popularity'], bins=bins, right=False)
    # Calculate the percentage of songs in each popularity bin
    bin_counts = df_popularity['Popularity Bin'].value_counts(normalize=True) * 100
    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()
    # Create a DataFrame for the bar chart
    df_bins_popularity = pd.DataFrame({
        'Popularity Range': [f"{int(interval.left)}-{int(interval.right)}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })
    # Set the Popularity Range as the index for the chart
    df_bins_popularity.set_index('Popularity Range', inplace=True)
    # Display the bar chart of popularity ranges using st.bar_chart
    st.bar_chart(df_bins_popularity, x_label="Popularity Score", y_label="Percentage of songs")


    # Function to convert duration from milliseconds to minutes
    def ms_to_minutes(ms):
        return ms // 60000  # Convert milliseconds to minutes

    # Apply the conversion to the track durations
    track_durations_minutes = [ms_to_minutes(duration) for duration in track_duration]

    # Create bins for the durations (0-1 mins, 1-2 mins, etc.)
    bins = pd.cut(track_durations_minutes, bins=range(0, max(track_durations_minutes)+2), right=False)

    # Count the occurrences in each bin
    duration_counts = pd.value_counts(bins).sort_index()

    # Calculate the percentage of each bin
    total_tracks = len(track_durations_minutes)
    duration_percentages = (duration_counts / total_tracks) * 100  # Calculate percentage

    # Convert the bin intervals to strings for labeling
    duration_labels = [f"{int(interval.left)}-{int(interval.right)} mins" for interval in duration_counts.index]

    # Create a DataFrame for the donut chart
    df_durations = pd.DataFrame({
        'Duration Range': duration_labels,
        'Percentage': duration_percentages.round(1)  # Round to 1 decimal place
    })

    # Create the donut chart using Plotly
    fig_duration = px.pie(df_durations, values='Percentage', names='Duration Range', title='Track Durations by Minutes (Percentage)',
                hole=0.4)  # hole=0.4 makes it a donut chart

    # Display the donut chart in Streamlit
    st.plotly_chart(fig_duration)


    # Calculate the average acousticness
    if track_acousticness:
        average_acousticness = sum(track_acousticness) / len(track_acousticness)
    else:
        average_acousticness = 0

    # Display the average acousticness (0-1 scale)
    st.write(f"The average acousticness of the songs in this playlist is: {average_acousticness:.2f} / 1")

    # Show horizontal progress bar for average acousticness (scaled between 0 and 1)
    st.progress(int(average_acousticness * 100))  # Multiply by 100 for progress bar

    # Create a DataFrame to hold track names and acousticness
    df_acousticness = pd.DataFrame({
        'Track': track_names,
        'Acousticness': track_acousticness  # Keep acousticness in 0-1 range
    })

    # Define the bins for acousticness (0-0.1, 0.1-0.2, etc.)
    bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

    # Assign each track to a bin
    df_acousticness['Acousticness Bin'] = pd.cut(df_acousticness['Acousticness'], bins=bins, right=False)

    # Calculate the percentage of songs in each acousticness bin
    bin_counts = df_acousticness['Acousticness Bin'].value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_acousticness = pd.DataFrame({
        'Acousticness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Set the Acousticness Range as the index for the chart
    df_bins_acousticness.set_index('Acousticness Range', inplace=True)

    # Display the bar chart of acousticness ranges using st.bar_chart
    st.bar_chart(df_bins_acousticness, x_label="Acousticness Score", y_label="Percentage of songs")



# Calculate the average danceability
    if track_danceability:
        average_danceability = sum(track_danceability) / len(track_danceability)
    else:
        average_danceability = 0

    # Display the average danceability (0-1 scale)
    st.write(f"The average danceability of the songs in this playlist is: {average_danceability:.2f} / 1")

    # Show horizontal progress bar for average danceability (scaled between 0 and 1)
    st.progress(int(average_danceability * 100))  # Multiply by 100 for progress bar

    # Create a DataFrame to hold track names and danceability
    df_danceability = pd.DataFrame({
        'Track': track_names,
        'Danceability': track_danceability  # Keep danceability in 0-1 range
    })

    # Define the bins for danceability (0-0.1, 0.1-0.2, etc.)
    bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

    # Assign each track to a bin
    df_danceability['Danceability Bin'] = pd.cut(df_danceability['Danceability'], bins=bins, right=False)

    # Calculate the percentage of songs in each danceability bin
    bin_counts = df_danceability['Danceability Bin'].value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_danceability = pd.DataFrame({
        'Danceability Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Set the Danceability Range as the index for the chart
    df_bins_danceability.set_index('Danceability Range', inplace=True)

    # Display the bar chart of danceability ranges using st.bar_chart
    st.bar_chart(df_bins_danceability, x_label="Danceability Score", y_label="Percentage of songs")


# Calculate the average energy
    if track_energy:
        average_energy = sum(track_energy) / len(track_energy)
    else:
        average_energy = 0

    # Display the average energy (0-1 scale)
    st.write(f"The average energy of the songs in this playlist is: {average_energy:.2f} / 1")

    # Show horizontal progress bar for average energy (scaled between 0 and 1)
    st.progress(int(average_energy * 100))  # Multiply by 100 for progress bar

    # Create a DataFrame to hold track names and energy
    df_energy = pd.DataFrame({
        'Track': track_names,
        'Energy': track_energy  # Keep energy in 0-1 range
    })

    # Define the bins for energy (0-0.1, 0.1-0.2, etc.)
    bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

    # Assign each track to a bin
    df_energy['Energy Bin'] = pd.cut(df_energy['Energy'], bins=bins, right=False)

    # Calculate the percentage of songs in each energy bin
    bin_counts = df_energy['Energy Bin'].value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_energy = pd.DataFrame({
        'Energy Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Set the Energy Range as the index for the chart
    df_bins_energy.set_index('Energy Range', inplace=True)

    # Display the bar chart of energy ranges using st.bar_chart
    st.bar_chart(df_bins_energy, x_label="Energy Score", y_label="Percentage of Songs (%)")



   # Calculate the average happiness (valence)
    if track_valence:
        average_happiness = sum(track_valence) / len(track_valence)
    else:
        average_happiness = 0

    # Create a thicker progress bar using custom HTML and CSS for happiness
    progress_percentage = int(average_happiness * 100)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}%
        </div>
    </div>
    """

    # Display the average happiness (0-1 scale)
    st.write(f"The average happiness (valence) of the songs in this playlist is: {average_happiness:.2f} / 1")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and happiness (valence)
    df_happiness = pd.DataFrame({
        'Track': track_names,
        'Happiness (Valence)': track_valence  # Keep happiness (valence) in 0-1 range
    })

    # Define the bins for happiness (0-0.1, 0.1-0.2, etc.)
    bins = [i / 10 for i in range(0, 11)]  # Create bins for every 0.1

    # Assign each track to a bin
    df_happiness['Happiness Bin'] = pd.cut(df_happiness['Happiness (Valence)'], bins=bins, right=False)

    # Calculate the percentage of songs in each happiness bin
    bin_counts = df_happiness['Happiness Bin'].value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_happiness = pd.DataFrame({
        'Happiness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Create a vertical bar chart using Plotly
    fig_happiness = go.Figure(go.Bar(
        x=df_bins_happiness['Happiness Range'],  # The happiness categories
        y=df_bins_happiness['Percentage of Songs (%)'],  # The percentages
        text=[f"{perc:.1f}%" for perc in df_bins_happiness['Percentage of Songs (%)']],  # Display percentages as text inside the bars
        textposition='auto',  # Position the text inside the bars automatically
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A']),  # Custom colors
    ))

    # Update layout for the vertical bar chart
    fig_happiness.update_layout(
        title_text='Percentage of Songs by Happiness (Valence) Range',
        xaxis_title='Happiness (Valence) Range',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_happiness)





    # Calculate the average instrumentalness
    if track_instrumentalness:
        average_instrumentalness = sum(track_instrumentalness) / len(track_instrumentalness)
    else:
        average_instrumentalness = 0

    # Create a thicker progress bar using custom HTML and CSS for instrumentalness
    progress_percentage = int(average_instrumentalness * 100)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}%
        </div>
    </div>
    """

    # Display the average instrumentalness (0-1 scale)
    st.write(f"The average instrumentalness of the songs in this playlist is: {average_instrumentalness:.2f} / 1")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and instrumentalness
    df_instrumentalness = pd.DataFrame({
        'Track': track_names,
        'Instrumentalness': track_instrumentalness  # Keep instrumentalness in 0-1 range
    })

    # Define the bins for instrumentalness (0-0.1, 0.1-0.2, etc.)
    bins = [i / 10 for i in range(0, 11)]  # Create bins for every 0.1

    # Assign each track to a bin
    df_instrumentalness['Instrumentalness Bin'] = pd.cut(df_instrumentalness['Instrumentalness'], bins=bins, right=False)

    # Calculate the percentage of songs in each instrumentalness bin
    bin_counts = df_instrumentalness['Instrumentalness Bin'].value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_instrumentalness = pd.DataFrame({
        'Instrumentalness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Create a vertical bar chart using Plotly
    fig_instrumentalness = go.Figure(go.Bar(
        x=df_bins_instrumentalness['Instrumentalness Range'],  # The instrumentalness categories
        y=df_bins_instrumentalness['Percentage of Songs (%)'],  # The percentages
        text=[f"{perc:.1f}%" for perc in df_bins_instrumentalness['Percentage of Songs (%)']],  # Display percentages as text inside the bars
        textposition='auto',  # Position the text inside the bars automatically
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A']),  # Custom colors
    ))

    # Update layout for the vertical bar chart
    fig_instrumentalness.update_layout(
        title_text='Percentage of Songs by Instrumentalness Range',
        xaxis_title='Instrumentalness Range',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_instrumentalness)


# Create a DataFrame to hold track keys and their occurrences
    df_keys = pd.DataFrame(track_keys_converted, columns=['Key'])

    # Count the occurrences of each key
    key_counts = df_keys['Key'].value_counts(normalize=True) * 100  # Calculate percentage
    key_counts = key_counts.round(1).reset_index()  # Round the percentage values to one decimal place
    key_counts.columns = ['Key', 'Percentage']

    # Create the pie chart using Plotly
    fig_keys = px.pie(key_counts, values='Percentage', names='Key', title='Distribution of Musical Keys in Playlist (Percentage)')

    # Display the pie chart in Streamlit
    st.plotly_chart(fig_keys)



    # Calculate the average liveness
    if track_liveness:
        average_liveness = sum(track_liveness) / len(track_liveness)
    else:
        average_liveness = 0

    # Create a thicker progress bar using custom HTML and CSS for liveness
    progress_percentage = int(average_liveness * 100)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}%
        </div>
    </div>
    """

    # Display the average liveness (0-1 scale)
    st.write(f"The average liveness of the songs in this playlist is: {average_liveness:.2f} / 1")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and liveness
    df_liveness = pd.DataFrame({
        'Track': track_names,
        'Liveness': track_liveness  # Keep liveness in 0-1 range
    })

    # Define the bins for liveness (0-0.1, 0.1-0.2, etc.)
    bins = [i / 10 for i in range(0, 11)]  # Create bins for every 0.1

    # Assign each track to a bin
    df_liveness['Liveness Bin'] = pd.cut(df_liveness['Liveness'], bins=bins, right=False)

    # Calculate the percentage of songs in each liveness bin
    bin_counts = df_liveness['Liveness Bin'].value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_liveness = pd.DataFrame({
        'Liveness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Create a vertical bar chart using Plotly
    fig_liveness = go.Figure(go.Bar(
        x=df_bins_liveness['Liveness Range'],  # The liveness categories
        y=df_bins_liveness['Percentage of Songs (%)'],  # The percentages
        text=[f"{perc:.1f}%" for perc in df_bins_liveness['Percentage of Songs (%)']],  # Display percentages as text inside the bars
        textposition='auto',  # Position the text inside the bars automatically
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A']),  # Custom colors
    ))

    # Update layout for the vertical bar chart
    fig_liveness.update_layout(
        title_text='Percentage of Songs by Liveness Range',
        xaxis_title='Liveness Range',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_liveness)


    # Create bins for track loudness based on suggested ranges
    bins_loudness = [-60, -40, -30, -20, -10, 0]  # Define the bin edges
    labels_loudness = ['-60 to -40 dB', '-40 to -30 dB', '-30 to -20 dB', '-20 to -10 dB', '-10 to 0 dB']  # Labels for each bin

    # Categorize the loudness values into bins
    loudness_binned = pd.cut(track_loudness, bins=bins_loudness, labels=labels_loudness, right=False)

    # Count the occurrences of each bin
    loudness_binned_counts = loudness_binned.value_counts().sort_index()

    # Calculate the percentage for each bin
    total_tracks = len(track_loudness)
    loudness_binned_percentages = (loudness_binned_counts / total_tracks) * 100

    # Create a Plotly stacked horizontal bar chart using the calculated percentages
    fig_loudness = go.Figure()

    # Add the bar (each segment of the bar represents a loudness bin)
    fig_loudness.add_trace(go.Bar(
        x=loudness_binned_percentages.values,  # Use the calculated percentages
        y=loudness_binned_percentages.index,  
        orientation='h',
        text=[f"{perc:.1f}%" for perc in loudness_binned_percentages.values],  # Add text labels showing the percentages
        textposition='inside',  # Place the text labels inside the bar
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']),  # Colors for the segments
        hoverinfo='text',  # Show the text on hover
        hovertext=[f"{label}: {perc:.1f}%" for label, perc in zip(labels_loudness, loudness_binned_percentages.values)]  # Hover info
    ))

    # Update the layout to include custom x-axis ticks and a title
    fig_loudness.update_layout(
        title_text='Distribution of Songs by Loudness Range',
        xaxis_title='Percentage of Tracks (%)',
        yaxis_title='',
        xaxis=dict(
            tickvals=[0, 20, 40, 60, 80, 100],  # Custom ticks at 0, 20, 40, 60, 80, 100
            ticktext=['0%', '20%', '40%', '60%', '80%', '100%'],  # Display percentage symbols on the x-axis
            range=[0, 100]  # Ensure the x-axis covers the full range from 0 to 100
        ),
        barmode='stack',
        showlegend=False,  # Disable the legend as it is not needed,
        annotations=[
            dict(
                x=105,  # Positioning to the right of the chart
                y=0,  # Align with the y-axis
                xref="x",  # Refer to the x-axis
                yref="y",  # Refer to the y-axis
                text=(
                    "-60 dB to -40 dB: Very quiet or background noise.<br>"
                    "-40 dB to -30 dB: Soft, likely ambient or very quiet tracks.<br>"
                    "-30 dB to -20 dB: Moderately soft tracks.<br>"
                    "-20 dB to -10 dB: Typical dynamic range for commercial music.<br>"
                    "-10 dB to 0 dB: Loud, compressed, heavily mastered tracks."
                ),
                showarrow=False,  # No arrow needed, just text
                align="left",
                font=dict(size=10)  # Adjust the font size for the helper text
            )
        ]
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_loudness)

       # Calculate the average speechiness
    if track_speechiness:
        average_speechiness = sum(track_speechiness) / len(track_speechiness)
    else:
        average_speechiness = 0

    # Create a thicker progress bar using custom HTML and CSS
    progress_percentage = int(average_speechiness * 100)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}%
        </div>
    </div>
    """

    # Display the average speechiness (0-1 scale)
    st.write(f"The average speechiness of the songs in this playlist is: {average_speechiness:.2f} / 1")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and speechiness
    df_speechiness = pd.DataFrame({
        'Track': track_names,
        'Speechiness': track_speechiness  # Keep speechiness in 0-1 range
    })

    # Define the bins for speechiness (0-0.1, 0.1-0.2, etc.)
    bins = [i / 10 for i in range(0, 11)]  # Create bins for every 0.1

    # Assign each track to a bin
    df_speechiness['Speechiness Bin'] = pd.cut(df_speechiness['Speechiness'], bins=bins, right=False)

    # Calculate the percentage of songs in each speechiness bin
    bin_counts = df_speechiness['Speechiness Bin'].value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_speechiness = pd.DataFrame({
        'Speechiness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Create a vertical bar chart using Plotly
    fig_speechiness = go.Figure(go.Bar(
        x=df_bins_speechiness['Speechiness Range'],  # The speechiness categories
        y=df_bins_speechiness['Percentage of Songs (%)'],  # The percentages
        text=[f"{perc:.1f}%" for perc in df_bins_speechiness['Percentage of Songs (%)']],  # Display percentages as text inside the bars
        textposition='auto',  # Position the text inside the bars automatically
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A']),  # Custom colors
        # hoverinfo='skip'  # Skip hover info
    ))

    # Update layout for the vertical bar chart
    fig_speechiness.update_layout(
        title_text='Percentage of Songs by Speechiness Range',
        xaxis_title='Speechiness Range',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_speechiness)



    # Define tempo categories with their corresponding ranges
    def categorize_tempo(tempo):
        if tempo < 60:
            return "Largo (Very Slow)"
        elif 60 <= tempo < 76:
            return "Adagio (Slow)"
        elif 76 <= tempo < 108:
            return "Andante (Moderate)"
        elif 108 <= tempo < 120:
            return "Moderato (Moderate/Fast)"
        elif 120 <= tempo < 156:
            return "Allegro (Fast)"
        elif 156 <= tempo < 200:
            return "Presto (Very Fast)"
        else:
            return "Prestissimo (Extremely Fast)"

    # Apply the categorization to the track_tempo list
    track_tempo_categories = [categorize_tempo(tempo) for tempo in track_tempo]

    # Create a DataFrame to count the occurrences of each tempo category
    df_tempo = pd.DataFrame({
        'Tempo Category': track_tempo_categories
    })

    # Count the occurrences of each tempo category and calculate percentages
    tempo_counts = df_tempo['Tempo Category'].value_counts(normalize=True) * 100
    tempo_counts = tempo_counts.sort_index()  # Sort categories alphabetically or based on a custom order

    # Create a Plotly horizontal bar chart
    fig_tempo = go.Figure(go.Bar(
        x=tempo_counts.values,  # The percentages
        y=tempo_counts.index,  # The tempo categories
        orientation='h',  # Horizontal bar chart
        text=[f"{perc:.1f}%" for perc in tempo_counts.values],  # Display percentages as text inside the bars
        textposition='auto',  # Position the text inside the bars automatically
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']),  # Custom colors
        hoverinfo='skip'
    ))

    # Update layout for the bar chart
    fig_tempo.update_layout(
        title_text='Percentage of Songs by Tempo Category',
        xaxis_title='Percentage of Songs (%)',
        yaxis_title='Tempo Category',
        xaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom x-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig_tempo)




    # Create a DataFrame with all the extracted features
    audio_features_for_spider = pd.DataFrame({
        'name': track_names,
        'danceability': track_danceability,
        'energy': track_energy,
        'loudness': track_loudness,
        'acousticness': track_acousticness,
        'instrumentalness': track_instrumentalness,
        'liveness': track_liveness,
        'happiness': track_valence,
        'tempo': track_tempo,
        'speechiness': track_speechiness,
        'key': track_key
    })

    # Convert the list of audio features into a DataFrame
    df_audio_features_for_spider = pd.DataFrame(audio_features_for_spider)

    # Apply MinMaxScaler to scale the features between 0 and 1
    scaler = MinMaxScaler()
    audio_features_without_name = df_audio_features_for_spider.drop(columns=['name'])
    audio_features_scaled = pd.DataFrame(scaler.fit_transform(audio_features_without_name), columns=audio_features_without_name.columns)

    # Calculate the average values of each feature
    average_audio_features = audio_features_scaled.mean()

    # Define the features to plot
    features = ['danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'liveness', 'happiness', 'tempo', 'speechiness', 'key']

    # Create the radar chart using Plotly
    # fig_audio_features = go.Figure()

    # Add the average values to the radar chart
    fig_audio_features = go.Figure(data=go.Scatterpolar(
        r=average_audio_features.values,  # Average values of the audio features
        theta=features,  # The audio features
        fill='toself',  # Fill the area inside the chart
        name='Average Audio Features'
    ))

    # Update the layout of the chart
    fig_audio_features.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]  # All values are between 0 and 1 due to MinMax scaling
            )
        ),
        title="Average Audio Features of Songs in the Playlist",
        showlegend=False
    )

    # Display the radar chart
    st.plotly_chart(fig_audio_features)


    # Merge the scaled data with track names
    df_audio_features_scaled = pd.concat([df_audio_features_for_spider[['name']], audio_features_scaled], axis=1)
    
    st.write("## Compare the audio features of 2 songs")

    # Create two dropdowns to select tracks
    track1 = st.selectbox("Select Song 1", df_audio_features_scaled['name'].unique())
    track2 = st.selectbox("Select Song 2", df_audio_features_scaled['name'].unique())

    # Filter the data for the selected tracks
    track1_data = df_audio_features_scaled[df_audio_features_scaled['name'] == track1]
    track2_data = df_audio_features_scaled[df_audio_features_scaled['name'] == track2]

    # Prepare data for radar chart
    track1_values = track1_data[features].values.flatten()
    track2_values = track2_data[features].values.flatten()

    # Create the radar chart using regular Plotly
    fig_compare_two = go.Figure()

    # Add trace for Track 1
    fig_compare_two.add_trace(go.Scatterpolar(
        r=track1_values,
        theta=features,
        fill='toself',
        name=track1,
        line=dict(color='blue')  # Set contrasting color for Track 1
    ))

    # Add trace for Track 2
    fig_compare_two.add_trace(go.Scatterpolar(
        r=track2_values,
        theta=features,
        fill='toself',
        name=track2,
        line=dict(color='orange')  # Set contrasting color for Track 1
    ))

    # Update the layout of the radar chart
    fig_compare_two.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]  # Audio features are scaled between 0 and 1
            )
        ),
        title="Comparison of Audio Features Between Two Tracks"
    )

    # Display the radar chart in Streamlit
    st.plotly_chart(fig_compare_two)


    st.write("## Heatmap of Audio Features for Songs in Playlist")

    # Calculate the number of tracks and features
    num_tracks = len(df_audio_features_scaled)
    num_features = len(df_audio_features_scaled.columns) - 1  # Exclude the 'name' column

    # Set the desired cell height and calculate the total width and height
    cell_height = 40  # Height of each cell in pixels
    cell_width = cell_height * 3  # Width of each cell is double the height

    # Calculate the total dimensions of the heatmap
    heatmap_width = cell_width * num_features
    heatmap_height = cell_height * num_tracks

    # Create a heatmap using Plotly
    fig_heatmap = px.imshow(
        df_audio_features_scaled.drop(columns=['name']),  # Keep the original data structure
        labels=dict(x="Audio Features", y="Tracks", color="Scaled Value"),
        x=df_audio_features_scaled.columns[1:],  # Audio feature names on x-axis
        y=df_audio_features_scaled['name'],  # Track names on y-axis
        color_continuous_scale='Turbo',  # Blue to red color scale
    )

    # Update the layout for better readability and increase the size of the heatmap
    fig_heatmap.update_layout(
        # title="Heatmap of Audio Features for Songs in Playlist",
        xaxis_title="Audio Features",
        yaxis_title="Songs",
        width=heatmap_width,  # Set the width based on the calculated value
        height=heatmap_height,  # Set the height based on the calculated value
        coloraxis_colorbar=dict(
            title_side='top',  # Position the title on the right side of the color bar
            title=dict(text="Scaled Value", font=dict(size=12)),  # Set title size
            title_font_size=12,  # Title font size
            tickfont=dict(size=10),  # Tick font size
            yanchor="bottom",  # Anchor the title lower
            y=0.12,  # Adjust the position of the color bar title to be lower
            yref="paper",
        )
    )

    # Display the heatmap in Streamlit
    st.plotly_chart(fig_heatmap, use_container_width=True)



    histogram_numeric_columns = ["Popularity", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]

    # Dropdown menu for selecting which column to display in the histogram
    selected_column = st.selectbox("Choose a feature to display in the histogram", histogram_numeric_columns)

    # Plotly's qualitative color scale
    color_scale = qualitative.Prism

    # Create the histogram using Plotly's go.Figure with nbinsx=20
    fig_histogram = go.Figure()

    # Add the histogram trace with Prism colors and nbinsx=20
    fig_histogram.add_trace(go.Histogram(
        x=df[selected_column],  # The selected data
        nbinsx=20,  # Set the number of bins to 20
        marker=dict(color=color_scale * (len(df[selected_column]) // len(color_scale) + 1)),  # Repeat colors for the bars
        name=f"{selected_column} Distribution"
    ))

    # Update the layout for better visuals
    fig_histogram.update_layout(
        title=f"{selected_column} Distribution",
        xaxis_title=selected_column,
        yaxis_title="Count",
        bargap=0.1  # Adjust gap between bars for a better appearance
    )

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_histogram)



    analysis_numeric_columns = ["Name", "Artist", "Release Date", "Genre", "Popularity", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]

    # Bivariate Analysis
    st.write("### Bivariate Analysis")
    x_axis = st.selectbox("Select a variable for the x-axis:", analysis_numeric_columns)
    y_axis = st.selectbox("Select a variable for the y-axis:", analysis_numeric_columns)

    fig_bivariate = px.scatter(df, x=x_axis, y=y_axis, title=f"{x_axis} vs. {y_axis}")
    fig_bivariate.update_layout(height=700)
    st.plotly_chart(fig_bivariate)

    # Multivariate Analysis
    st.write("### Multivariate Analysis")
 
    # Convert duration formatted as "minutes:seconds" to total seconds (replace with actual conversion)
    def convert_duration(duration_str):
        # Example conversion of "mm:ss" to seconds
        minutes, seconds = map(int, duration_str.split(':'))
        return minutes * 60 + seconds
    
    # Append "Duration (s)" column to the existing DataFrame `df`
    df['Duration (s)'] = df['Duration'].apply(convert_duration) 

    # Define the numeric columns including the new "Duration (s)" for further analysis
    numeric_columns = ["Popularity", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo", "Duration (s)"]

    # Define all analysis columns including "Duration" and "Duration (s)" for color
    analysis_columns = ["Name", "Artist", "Release Date", "Genre"] + numeric_columns

    # Select variables for the x-axis, y-axis, color, and size
    x_axis = st.selectbox("Select a variable for the x-axis:", numeric_columns)
    y_axis = st.selectbox("Select a variable for the y-axis:", numeric_columns)
    color_by = st.selectbox("Select a variable to color by:", analysis_columns)
    size_by = st.selectbox("Select a variable to size by:", numeric_columns)

    # Create the multivariate scatter plot with dynamic x and y
    fig_multivariate = px.scatter(df, x=x_axis, y=y_axis, color=color_by, size=size_by, hover_name="Name", 
                                title=f"{x_axis} vs. {y_axis} Colored by {color_by} and Sized by {size_by}")

    # Make the chart wider using the update_layout() method
    fig_multivariate.update_layout(width=1000, height=700)  # Adjust the width and height

    # Display the chart in Streamlit
    st.plotly_chart(fig_multivariate)

    



# import streamlit as st

# hide_streamlit_style = """
#                 <style>
#                 div[data-testid="stToolbar"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
#                 div[data-testid="stDecoration"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
#                 div[data-testid="stStatusWidget"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
#                 #MainMenu {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 header {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 footer {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 </style>
#                 """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# with open( "style.css" ) as css:
#     st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


# import spotipy
# from PIL import Image
# from spotipy.oauth2 import SpotifyClientCredentials

# client_id = '922604ee2b934fbd9d1223f4ec023fba'
# client_secret = '1bdf88cb16d64e54ba30220a8f126997'

# client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from sklearn.preprocessing import MinMaxScaler
# from datetime import datetime
# from plotly.colors import qualitative


# image = Image.open('data_adventures_logo.png')
# st.sidebar.image(image)
# st.title("Data Adventures in Music")
# st.write('Let’s dive into a Data Adventure with your playlist!')

# # Add radio button for choosing between entering playlist name or URL
# input_choice = st.sidebar.radio("How would you like to enter the playlist?", ("by name", "by URL"))

# # Initialize playlist_id as None
# playlist_id = None

# # Conditional input based on the user's choice
# if input_choice == "by name":
#     playlist_name = st.sidebar.text_input("Enter the public Spotify playlist name:")

#     # Search for the playlist ID based on the name
#     if playlist_name:
#         try:
#             playlists = sp.search(playlist_name, type="playlist")["playlists"]["items"]
#             if playlists:
#                 playlist_id = playlists[0]["id"]
#             else:
#                 st.write("No playlists found with that name.")
#         except Exception as e:
#             st.write("Error occurred while searching for the playlist.")
#             st.write(f"Error: {e}")
# else:
#     playlist_url = st.sidebar.text_input("Enter the Spotify playlist URL:")

#     # Extract the playlist ID from the URL
#     if playlist_url:
#         try:
#             playlist_id = playlist_url.split("/")[-1].split("?")[0]  # Handles URLs with or without query params
#         except Exception as e:
#             st.write("Error occurred while extracting the playlist ID.")
#             st.write(f"Error: {e}")

# # retrieve data from the Spotify API
# if playlist_id:
#     playlist = sp.playlist(playlist_id)
#     playlist_cover = playlist["images"][0]["url"]
#     tracks = playlist["tracks"]["items"]
#     track_id = [track["track"]["id"] for track in tracks]
#     track_names = [track["track"]["name"] for track in tracks]
#     track_artists = [", ".join([artist["name"] for artist in track["track"]["artists"]]) for track in tracks]
#     track_popularity = [track["track"]["popularity"] for track in tracks]
#     track_duration = [track["track"]["duration_ms"] for track in tracks]
#     track_album = [track["track"]["album"]["name"] for track in tracks]
#     track_preview = [track["track"]["preview_url"] for track in tracks]
#     track_image = [track["track"]["album"]["images"][0]["url"] for track in tracks]
#     track_release_date = [track["track"]["album"]["release_date"] for track in tracks]
#     track_url = [track["track"]["external_urls"]["spotify"] for track in tracks]
#     audio_features = sp.audio_features(track_url)
#     track_danceability = [track["danceability"] for track in audio_features]
#     track_energy = [track["energy"] for track in audio_features]
#     track_loudness = [track["loudness"] for track in audio_features]
#     track_acousticness = [track["acousticness"] for track in audio_features]
#     track_instrumentalness = [track["instrumentalness"] for track in audio_features]
#     track_liveness = [track["liveness"] for track in audio_features]
#     track_valence = [track["valence"] for track in audio_features]
#     track_tempo = [round(track["tempo"]) for track in audio_features]
#     track_signature = [track["time_signature"] for track in audio_features]
#     track_speechiness = [track["speechiness"] for track in audio_features]
#     track_key = [track["key"] for track in audio_features]

#     # Extract genres by fetching artist details
#     track_genres = []
#     for track in tracks:
#         artist_id = track["track"]["artists"][0]["id"]  # Get the first artist for simplicity
#         artist = sp.artist(artist_id)  # Fetch artist information
#         genres = artist.get("genres", [])  # Extract genres from artist
#         first_genre = genres[0] if genres else "No genre available"  # Get the first genre, or a default if no genres exist
#         track_genres.append(first_genre)


#     # Function to convert duration from milliseconds to minutes:seconds
#     def ms_to_minutes_seconds(ms):
#         minutes = ms // 60000  # Get minutes
#         seconds = (ms % 60000) // 1000  # Get remaining seconds
#         return f"{minutes}:{seconds:02d}"  # Format as mm:ss with zero-padded seconds

#     # Apply the conversion to the track durations
#     track_duration_formatted = [ms_to_minutes_seconds(duration) for duration in track_duration]
    


#     # Convert track keys to pitch class notation
#     # Map numeric key values to pitch class notation
#     key_mapping = {
#         -1: 'None',
#         0: 'C',
#         1: 'C# / Db',
#         2: 'D',
#         3: 'D# / Eb',
#         4: 'E',
#         5: 'F',
#         6: 'F# / Gb',
#         7: 'G',
#         8: 'G# / Ab',
#         9: 'A',
#         10: 'A# / Bb',
#         11: 'B'
#     }

#     # Convert track keys to pitch class notation
#     track_keys_converted = [key_mapping[key] for key in track_key]


#     # display the playlist data in a table
#     st.write(f"## {playlist['name']}")
#     st.image(playlist_cover, width=300)
#     if playlist.get('description'):
#         st.write(f"**Description:** {playlist['description']}")
#     st.write(f"**Number of tracks:** {len(tracks)}")
#     # st.write("")
#     # st.write("### Tracklist")
#     # st.write("| Name | Artist | Release Date | :blue[Popularity] | :green[Danceability] | :orange[Energy] | :red[Happiness] | :violet[Speechiness] | :gray[Tempo] |")
#     # for i in range(len(tracks)):
#     #     st.write(f"| {track_names[i]} | {track_artists[i]} | {track_release_date[i]} | :blue[{track_popularity[i]}] | :green[{track_danceability[i]}] | :orange[{track_energy[i]}] | :red[{track_valence[i]}] | :violet[{track_speechiness[i]}] | :gray[{track_tempo[i]}] |")

# # data = {"Image": track_image, "Name": track_names, "Preview": track_preview, "Artist": track_artists, "Release Date": track_release_date, "Popularity": track_popularity, "Duration (ms)": track_duration, "Acoustic": track_acousticness, "Dance": track_danceability, "Energy": track_energy, "Happy": track_valence, "Instrumental": track_instrumentalness, "Key": track_key, "Live": track_liveness, "Loud (Db)": track_loudness, "Speech": track_speechiness, "Tempo": track_tempo}
# if playlist_id:
#     data = {"Image": track_image, "Name": track_names, "Artist": track_artists, "Genre": track_genres, "Release Date": track_release_date, "Popularity": track_popularity, "Duration": track_duration_formatted, "Acoustic": track_acousticness, "Dance": track_danceability, "Energy": track_energy, "Happy": track_valence, "Instrumental": track_instrumentalness, "Key": track_keys_converted, "Live": track_liveness, "Loud (Db)": track_loudness, "Speech": track_speechiness, "Tempo": track_tempo}
#     df = pd.DataFrame(data)
#     num_total_tracks = len(df)
#     df.index += 1
#     st.write("The table below is scrollable both horizontally and vertically. Each column can be clicked to sort in ascending or descending order. Hovering over a column header will explain what that feature represents.")
#     st.data_editor(
#         df,
#         column_config={
#             "Image": st.column_config.ImageColumn(
#             "Album Art", help="Click on the album cover to enlarge"
#             ),
#             "Name": st.column_config.TextColumn(
#                 "Track Name", help="The name of the track"
#             ),
#             "Artist": st.column_config.TextColumn(
#                 "Artist", help="The primary artist or band who performed the track"
#             ),
#             "Genre": st.column_config.TextColumn(
#                 "Genre", help="Genres are based on the primary artist, as Spotify doesn't provide genre information at the album or track level."
#             ),
#             "Release Date": st.column_config.TextColumn(
#                 "Release Date", help="The date when the track or album was released"
#             ),
#             "Popularity": st.column_config.NumberColumn(
#                 "Popularity", help="The popularity score of the track (0 to 100)"
#             ),
#             "Duration": st.column_config.TextColumn(
#                 "Duration", help="The duration of the track"
#             ),
#             "Acoustic": st.column_config.NumberColumn(
#                 "Acousticness", help="A measure of the acoustic quality of the track (0 to 1)"
#             ),
#             "Dance": st.column_config.NumberColumn(
#                 "Danceability", help="How suitable the track is for dancing (0 to 1)"
#             ),
#             "Energy": st.column_config.NumberColumn(
#                 "Energy", help="The intensity and activity level of the track (0 to 1)"
#             ),
#             "Happy": st.column_config.NumberColumn(
#                 "Valence", help="A measure of the musical positivity of the track (0 to 1)"
#             ),
#             "Instrumental": st.column_config.NumberColumn(
#                 "Instrumental", help="The likelihood that the track is instrumental (0 to 1)"
#             ),
#             "Key": st.column_config.TextColumn(
#                 "Key", help="The musical key the track is composed in (0 to 11)"
#             ),
#             "Live": st.column_config.NumberColumn(
#                 "Liveness", help="The probability that the track was performed live (0 to 1)"
#             ),
#             "Loud (Db)": st.column_config.NumberColumn(
#                 "Loudness", help="The average loudness of a track in decibels (dB), useful for comparing the relative loudness of tracks"
#             ),
#             "Speech": st.column_config.NumberColumn(
#                 "Speechiness", help="The presence of spoken words in the track (0 to 1)"
#             ),
#             "Tempo": st.column_config.NumberColumn(
#                 "Tempo", help="The tempo of the track in beats per minute (BPM)"
#             )
#         },
#         disabled=True,
#     )
#     data2 = {"Name": track_names, "ID": track_id}
#     df2 = pd.DataFrame(data2)
#     selected_audio = st.selectbox("Select a song from the playlist to play its preview:", df2["Name"])
#     if selected_audio:
#         selected_url = df2[df2["Name"] == selected_audio]["ID"].values[0]
#         embed_url = f"https://open.spotify.com/embed/track/{selected_url}"
#         st.markdown(f'<iframe src="{embed_url}" width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
#     st.markdown("<br>", unsafe_allow_html=True)

#      # Features to choose from in the dropdown
#     features = ["Popularity", "Duration", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]
#     features_with_descriptions = [
#     "Popularity: The popularity score of the track (0 to 100)",
#     "Duration: The duration of the track",
#     "Acoustic: A measure of the acoustic quality of the track (0 to 1)",
#     "Dance: How suitable the track is for dancing (0 to 1)",
#     "Energy: The intensity and activity level of the track (0 to 1)",
#     "Happy: A measure of the musical positivity of the track (0 to 1)",
#     "Instrumental: The likelihood that the track is instrumental (0 to 1)",
#     "Key: The musical key the track is composed in (0 to 11)",
#     "Live: The probability that the track was performed live (0 to 1)",
#     "Loud (Db): The overall loudness of the track in decibels",
#     "Speech: The presence of spoken words in the track (0 to 1)",
#     "Tempo: The tempo of the track in beats per minute (BPM)"
#     ]
#     selected_feature_with_description = st.selectbox("Select an audio feature to rank tracks by:", features_with_descriptions)
#     # Extract the feature name from the selected option (before the colon)
#     selected_feature = selected_feature_with_description.split(":")[0]
#     num_tracks = st.slider(f"How many tracks do you want to display?", min_value=1, max_value=num_total_tracks, value=3)
#     sorted_df = df.sort_values(by=selected_feature, ascending=False)
#     st.write(f"### Top {num_tracks} Tracks by {selected_feature}")
#     st.dataframe(sorted_df.head(num_tracks)[["Name", "Artist", selected_feature]], hide_index=True)
#     sorted_df_ascending = df.sort_values(by=selected_feature, ascending=True)
#     st.write(f"### Lowest {num_tracks} Tracks by {selected_feature}")
#     st.dataframe(sorted_df_ascending.head(num_tracks)[["Name", "Artist", selected_feature]], hide_index=True) 

#     # Playlist track_genres data 
#     # Convert track_genres to a DataFrame for easier analysis
#     df_genres = pd.DataFrame(track_genres, columns=["Genre"])

#     # Count occurrences of each genre
#     genre_counts = df_genres["Genre"].value_counts()

#     # Calculate the percentage for each genre
#     genre_percentages = (genre_counts / genre_counts.sum()) * 100
#     # Sort genres by their percentage in descending order
#     genre_percentages_sorted = genre_percentages.sort_values(ascending=False)

#     # Calculate the cumulative sum and filter to only include genres up to 80%
#     cumulative_percentages = genre_percentages_sorted.cumsum()
#     top_genres_80 = genre_percentages_sorted[cumulative_percentages <= 80]

#     st.write(f"### Main Genres of Songs")
#     # Create a horizontal bar chart using Plotly to display top genres contributing to 80%
#     fig = px.bar(
#         top_genres_80,
#         x=top_genres_80.values,
#         y=top_genres_80.index,
#         orientation='h',  # Horizontal bar chart
#         labels={'x': 'Percentage of Songs (%)', 'y': 'Genres'},
#         # title='Main Genres of Songs',
#     )
#     # Customize hovertemplate to show only the percentage
#     fig.update_traces(hovertemplate='%{x:.2f}%<extra></extra>')
#     # Customize the bar chart's appearance
#     fig.update_layout(
#         xaxis_title="Percentage of Songs (%)",
#         yaxis_title="Genres",
#         xaxis=dict(range=[0, 100]),  # Set x-axis range from 0 to 100
#         margin=dict(t=0)  # Remove the space at the top of the chart
#         # title_x=0  # Center the title
#     )

#     # Display the bar chart in Streamlit
#     st.plotly_chart(fig, theme="streamlit")

#     # Calculate the average popularity
#     if track_popularity:
#         average_popularity = sum(track_popularity) / len(track_popularity)
#     else:
#         average_popularity = 0

#     # Display the average popularity
#     st.write(f"The average popularity of the songs in this playlist is: {int(average_popularity)} / 100")
#     # Show horizontal progress bar for average popularity (scaled between 0 and 100)
#     st.progress(int(average_popularity))
#     # Create a DataFrame to hold track names and popularity
#     df_popularity = pd.DataFrame({
#         'Track': track_names,
#         'Popularity': track_popularity
#     })
#     # Define the bins for popularity (0-10%, 10-20%, etc.)
#     bins = [i for i in range(0, 101, 10)]  # Create bins for every 10%
#     # Assign each track to a bin
#     df_popularity['Popularity Bin'] = pd.cut(df_popularity['Popularity'], bins=bins, right=False)
#     # Calculate the percentage of songs in each popularity bin
#     bin_counts = df_popularity['Popularity Bin'].value_counts(normalize=True) * 100
#     # Sort the bins so they appear in order
#     bin_counts = bin_counts.sort_index()
#     # Create a DataFrame for the bar chart
#     df_bins_popularity = pd.DataFrame({
#         'Popularity Range': [f"{int(interval.left)}-{int(interval.right)}" for interval in bin_counts.index],
#         'Percentage of Songs (%)': bin_counts.values
#     })
#     # Set the Popularity Range as the index for the chart
#     df_bins_popularity.set_index('Popularity Range', inplace=True)
#     # Display the bar chart of popularity ranges using st.bar_chart
#     st.bar_chart(df_bins_popularity, x_label="Popularity Score", y_label="Percentage of songs")


#     # Function to convert duration from milliseconds to minutes
#     def ms_to_minutes(ms):
#         return ms // 60000  # Convert milliseconds to minutes

#     # Apply the conversion to the track durations
#     track_durations_minutes = [ms_to_minutes(duration) for duration in track_duration]

#     # Create bins for the durations (0-1 mins, 1-2 mins, etc.)
#     bins = pd.cut(track_durations_minutes, bins=range(0, max(track_durations_minutes)+2), right=False)

#     # Count the occurrences in each bin
#     duration_counts = pd.value_counts(bins).sort_index()

#     # Calculate the percentage of each bin
#     total_tracks = len(track_durations_minutes)
#     duration_percentages = (duration_counts / total_tracks) * 100  # Calculate percentage

#     # Convert the bin intervals to strings for labeling
#     duration_labels = [f"{int(interval.left)}-{int(interval.right)} mins" for interval in duration_counts.index]

#     # Create a DataFrame for the donut chart
#     df_durations = pd.DataFrame({
#         'Duration Range': duration_labels,
#         'Percentage': duration_percentages.round(1)  # Round to 1 decimal place
#     })

#     # Create the donut chart using Plotly
#     fig_duration = px.pie(df_durations, values='Percentage', names='Duration Range', title='Track Durations by Minutes (Percentage)',
#                 hole=0.4)  # hole=0.4 makes it a donut chart

#     # Display the donut chart in Streamlit
#     st.plotly_chart(fig_duration)


#     # Calculate the average acousticness
#     if track_acousticness:
#         average_acousticness = sum(track_acousticness) / len(track_acousticness)
#     else:
#         average_acousticness = 0

#     # Display the average acousticness (0-1 scale)
#     st.write(f"The average acousticness of the songs in this playlist is: {average_acousticness:.2f} / 1")

#     # Show horizontal progress bar for average acousticness (scaled between 0 and 1)
#     st.progress(int(average_acousticness * 100))  # Multiply by 100 for progress bar

#     # Create a DataFrame to hold track names and acousticness
#     df_acousticness = pd.DataFrame({
#         'Track': track_names,
#         'Acousticness': track_acousticness  # Keep acousticness in 0-1 range
#     })

#     # Define the bins for acousticness (0-0.1, 0.1-0.2, etc.)
#     bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

#     # Assign each track to a bin
#     df_acousticness['Acousticness Bin'] = pd.cut(df_acousticness['Acousticness'], bins=bins, right=False)

#     # Calculate the percentage of songs in each acousticness bin
#     bin_counts = df_acousticness['Acousticness Bin'].value_counts(normalize=True) * 100

#     # Sort the bins so they appear in order
#     bin_counts = bin_counts.sort_index()

#     # Create a DataFrame for the bar chart
#     df_bins_acousticness = pd.DataFrame({
#         'Acousticness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
#         'Percentage of Songs (%)': bin_counts.values
#     })

#     # Set the Acousticness Range as the index for the chart
#     df_bins_acousticness.set_index('Acousticness Range', inplace=True)

#     # Display the bar chart of acousticness ranges using st.bar_chart
#     st.bar_chart(df_bins_acousticness, x_label="Acousticness Score", y_label="Percentage of songs")



# # Calculate the average danceability
#     if track_danceability:
#         average_danceability = sum(track_danceability) / len(track_danceability)
#     else:
#         average_danceability = 0

#     # Display the average danceability (0-1 scale)
#     st.write(f"The average danceability of the songs in this playlist is: {average_danceability:.2f} / 1")

#     # Show horizontal progress bar for average danceability (scaled between 0 and 1)
#     st.progress(int(average_danceability * 100))  # Multiply by 100 for progress bar

#     # Create a DataFrame to hold track names and danceability
#     df_danceability = pd.DataFrame({
#         'Track': track_names,
#         'Danceability': track_danceability  # Keep danceability in 0-1 range
#     })

#     # Define the bins for danceability (0-0.1, 0.1-0.2, etc.)
#     bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

#     # Assign each track to a bin
#     df_danceability['Danceability Bin'] = pd.cut(df_danceability['Danceability'], bins=bins, right=False)

#     # Calculate the percentage of songs in each danceability bin
#     bin_counts = df_danceability['Danceability Bin'].value_counts(normalize=True) * 100

#     # Sort the bins so they appear in order
#     bin_counts = bin_counts.sort_index()

#     # Create a DataFrame for the bar chart
#     df_bins_danceability = pd.DataFrame({
#         'Danceability Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
#         'Percentage of Songs (%)': bin_counts.values
#     })

#     # Set the Danceability Range as the index for the chart
#     df_bins_danceability.set_index('Danceability Range', inplace=True)

#     # Display the bar chart of danceability ranges using st.bar_chart
#     st.bar_chart(df_bins_danceability, x_label="Danceability Score", y_label="Percentage of songs")


# # Calculate the average energy
#     if track_energy:
#         average_energy = sum(track_energy) / len(track_energy)
#     else:
#         average_energy = 0

#     # Display the average energy (0-1 scale)
#     st.write(f"The average energy of the songs in this playlist is: {average_energy:.2f} / 1")

#     # Show horizontal progress bar for average energy (scaled between 0 and 1)
#     st.progress(int(average_energy * 100))  # Multiply by 100 for progress bar

#     # Create a DataFrame to hold track names and energy
#     df_energy = pd.DataFrame({
#         'Track': track_names,
#         'Energy': track_energy  # Keep energy in 0-1 range
#     })

#     # Define the bins for energy (0-0.1, 0.1-0.2, etc.)
#     bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

#     # Assign each track to a bin
#     df_energy['Energy Bin'] = pd.cut(df_energy['Energy'], bins=bins, right=False)

#     # Calculate the percentage of songs in each energy bin
#     bin_counts = df_energy['Energy Bin'].value_counts(normalize=True) * 100

#     # Sort the bins so they appear in order
#     bin_counts = bin_counts.sort_index()

#     # Create a DataFrame for the bar chart
#     df_bins_energy = pd.DataFrame({
#         'Energy Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
#         'Percentage of Songs (%)': bin_counts.values
#     })

#     # Set the Energy Range as the index for the chart
#     df_bins_energy.set_index('Energy Range', inplace=True)

#     # Display the bar chart of energy ranges using st.bar_chart
#     st.bar_chart(df_bins_energy, x_label="Energy Score", y_label="Percentage of Songs (%)")



#    # Calculate the average happiness (valence)
#     if track_valence:
#         average_happiness = sum(track_valence) / len(track_valence)
#     else:
#         average_happiness = 0

#     # Display the average happiness (valence) (0-1 scale)
#     st.write(f"The average happiness of the songs in this playlist is: {average_happiness:.2f} / 1")

#     # Show horizontal progress bar for average happiness (scaled between 0 and 1)
#     st.progress(int(average_happiness * 100))  # Multiply by 100 for progress bar

#     # Create a DataFrame to hold track names and happiness (valence)
#     df_happiness = pd.DataFrame({
#         'Track': track_names,
#         'Happiness': track_valence  # Keep valence (happiness) in 0-1 range
#     })

#     # Define the bins for happiness (0-0.1, 0.1-0.2, etc.)
#     bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

#     # Assign each track to a bin
#     df_happiness['Happiness Bin'] = pd.cut(df_happiness['Happiness'], bins=bins, right=False)

#     # Calculate the percentage of songs in each happiness bin
#     bin_counts = df_happiness['Happiness Bin'].value_counts(normalize=True) * 100

#     # Sort the bins so they appear in order
#     bin_counts = bin_counts.sort_index()

#     # Create a DataFrame for the bar chart
#     df_bins_happiness = pd.DataFrame({
#         'Happiness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
#         'Percentage of Songs (%)': bin_counts.values
#     })

#     # Set the Happiness Range as the index for the chart
#     df_bins_happiness.set_index('Happiness Range', inplace=True)

#     # Display the bar chart of happiness ranges using st.bar_chart
#     st.bar_chart(df_bins_happiness, x_label="Happiness Score", y_label="Percentage of Songs (%)")




#  # Calculate the average instrumentalness
#     if track_instrumentalness:
#         average_instrumentalness = sum(track_instrumentalness) / len(track_instrumentalness)
#     else:
#         average_instrumentalness = 0

#     # Display the average instrumentalness (0-1 scale)
#     st.write(f"The average instrumentalness of the songs in this playlist is: {average_instrumentalness:.2f} / 1")

#     # Show horizontal progress bar for average instrumentalness (scaled between 0 and 1)
#     st.progress(int(average_instrumentalness * 100))  # Multiply by 100 for progress bar

#     # Create a DataFrame to hold track names and instrumentalness
#     df_instrumentalness = pd.DataFrame({
#         'Track': track_names,
#         'Instrumentalness': track_instrumentalness  # Keep instrumentalness in 0-1 range
#     })

#     # Define the bins for instrumentalness (0-0.1, 0.1-0.2, etc.)
#     bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

#     # Assign each track to a bin
#     df_instrumentalness['Instrumentalness Bin'] = pd.cut(df_instrumentalness['Instrumentalness'], bins=bins, right=False)

#     # Calculate the percentage of songs in each instrumentalness bin
#     bin_counts = df_instrumentalness['Instrumentalness Bin'].value_counts(normalize=True) * 100

#     # Sort the bins so they appear in order
#     bin_counts = bin_counts.sort_index()

#     # Create a DataFrame for the bar chart
#     df_bins_instrumentalness = pd.DataFrame({
#         'Instrumentalness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
#         'Percentage of Songs (%)': bin_counts.values
#     })

#     # Set the Instrumentalness Range as the index for the chart
#     df_bins_instrumentalness.set_index('Instrumentalness Range', inplace=True)

#     # Display the bar chart of instrumentalness ranges using st.bar_chart
#     st.bar_chart(df_bins_instrumentalness, x_label="Instrulmentalness Score", y_label="Percentage of Songs (%)")



# # Create a DataFrame to hold track keys and their occurrences
#     df_keys = pd.DataFrame(track_keys_converted, columns=['Key'])

#     # Count the occurrences of each key
#     key_counts = df_keys['Key'].value_counts(normalize=True) * 100  # Calculate percentage
#     key_counts = key_counts.round(1).reset_index()  # Round the percentage values to one decimal place
#     key_counts.columns = ['Key', 'Percentage']

#     # Create the pie chart using Plotly
#     fig_keys = px.pie(key_counts, values='Percentage', names='Key', title='Distribution of Musical Keys in Playlist (Percentage)')

#     # Display the pie chart in Streamlit
#     st.plotly_chart(fig_keys)



# # Calculate the average liveness
#     if track_liveness:
#         average_liveness = sum(track_liveness) / len(track_liveness)
#     else:
#         average_liveness = 0

#     # Display the average liveness (0-1 scale)
#     st.write(f"The average liveness of the songs in this playlist is: {average_liveness:.2f} / 1")

#     # Show horizontal progress bar for average liveness (scaled between 0 and 1)
#     st.progress(int(average_liveness * 100))  # Multiply by 100 for progress bar

#     # Create a DataFrame to hold track names and liveness
#     df_liveness = pd.DataFrame({
#         'Track': track_names,
#         'Liveness': track_liveness  # Keep liveness in 0-1 range
#     })

#     # Define the bins for liveness (0-0.1, 0.1-0.2, etc.)
#     bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

#     # Assign each track to a bin
#     df_liveness['Liveness Bin'] = pd.cut(df_liveness['Liveness'], bins=bins, right=False)

#     # Calculate the percentage of songs in each liveness bin
#     bin_counts = df_liveness['Liveness Bin'].value_counts(normalize=True) * 100

#     # Sort the bins so they appear in order
#     bin_counts = bin_counts.sort_index()

#     # Create a DataFrame for the bar chart
#     df_bins_liveness = pd.DataFrame({
#         'Liveness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
#         'Percentage of Songs (%)': bin_counts.values
#     })

#     # Set the Liveness Range as the index for the chart
#     df_bins_liveness.set_index('Liveness Range', inplace=True)

#     # Display the bar chart of liveness ranges using st.bar_chart
#     st.bar_chart(df_bins_liveness, x_label="Liveness Score", y_label="Percentage of Songs (%)")



# # Create bins for track loudness based on suggested ranges
#     bins_loudness = [-60, -40, -30, -20, -10, 0]  # Define the bin edges
#     labels_loudness = ['-60 to -40 dB', '-40 to -30 dB', '-30 to -20 dB', '-20 to -10 dB', '-10 to 0 dB']  # Labels for each bin

#     # Categorize the loudness values into bins
#     loudness_binned = pd.cut(track_loudness, bins=bins_loudness, labels=labels_loudness, right=False)

#     # Count the occurrences of each bin
#     loudness_binned_counts = loudness_binned.value_counts().sort_index()

#     # Calculate the percentage for each bin
#     total_tracks = len(track_loudness)
#     loudness_binned_percentages = (loudness_binned_counts / total_tracks) * 100

#     # Create a Plotly stacked horizontal bar chart using the calculated percentages
#     fig_loudness = go.Figure()

#     # Add the bar (each segment of the bar represents a loudness bin)
#     fig_loudness.add_trace(go.Bar(
#         x=loudness_binned_percentages.values,  # Use the calculated percentages
#         y=loudness_binned_percentages.index,  
#         orientation='h',
#         text=[f"{perc:.1f}%" for perc in loudness_binned_percentages.values],  # Add text labels showing the percentages
#         textposition='inside',  # Place the text labels inside the bar
#         marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']),  # Colors for the segments
#         hoverinfo='text',  # Show the text on hover
#         hovertext=[f"{label}: {perc:.1f}%" for label, perc in zip(labels_loudness, loudness_binned_percentages.values)]  # Hover info
#     ))

#     # Update the layout to include custom x-axis ticks and a title
#     fig_loudness.update_layout(
#         title_text='Distribution of Songs by Loudness Range',
#         xaxis_title='Percentage of Tracks (%)',
#         yaxis_title='',
#         xaxis=dict(
#             tickvals=[0, 20, 40, 60, 80, 100],  # Custom ticks at 0, 20, 40, 60, 80, 100
#             ticktext=['0%', '20%', '40%', '60%', '80%', '100%'],  # Display percentage symbols on the x-axis
#             range=[0, 100]  # Ensure the x-axis covers the full range from 0 to 100
#         ),
#         barmode='stack',
#         showlegend=False,  # Disable the legend as it is not needed,
#         annotations=[
#             dict(
#                 x=105,  # Positioning to the right of the chart
#                 y=0,  # Align with the y-axis
#                 xref="x",  # Refer to the x-axis
#                 yref="y",  # Refer to the y-axis
#                 text=(
#                     "-60 dB to -40 dB: Very quiet or background noise.<br>"
#                     "-40 dB to -30 dB: Soft, likely ambient or very quiet tracks.<br>"
#                     "-30 dB to -20 dB: Moderately soft tracks.<br>"
#                     "-20 dB to -10 dB: Typical dynamic range for commercial music.<br>"
#                     "-10 dB to 0 dB: Loud, compressed, heavily mastered tracks."
#                 ),
#                 showarrow=False,  # No arrow needed, just text
#                 align="left",
#                 font=dict(size=10)  # Adjust the font size for the helper text
#             )
#         ]
#     )

#     # Display the chart in Streamlit
#     st.plotly_chart(fig_loudness)


#    # Calculate the average speechiness
#     if track_speechiness:
#         average_speechiness = sum(track_speechiness) / len(track_speechiness)
#     else:
#         average_speechiness = 0

#     # Display the average speechiness (0-1 scale)
#     st.write(f"The average speechiness of the songs in this playlist is: {average_speechiness:.2f} / 1")

#     # Show horizontal progress bar for average speechiness (scaled between 0 and 1)
#     st.progress(int(average_speechiness * 100))  # Multiply by 100 for progress bar

#     # Create a DataFrame to hold track names and speechiness
#     df_speechiness = pd.DataFrame({
#         'Track': track_names,
#         'Speechiness': track_speechiness  # Keep speechiness in 0-1 range
#     })

#     # Define the bins for speechiness (0-0.1, 0.1-0.2, etc.)
#     bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

#     # Assign each track to a bin
#     df_speechiness['Speechiness Bin'] = pd.cut(df_speechiness['Speechiness'], bins=bins, right=False)

#     # Calculate the percentage of songs in each speechiness bin
#     bin_counts = df_speechiness['Speechiness Bin'].value_counts(normalize=True) * 100

#     # Sort the bins so they appear in order
#     bin_counts = bin_counts.sort_index()

#     # Create a DataFrame for the bar chart
#     df_bins_speechiness = pd.DataFrame({
#         'Speechiness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
#         'Percentage of Songs (%)': bin_counts.values
#     })

#     # Set the Speechiness Range as the index for the chart
#     df_bins_speechiness.set_index('Speechiness Range', inplace=True)

#     # Display the bar chart of speechiness ranges using st.bar_chart
#     st.bar_chart(df_bins_speechiness, x_label="Speechiness Score", y_label="Percentage of Songs (%)")


#     # Define tempo categories with their corresponding ranges
#     def categorize_tempo(tempo):
#         if tempo < 60:
#             return "Largo (Very Slow)"
#         elif 60 <= tempo < 76:
#             return "Adagio (Slow)"
#         elif 76 <= tempo < 108:
#             return "Andante (Moderate)"
#         elif 108 <= tempo < 120:
#             return "Moderato (Moderate/Fast)"
#         elif 120 <= tempo < 156:
#             return "Allegro (Fast)"
#         elif 156 <= tempo < 200:
#             return "Presto (Very Fast)"
#         else:
#             return "Prestissimo (Extremely Fast)"

#     # Apply the categorization to the track_tempo list
#     track_tempo_categories = [categorize_tempo(tempo) for tempo in track_tempo]

#     # Create a DataFrame to count the occurrences of each tempo category
#     df_tempo = pd.DataFrame({
#         'Tempo Category': track_tempo_categories
#     })

#     # Count the occurrences of each tempo category and calculate percentages
#     tempo_counts = df_tempo['Tempo Category'].value_counts(normalize=True) * 100
#     tempo_counts = tempo_counts.sort_index()  # Sort categories alphabetically or based on a custom order

#     # Create a Plotly horizontal bar chart
#     fig_tempo = go.Figure(go.Bar(
#         x=tempo_counts.values,  # The percentages
#         y=tempo_counts.index,  # The tempo categories
#         orientation='h',  # Horizontal bar chart
#         text=[f"{perc:.1f}%" for perc in tempo_counts.values],  # Display percentages as text inside the bars
#         textposition='auto',  # Position the text inside the bars automatically
#         marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']),  # Custom colors
#         hoverinfo='skip'
#     ))

#     # Update layout for the bar chart
#     fig_tempo.update_layout(
#         title_text='Percentage of Songs by Tempo Category',
#         xaxis_title='Percentage of Songs (%)',
#         yaxis_title='Tempo Category',
#         xaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom x-axis ticks for percentage
#         showlegend=False  # Disable the legend
#     )

#     # Display the chart in Streamlit
#     st.plotly_chart(fig_tempo)

# # Create a DataFrame with all the extracted features
#     audio_features_for_spider = pd.DataFrame({
#         'name': track_names,
#         'danceability': track_danceability,
#         'energy': track_energy,
#         'loudness': track_loudness,
#         'acousticness': track_acousticness,
#         'instrumentalness': track_instrumentalness,
#         'liveness': track_liveness,
#         'happiness': track_valence,
#         'tempo': track_tempo,
#         'speechiness': track_speechiness,
#         'key': track_key
#     })

#     # Convert the list of audio features into a DataFrame
#     df_audio_features_for_spider = pd.DataFrame(audio_features_for_spider)

#     # Apply MinMaxScaler to scale the features between 0 and 1
#     scaler = MinMaxScaler()
#     audio_features_without_name = df_audio_features_for_spider.drop(columns=['name'])
#     audio_features_scaled = pd.DataFrame(scaler.fit_transform(audio_features_without_name), columns=audio_features_without_name.columns)

#     # Calculate the average values of each feature
#     average_audio_features = audio_features_scaled.mean()

#     # Define the features to plot
#     features = ['danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'liveness', 'happiness', 'tempo', 'speechiness', 'key']

#     # Create the radar chart using Plotly
#     # fig_audio_features = go.Figure()

#     # Add the average values to the radar chart
#     fig_audio_features = go.Figure(data=go.Scatterpolar(
#         r=average_audio_features.values,  # Average values of the audio features
#         theta=features,  # The audio features
#         fill='toself',  # Fill the area inside the chart
#         name='Average Audio Features'
#     ))

#     # Update the layout of the chart
#     fig_audio_features.update_layout(
#         polar=dict(
#             radialaxis=dict(
#                 visible=True,
#                 range=[0, 1]  # All values are between 0 and 1 due to MinMax scaling
#             )
#         ),
#         title="Average Audio Features of Songs in the Playlist",
#         showlegend=False
#     )

#     # Display the radar chart
#     st.plotly_chart(fig_audio_features)


#     # Merge the scaled data with track names
#     df_audio_features_scaled = pd.concat([df_audio_features_for_spider[['name']], audio_features_scaled], axis=1)
    
#     st.write("## Compare the audio features of 2 songs")

#     # Create two dropdowns to select tracks
#     track1 = st.selectbox("Select Song 1", df_audio_features_scaled['name'].unique())
#     track2 = st.selectbox("Select Song 2", df_audio_features_scaled['name'].unique())

#     # Filter the data for the selected tracks
#     track1_data = df_audio_features_scaled[df_audio_features_scaled['name'] == track1]
#     track2_data = df_audio_features_scaled[df_audio_features_scaled['name'] == track2]

#     # Prepare data for radar chart
#     track1_values = track1_data[features].values.flatten()
#     track2_values = track2_data[features].values.flatten()

#     # Create the radar chart using regular Plotly
#     fig_compare_two = go.Figure()

#     # Add trace for Track 1
#     fig_compare_two.add_trace(go.Scatterpolar(
#         r=track1_values,
#         theta=features,
#         fill='toself',
#         name=track1,
#         line=dict(color='blue')  # Set contrasting color for Track 1
#     ))

#     # Add trace for Track 2
#     fig_compare_two.add_trace(go.Scatterpolar(
#         r=track2_values,
#         theta=features,
#         fill='toself',
#         name=track2,
#         line=dict(color='orange')  # Set contrasting color for Track 1
#     ))

#     # Update the layout of the radar chart
#     fig_compare_two.update_layout(
#         polar=dict(
#             radialaxis=dict(
#                 visible=True,
#                 range=[0, 1]  # Audio features are scaled between 0 and 1
#             )
#         ),
#         title="Comparison of Audio Features Between Two Tracks"
#     )

#     # Display the radar chart in Streamlit
#     st.plotly_chart(fig_compare_two)



#     st.write("## Heatmap of Audio Features for Songs in Playlist")

#     # Calculate the number of tracks and features
#     num_tracks = len(df_audio_features_scaled)
#     num_features = len(df_audio_features_scaled.columns) - 1  # Exclude the 'name' column

#     # Set the desired cell height and calculate the total width and height
#     cell_height = 40  # Height of each cell in pixels
#     cell_width = cell_height * 3  # Width of each cell is double the height

#     # Calculate the total dimensions of the heatmap
#     heatmap_width = cell_width * num_features
#     heatmap_height = cell_height * num_tracks

#     # Create a heatmap using Plotly
#     fig_heatmap = px.imshow(
#         df_audio_features_scaled.drop(columns=['name']),  # Keep the original data structure
#         labels=dict(x="Audio Features", y="Tracks", color="Scaled Value"),
#         x=df_audio_features_scaled.columns[1:],  # Audio feature names on x-axis
#         y=df_audio_features_scaled['name'],  # Track names on y-axis
#         color_continuous_scale='Turbo',  # Blue to red color scale
#     )

#     # Update the layout for better readability and increase the size of the heatmap
#     fig_heatmap.update_layout(
#         # title="Heatmap of Audio Features for Songs in Playlist",
#         xaxis_title="Audio Features",
#         yaxis_title="Songs",
#         width=heatmap_width,  # Set the width based on the calculated value
#         height=heatmap_height,  # Set the height based on the calculated value
#         coloraxis_colorbar=dict(
#             title_side='top',  # Position the title on the right side of the color bar
#             title=dict(text="Scaled Value", font=dict(size=12)),  # Set title size
#             title_font_size=12,  # Title font size
#             tickfont=dict(size=10),  # Tick font size
#             yanchor="bottom",  # Anchor the title lower
#             y=0.12,  # Adjust the position of the color bar title to be lower
#             yref="paper",
#         )
#     )

#     # Display the heatmap in Streamlit
#     st.plotly_chart(fig_heatmap, use_container_width=True)

#     histogram_numeric_columns = ["Popularity", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]

#     # Dropdown menu for selecting which column to display in the histogram
#     selected_column = st.selectbox("Choose a feature to display in the histogram", histogram_numeric_columns)

#     # Plotly's qualitative color scale
#     color_scale = qualitative.Prism

#     # Create the histogram using Plotly's go.Figure with nbinsx=20
#     fig_histogram = go.Figure()

#     # Add the histogram trace with Prism colors and nbinsx=20
#     fig_histogram.add_trace(go.Histogram(
#         x=df[selected_column],  # The selected data
#         nbinsx=20,  # Set the number of bins to 20
#         marker=dict(color=color_scale * (len(df[selected_column]) // len(color_scale) + 1)),  # Repeat colors for the bars
#         name=f"{selected_column} Distribution"
#     ))

#     # Update the layout for better visuals
#     fig_histogram.update_layout(
#         title=f"{selected_column} Distribution",
#         xaxis_title=selected_column,
#         yaxis_title="Count",
#         bargap=0.1  # Adjust gap between bars for a better appearance
#     )

#     # Display the Plotly chart in Streamlit
#     st.plotly_chart(fig_histogram)


    

#     # # Display the Plotly chart in Streamlit
#     # st.plotly_chart(fig_histogram)



#     # analysis_numeric_columns = ["Name", "Artist", "Release Date", "Genre", "Popularity", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]

#     # # Bivariate Analysis
#     # st.write("### Bivariate Analysis")
#     # x_axis = st.selectbox("Select a variable for the x-axis:", analysis_numeric_columns)
#     # y_axis = st.selectbox("Select a variable for the y-axis:", analysis_numeric_columns)

#     # fig_bivariate = px.scatter(df, x=x_axis, y=y_axis, title=f"{x_axis} vs. {y_axis}")
#     # fig_bivariate.update_layout(height=700)
#     # st.plotly_chart(fig_bivariate)

#     # # Multivariate Analysis
#     # st.write("### Multivariate Analysis")
 
#     # # Convert duration formatted as "minutes:seconds" to total seconds (replace with actual conversion)
#     # def convert_duration(duration_str):
#     #     # Example conversion of "mm:ss" to seconds
#     #     minutes, seconds = map(int, duration_str.split(':'))
#     #     return minutes * 60 + seconds
    
#     # # Append "Duration (s)" column to the existing DataFrame `df`
#     # df['Duration (s)'] = df['Duration'].apply(convert_duration) 

#     # # Define the numeric columns including the new "Duration (s)" for further analysis
#     # numeric_columns = ["Popularity", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo", "Duration (s)"]

#     # # Define all analysis columns including "Duration" and "Duration (s)" for color
#     # analysis_columns = ["Name", "Artist", "Release Date", "Genre"] + numeric_columns

#     # # Select variables for the x-axis, y-axis, color, and size
#     # x_axis = st.selectbox("Select a variable for the x-axis:", numeric_columns)
#     # y_axis = st.selectbox("Select a variable for the y-axis:", numeric_columns)
#     # color_by = st.selectbox("Select a variable to color by:", analysis_columns)
#     # size_by = st.selectbox("Select a variable to size by:", numeric_columns)

#     # # Create the multivariate scatter plot with dynamic x and y
#     # fig_multivariate = px.scatter(df, x=x_axis, y=y_axis, color=color_by, size=size_by, hover_name="Name", 
#     #                             title=f"{x_axis} vs. {y_axis} Colored by {color_by} and Sized by {size_by}")

#     # # Make the chart wider using the update_layout() method
#     # fig_multivariate.update_layout(width=1000, height=700)  # Adjust the width and height

#     # # Display the chart in Streamlit
#     # st.plotly_chart(fig_multivariate)


#     # # add a dropdown menu for bivariate analysis
#     # st.write("#### Bivariate Analysis")
#     # x_axis = st.selectbox("Select a variable for the x-axis:", ["Popularity", "Duration (ms)","Release Date"])
#     # y_axis = st.selectbox("Select a variable for the y-axis:", ["Popularity", "Duration (ms)", "Release Date"])
#     # fig_bivariate = px.scatter(df, x=x_axis, y=y_axis, title=f"{x_axis} vs. {y_axis}")
#     # st.plotly_chart(fig_bivariate)

#     # # add a dropdown menu for multivariate analysis
#     # st.write("#### Multivariate Analysis")
#     # color_by = st.selectbox("Select a variable to color by:", ["Artist", "Album", "Release Date"])
#     # size_by = st.selectbox("Select a variable to size by:", ["Popularity", "Duration (ms)"])
#     # fig_multivariate = px.scatter(df, x="Duration (ms)", y="Popularity", color=color_by, size=size_by, hover_name="Name", title="Duration vs. Popularity Colored by Artist")
#     # st.plotly_chart(fig_multivariate)
