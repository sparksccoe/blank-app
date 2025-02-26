import streamlit as st
import requests
import streamlit.components.v1 as components

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
import numpy as np
import soundfile as sf
import sounddevice as sd

image = Image.open('data_adventures_logo.png')
col1, col2, col3 = st.columns([1,6,1])

with col1:
    st.write("")

with col2:
    st.image(image, width=int(image.width * 0.4))

with col3:
    st.write("")

# st.markdown(
#     "<h1 style='text-align: center;'>Playtest Welcome</h1>",
#     unsafe_allow_html=True
# )

# st.write('Let’s go on a Data Adventure with our Bards!')
st.markdown(
    "<div style='text-align: center; font-size: 16px; font-weight: normal;'>"
    "Let’s go on a Data Adventure with our Bards!"
    "</div>", 
    unsafe_allow_html=True
)

st.header("🎚️ Metronome Master")
# 🎼 Show relatable response only after the user enters BPM

# 🎵 Ask for BPM input (default None)
bpm = st.number_input("Enter the BPM (Beats Per Minute) of your song:", 
                      min_value=40, max_value=250, value=None, step=1, format="%d")
if bpm is not None:
    if bpm < 60:
        st.write("This is a **super chill, slow-tempo song**—perfect for relaxation or deep focus.")
    elif bpm < 90:
        st.write("A **laid-back groove**, great for R&B, lo-fi beats, or smooth jazz.")
    elif bpm < 120:
        st.write("A **mid-tempo track**—probably a good dance groove or pop beat!")
    elif bpm < 150:
        st.write("A **fast-paced song**, great for working out or getting pumped up!")
    else:
        st.write("This is **ultra-fast**—likely a drum & bass, punk, or extreme techno beat!")

if bpm is not None:
    st.session_state.loudness = None # Reset loudness state

# 🥁 Function to generate a percussive sound (kick, snare, hi-hat)
def generate_drum_sound(sample_rate=44100, drum_type="kick"):
    duration = 0.15  # Length of drum sound
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    if drum_type == "kick":
        # Deep sine wave for kick drum
        envelope = np.exp(-t / 0.05)  # Short decay
        sound = 0.8 * envelope * np.sin(2 * np.pi * 60 * t)  # 60 Hz kick

    elif drum_type == "snare":
        # White noise for snare drum + low pass filter
        envelope = np.exp(-t / 0.04)  # Snappier decay
        noise = np.random.normal(0, 0.5, t.shape)
        sound = 0.5 * envelope * noise  # White noise snare

    elif drum_type == "hihat":
        # High-frequency noise for hi-hat
        envelope = np.exp(-t / 0.02)  # Very short decay
        noise = np.random.normal(0, 0.3, t.shape)
        sound = 0.3 * envelope * noise  # Crisp hi-hat

    return np.clip(sound, -1, 1)

# 🥁 Function to generate a drum beat loop
def generate_drum_beat(bpm, duration=5, sample_rate=44100):
    interval = 60 / bpm  # Seconds per beat
    num_beats = int(duration / interval)  # Total beats in duration
    audio = np.zeros(int(sample_rate * duration))  # Empty audio track

    # Generate individual drum sounds
    kick = generate_drum_sound(drum_type="kick")
    snare = generate_drum_sound(drum_type="snare")
    hihat = generate_drum_sound(drum_type="hihat")

    for i in range(num_beats):
        start = int(i * interval * sample_rate)
        end = start + len(kick)

        # Add kick on beats 1 & 3
        if i % 4 in [0, 2]:
            audio[start:end] += kick

        # Add snare on beats 2 & 4
        if i % 4 == 1 or i % 4 == 3:
            audio[start:end] += snare

        # Add hi-hat on every beat
        hh_start = int(i * interval * sample_rate)
        hh_end = hh_start + len(hihat)
        audio[hh_start:hh_end] += hihat

    return np.clip(audio, -1, 1)  # Prevent distortion

# 🎧 Button to play drum beat (only after BPM is entered)
if bpm is not None:
    if st.button("🥁 Play Your Tempo as a Drum Loop"):
        drum_beat = generate_drum_beat(bpm)
        sf.write("drum_beat.wav", drum_beat, 44100)
        st.audio("drum_beat.wav")


# 🔊 Section: Loudness Analysis
st.header("🔊 Volume Virtuoso")
# 🔊 Initialize session state for loudness if not already set
if "loudness" not in st.session_state:
    st.session_state.loudness = None  # Start as None (empty input)

# Ensure number input does not reset, but starts empty
loudness = st.number_input(
    "Enter the relative loudness of your song (in dB, typically between -60 and 0):",
    min_value=-60, max_value=0, value=st.session_state.loudness, step=1, format="-%d"
)

# Update session state when the user enters a value
if loudness is not None and loudness != st.session_state.loudness:
    st.session_state.loudness = loudness

# 🎼 Show relatable response only after the user enters loudness
if loudness is not None:
    if loudness < -40:
        st.write("This is **super quiet**, like the peaceful piano in *Clair de Lune* or the soft intro of *Lofi Girl* study beats.")
    elif loudness < -25:
        st.write("This is a **soft, gentle track**, like *Golden Hour* by JVKE or the calm melodies in *Somewhere Over the Rainbow* by Israel Kamakawiwo'ole.")
    elif loudness < -15:
        st.write("A **moderate loudness level**, like *Watermelon Sugar* by Harry Styles or *Sunroof* by Nicky Youre—smooth but with some energy!")
    elif loudness < -5:
        st.write("This is **fairly loud**, like *Uptown Funk* by Bruno Mars or *Industry Baby* by Lil Nas X—big, dynamic, and exciting!")
    else:
        st.write("**Max loudness!** This is like *Blinding Lights* by The Weeknd or *Sicko Mode* by Travis Scott—high-energy, booming, and club-ready!")



# Initialize playlist_id as None or hardcoded here
playlist_id = "3BGJRi9zQrIjLDtBbRYy5n"

# YouTube API key and playlist ID (replace with your own)
api_key = "AIzaSyAxHBK8MxzePcos86BOaBwUtTurr_ZbpNg"  # Replace with your API key
youtube_playlist_url = "https://www.youtube.com/playlist?list=PLtg7R4Q_LfGU-WLVp5jeOoD7tdUiS6FHg"
youtube_playlist_id = youtube_playlist_url.split("list=")[-1]

# 🔹 Ensure user playlist is initialized in session state
if "user_playlist" not in st.session_state:
    st.session_state.user_playlist = pd.DataFrame(columns=["Name", "Artist", "Image", "track_video_id", "Tempo", "Loud (Db)"])


# 🟢 Ensure both BPM & Loudness are entered before proceeding
if bpm is not None and loudness is not None:
    # 🟢 Retrieve data from Spotify API
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

        # Create a DataFrame for track decades
        df_decades = pd.DataFrame({'Release Date': track_release_date})
        df_decades['Year'] = pd.to_datetime(df_decades['Release Date']).dt.year
        df_decades['Decade'] = (df_decades['Year'] // 10) * 10
        track_decade = df_decades['Decade'].astype(str) + "s"

        # 🟢 Load additional song features from CSV
        df = pd.read_csv("Symphonia Bards-3.csv")

        track_danceability = df["Dance"].tolist()
        track_energy = df["Energy"].tolist()
        track_loudness = df["Loud (Db)"].tolist()
        track_acousticness = df["Acoustic"].tolist()
        track_instrumentalness = df["Instrumental"].tolist()
        track_liveness = df["Live"].tolist()
        track_valence = df["Happy"].tolist()
        track_tempo = df["BPM"].apply(round).tolist()
        track_signature = df["Time Signature"].tolist()
        track_speechiness = df["Speech"].tolist()
        track_keys_converted = df["Key"].tolist()

        # 🟢 Create a DataFrame with relevant data
        df_tracks = pd.DataFrame({
            "Name": track_names,
            "Artist": track_artists,
            "Tempo": track_tempo,
            "Loud (Db)": track_loudness,
            "Image": track_image,
            "Spotify URL": track_url
        })

        # Function to fetch playlist details using the YouTube API
        def fetch_playlist_videos(api_key, youtube_playlist_id):
            base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
            params = {
                "part": "snippet",
                "playlistId": youtube_playlist_id,
                "maxResults": 50,  # Max number of videos per API call
                "key": api_key
            }
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract video title, URL, and video ID
                videos = [
                    {
                        "title": item["snippet"]["title"],
                        "url": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
                        "video_id": item["snippet"]["resourceId"].get("videoId", None)  # Extract YouTube video ID
                    }
                    for item in data.get("items", [])
                ]

                 # Create track_video_id list from extracted video IDs
                track_video_id = [video["video_id"] for video in videos if video["video_id"] is not None]

                return videos, track_video_id  # Return both video details and video IDs
            else:
                st.error("❌ Failed to fetch playlist details. Check your API key and playlist ID.")
                return []

        # 🎯 Find the closest matching song in the playlist
        if not df_tracks.empty:
            # Calculate differences in tempo and loudness
            df_tracks["Tempo Difference"] = abs(df_tracks["Tempo"] - bpm)
            df_tracks["Loudness Difference"] = abs(df_tracks["Loud (Db)"] - loudness)

            # Compute a "match score" (lower is better)
            df_tracks["Match Score"] = df_tracks["Tempo Difference"] + df_tracks["Loudness Difference"]

            # Get the best-matching song
            best_match = df_tracks.loc[df_tracks["Match Score"].idxmin()]

            # 🎵 Display the result
            st.subheader(f"🎵 Your song is **{best_match['Name']}** by **{best_match['Artist']}**")
            
            # Show album cover
            st.image(best_match["Image"], caption=best_match["Name"], width=250)

            
            # 🔍 Fetch video details and extract track_video_id
            videos, track_video_id = fetch_playlist_videos(api_key, youtube_playlist_id)

            # Convert to DataFrame and ensure proper mapping
            video_df = pd.DataFrame(videos)  # Convert videos list to DataFrame
            video_df.rename(columns={"video_id": "track_video_id"}, inplace=True)  # Rename column for consistency

            # Merge YouTube video data into df_tracks (match by song name)
            df_tracks = df_tracks.merge(video_df, how="left", left_on="Name", right_on="title")

            # Refresh best_match to include video_id
            best_match = df_tracks.loc[df_tracks["Match Score"].idxmin()]

            # 🎬 Embed YouTube Video of the Best Match
            if "track_video_id" in best_match and pd.notna(best_match["track_video_id"]):  # Ensure video_id exists
                youtube_embed_url = f"https://www.youtube.com/embed/{best_match['track_video_id']}"
                st.markdown(f"""
                    <iframe width="560" height="315" src="{youtube_embed_url}" 
                    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen></iframe>
                """, unsafe_allow_html=True)
            else:
                st.write("⚠️ No YouTube video available for this track.")

            # 🎵 Button to Add Song to Playlist
            if st.button("➕ Add Song to Playlist"):
                new_song = pd.DataFrame([{
                    "Name": best_match["Name"],
                    "Artist": best_match["Artist"],
                    "Image": best_match["Image"],
                    "track_video_id": best_match["track_video_id"],
                    "Tempo": best_match["Tempo"],   
                    "Loud (Db)": best_match["Loud (Db)"]  
                }])

                # Append song to user playlist
                st.session_state.user_playlist = pd.concat([st.session_state.user_playlist, new_song], ignore_index=True)
                st.success(f"✅ Added **{best_match['Name']}** to your playlist!")

        # 🎼 Display User-Defined Playlist
        if not st.session_state.user_playlist.empty:
            st.subheader("🎶 Your Playlist")
            
            for _, row in st.session_state.user_playlist.iterrows():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.image(row["Image"], width=100)

                with col2:
                    st.write(f"**{row['Name']}** by {row['Artist']}")
                    st.write(f"**Tempo:** {row['Tempo']} BPM")
                    st.write(f"**Loudness:** {row['Loud (Db)']} dB")

            st.write("📋 You can keep adding songs and build your playlist!")

        else:
            st.write("Your playlist is empty. Add songs to create one!")

else:
    st.write("⚠️ Please enter both **Tempo (BPM)** and **Loudness (dB)** to find your matching song.")

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
    
    # Create a DataFrame named df_decades
    df_decades = pd.DataFrame({'Release Date': track_release_date})

    # Convert to datetime and extract the year
    df_decades['Year'] = pd.to_datetime(df_decades['Release Date']).dt.year

    # Compute the decade (numerically, e.g., 1970, 1980, 1990...)
    df_decades['Decade'] = (df_decades['Year'] // 10) * 10

    # Convert decade to a string ending with 's' (e.g., 1970 -> "1970s")
    track_decade = df_decades['track_decade'] = df_decades['Decade'].astype(str) + "s"

    df = pd.read_csv("Symphonia Bards-3.csv")
    track_danceability = df["Dance"].tolist()
    track_energy = df["Energy"].tolist()
    track_loudness = df["Loud (Db)"].tolist()
    track_acousticness = df["Acoustic"].tolist()
    track_instrumentalness = df["Instrumental"].tolist()
    track_liveness = df["Live"].tolist()
    track_valence = df["Happy"].tolist()
    track_tempo = df["BPM"].apply(round).tolist()
    track_signature = df["Time Signature"].tolist()
    track_speechiness = df["Speech"].tolist()
    track_keys_converted = df["Key"].tolist()

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
    
    # Function to fetch playlist details using the YouTube API
    def fetch_playlist_videos(api_key, youtube_playlist_id):
        base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet",
            "playlistId": youtube_playlist_id,
            "maxResults": 50,  # Max number of videos per API call
            "key": api_key
        }
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract video title, URL, and video ID
            videos = [
                {
                    "title": item["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
                    "video_id": item["snippet"]["resourceId"]["videoId"]  # Extract YouTube video ID
                }
                for item in data.get("items", [])
            ]
            
            return videos
        else:
            st.error("❌ Failed to fetch playlist details. Check your API key and playlist ID.")
            return []

  
  

    # Convert track keys to pitch class notation
    # Map numeric key values to pitch class notation
    # key_mapping = {
    #     -1: 'None',
    #     0: 'C',
    #     1: 'C# / Db',
    #     2: 'D',
    #     3: 'D# / Eb',
    #     4: 'E',
    #     5: 'F',
    #     6: 'F# / Gb',
    #     7: 'G',
    #     8: 'G# / Ab',
    #     9: 'A',
    #     10: 'A# / Bb',
    #     11: 'B'
    # }

    # # Convert track keys to pitch class notation
    # track_keys_converted = [key_mapping[key] for key in track_key]


    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    # display the playlist data in a table
    st.header("Additional Playlist Information")
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
    data = {"Image": track_image, "Name": track_names, "Artist": track_artists, "Genre": track_genres, "Release Date": track_release_date, "Release Decade": track_decade, "Popularity": track_popularity, "Duration": track_duration_formatted, "Acoustic": track_acousticness, "Dance": track_danceability, "Energy": track_energy, "Happy": track_valence, "Instrumental": track_instrumentalness, "Key": track_keys_converted, "Live": track_liveness, "Loud (Db)": track_loudness, "Speech": track_speechiness, "Tempo": track_tempo}
    df = pd.DataFrame(data)
    num_total_tracks = len(df)
    df.index += 1
    st.write("The table below is scrollable both horizontally and vertically. Please scroll to the right of the table to see every audio feature. Each column can be clicked to sort in ascending or descending order. Hovering over a column header will explain what that feature represents.")
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
            "Release Decade": st.column_config.TextColumn(
                "Release Decade", help="The decade when the track or album was released"
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
    # data2 = {"Name": track_names, "ID": track_id}
    # df2 = pd.DataFrame(data2)
    # selected_audio = st.selectbox("Select a song from the playlist to play its preview:", df2["Name"])
    # if selected_audio:
    #     selected_url = df2[df2["Name"] == selected_audio]["ID"].values[0]
    #     embed_url = f"https://open.spotify.com/embed/track/{selected_url}"
    #     st.markdown(f'<iframe src="{embed_url}" width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
    # st.markdown("<br>", unsafe_allow_html=True)


    # Display the full playlist player
    playlist_embed_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
    st.markdown(f'<iframe src="{playlist_embed_url}" width="100%" height="400" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)

    # Add title and description
    st.title("YouTube Playlist Player")
    st.write("Click on the hamburger icon in the top right of the YouTube player to navigate the playlist.")

    # Embed YouTube playlist with strict-origin referrer policy
    components.html(f"""
        <iframe 
            src="https://www.youtube.com/embed/videoseries?list=PLtg7R4Q_LfGU-WLVp5jeOoD7tdUiS6FHg" 
            scrolling="yes" 
            height="350" 
            width="100%" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; gyroscope; web-share" 
            >
        </iframe>
    """, height=350)


    # Function to fetch playlist details using the YouTube API
    def fetch_playlist_videos(api_key, youtube_playlist_id):
        base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet",
            "playlistId": youtube_playlist_id,
            "maxResults": 50,  # Max number of videos per API call
            "key": api_key
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            videos = [
                {
                    "title": item["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                }
                for item in data["items"]
            ]
            return videos
        else:
            st.error("Failed to fetch playlist details.")
            return []

   

    # Fetch playlist details
    videos = fetch_playlist_videos(api_key, youtube_playlist_id)

    if videos:
        # Default video (first video in the playlist)
        default_video_url = videos[0]["url"]

        # Create a dropdown menu for video selection
        selected_video = st.selectbox(
            "Or choose a video from your playlist to watch:",
            options=videos,
            format_func=lambda video: video["title"]  # Use the video title as the dropdown label
        )

        # Get the selected video URL
        selected_video_url = selected_video["url"]

        # Extract the YouTube video ID
        youtube_video_id = selected_video_url.split("v=")[-1].split("&")[0]

        # Embed the selected YouTube video with height 350px
        youtube_embed_html = f"""
        <iframe width="100%" height="350" src="https://www.youtube.com/embed/{youtube_video_id}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen></iframe>
        """
        
        st.markdown(youtube_embed_html, unsafe_allow_html=True)

    else:
        st.write("No videos found in the playlist.")



    # Add some spacing
    st.markdown("<br><br>", unsafe_allow_html=True)

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
    genre_counts = pd.Series(df_genres["Genre"]).value_counts()

    # Calculate the percentage for each genre
    genre_percentages = (genre_counts / genre_counts.sum()) * 100

    # Sort genres by their percentage in descending order
    genre_percentages_sorted = genre_percentages.sort_values(ascending=False)

    # Calculate the cumulative sum and filter to only include genres up to 80%
    cumulative_percentages = genre_percentages_sorted.cumsum()
    top_genres_80 = genre_percentages_sorted[cumulative_percentages <= 80]

    # Display the title for the chart
    st.write(f"### Main Genres of Songs")

    # Create a colorful horizontal bar chart using Plotly
    fig_genres = px.bar(
        top_genres_80,
        x=top_genres_80.values,
        y=top_genres_80.index,
        orientation='h',  # Horizontal bar chart
        labels={'x': 'Percentage of Songs (%)', 'y': 'Genres'},
        color=top_genres_80.index,  # Use the genre names to create color categories
        color_discrete_sequence=px.colors.qualitative.Set3  # Set a qualitative color palette
    )

    # Customize hovertemplate to show only the percentage
    fig_genres.update_traces(hovertemplate='%{x:.1f}%<extra></extra>')

    # Customize the bar chart's appearance
    fig_genres.update_layout(
        xaxis_title="Percentage of Songs (%)",
        yaxis_title="Genres",
        xaxis=dict(range=[0, 100]),  # Set x-axis range from 0 to 100
        margin=dict(t=0),  # Remove the space at the top of the chart
        showlegend=False
    )

    # Display the bar chart in Streamlit
    st.plotly_chart(fig_genres)


    # Create a DataFrame to hold track names and track_decade
    df_decades = pd.DataFrame({
        'Track': track_names,
        'Decade': track_decade
    })

    # Calculate the percentage of songs in each decade
    decade_counts = df_decades['Decade'].value_counts(normalize=True) * 100

    # Sort the decades in chronological order
    decade_counts = decade_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_decades = pd.DataFrame({
        'Decade': decade_counts.index,
        'Percentage of Songs (%)': decade_counts.values
    })

    # Create a vertical bar chart using Plotly
    fig_decades = go.Figure(go.Bar(
        x=df_bins_decades['Decade'],  # The decade categories
        y=df_bins_decades['Percentage of Songs (%)'],  # The percentages
        text=[f"{perc:.1f}%" for perc in df_bins_decades['Percentage of Songs (%)']],  # Display percentages as text inside the bars
        textposition='auto',  # Position the text inside the bars automatically
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A']),  # Custom colors
    ))

    # Update layout for the vertical bar chart
    fig_decades.update_layout(
        title_text='Percentage of Songs by Decade',
        xaxis_title='Decade',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_decades)

    # Calculate the average popularity
    if track_popularity:
        average_popularity = sum(track_popularity) / len(track_popularity)
    else:
        average_popularity = 0

    # Create a thicker progress bar using custom HTML and CSS for popularity
    progress_percentage = int(average_popularity)  # Popularity is already on a 0-100 scale

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}
        </div>
    </div>
    """

    # Display the average popularity (0-100 scale)
    st.write(f"The average popularity of the songs in this playlist is: {int(average_popularity)} / 100")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and popularity
    df_popularity = pd.DataFrame({
        'Track': track_names,
        'Popularity': track_popularity  # Popularity on 0-100 scale
    })

    # Define the bins for popularity (0-10, 10-20, etc.)
    bins = [i for i in range(0, 101, 10)]  # Create bins for every 10

    # Assign each track to a bin
    df_popularity['Popularity Bin'] = pd.cut(df_popularity['Popularity'], bins=bins, right=False)

    # Calculate the percentage of songs in each popularity bin
    bin_counts = pd.Series(df_popularity['Popularity Bin']).value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_popularity = pd.DataFrame({
        'Popularity Range': [f"{int(interval.left)} - {int(interval.right)}" for interval in bin_counts.index],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Create a vertical bar chart using Plotly
    fig_popularity = go.Figure(go.Bar(
        x=df_bins_popularity['Popularity Range'],  # The popularity categories
        y=df_bins_popularity['Percentage of Songs (%)'],  # The percentages
        text=[f"{perc:.1f}%" for perc in df_bins_popularity['Percentage of Songs (%)']],  # Display percentages as text inside the bars
        textposition='auto',  # Position the text inside the bars automatically
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A']),  # Custom colors
    ))

    # Update layout for the vertical bar chart
    fig_popularity.update_layout(
        title_text='Percentage of Songs by Popularity Range',
        xaxis_title='Popularity Range',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_popularity)

    # Function to convert duration from milliseconds to minutes
    def ms_to_minutes(ms):
        return ms // 60000  # Convert milliseconds to minutes

    # Apply the conversion to the track durations
    track_durations_minutes = [ms_to_minutes(duration) for duration in track_duration]

    # Create bins for the durations (0-1 mins, 1-2 mins, etc.)
    bins = pd.cut(track_durations_minutes, bins=range(0, max(track_durations_minutes)+2), right=False)

    # Count the occurrences in each bin
    duration_counts = pd.Series(bins).value_counts().sort_index()

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

    # Create a thicker progress bar using custom HTML and CSS for acousticness
    progress_percentage = int(average_acousticness)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}
        </div>
    </div>
    """

    # Display the average acousticness (0-100 scale)
    st.write(f"The average acousticness of the songs in this playlist is: {int(average_acousticness)} / 100")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and acousticness
    df_acousticness = pd.DataFrame({
        'Track': track_names,
        'Acousticness': track_acousticness  # Now assumed to be in the range 0-100
    })

    # Define the bins for acousticness (0–10, 10–20, 20–30, ..., 90–100)
    bins = list(range(0, 101, 10))  # [0, 10, 20, ..., 100]

    # Assign each track to a bin
    df_acousticness['Acousticness Bin'] = pd.cut(
        df_acousticness['Acousticness'],
        bins=bins,
        right=False  # [0,10), [10,20), etc.
    )

    # Calculate the percentage of songs in each acousticness bin
    bin_counts = pd.Series(df_acousticness['Acousticness Bin']).value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_acousticness = pd.DataFrame({
        'Acousticness Range': [
            f"{interval.left:.0f} - {interval.right:.0f}" for interval in bin_counts.index
        ],
        'Percentage of Songs (%)': bin_counts.values
    })


    # Create a vertical bar chart using Plotly
    fig_acousticness = go.Figure(go.Bar(
        x=df_bins_acousticness['Acousticness Range'],  # The acousticness categories
        y=df_bins_acousticness['Percentage of Songs (%)'],  # The percentages
        text=[f"{perc:.1f}%" for perc in df_bins_acousticness['Percentage of Songs (%)']],  # Display percentages as text inside the bars
        textposition='auto',  # Position the text inside the bars automatically
        marker=dict(color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A']),  # Custom colors
    ))

    # Update layout for the vertical bar chart
    fig_acousticness.update_layout(
        title_text='Percentage of Songs by Acousticness Range',
        xaxis_title='Acousticness Range',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_acousticness)


    # Calculate the average danceability
    if track_danceability:
        average_danceability = sum(track_danceability) / len(track_danceability)
    else:
        average_danceability = 0

    # Create a thicker progress bar using custom HTML and CSS for danceability
    progress_percentage = int(average_danceability)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}
        </div>
    </div>
    """

    # Display the average danceability (0-1 scale)
    st.write(f"The average danceability of the songs in this playlist is: {int(average_danceability)} / 100")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and danceability
    df_danceability = pd.DataFrame({
        'Track': track_names,
        'Danceability': track_danceability  # Now assumed to be in the range 0-100
    })

    # Define the bins for danceability (0–10, 10–20, 20–30, ..., 90–100)
    bins = list(range(0, 101, 10))  # [0, 10, 20, ..., 100]

    # Assign each track to a bin
    df_danceability['Danceability Bin'] = pd.cut(
        df_danceability['Danceability'],
        bins=bins,
        right=False  # [0,10), [10,20), etc.
    )

    # Calculate the percentage of songs in each danceability bin
    bin_counts = pd.Series(df_danceability['Danceability Bin']).value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_danceability = pd.DataFrame({
        'Danceability Range': [
            f"{interval.left:.0f} - {interval.right:.0f}" for interval in bin_counts.index
        ],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Create a vertical bar chart using Plotly
    fig_danceability = go.Figure(go.Bar(
        x=df_bins_danceability['Danceability Range'],  # The danceability categories
        y=df_bins_danceability['Percentage of Songs (%)'],  # The percentages
        text=[f"{perc:.1f}%" for perc in df_bins_danceability['Percentage of Songs (%)']],  # Display percentages as text
        textposition='auto',  # Position the text inside the bars
        marker=dict(
            color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', 
                '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A']
        ),
    ))

    # Update layout for the vertical bar chart
    fig_danceability.update_layout(
        title_text='Percentage of Songs by Danceability Range',
        xaxis_title='Danceability Range',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks for percentage
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_danceability)



    # Calculate the average energy
    if track_energy:
        average_energy = sum(track_energy) / len(track_energy)
    else:
        average_energy = 0

    # Create a thicker progress bar using custom HTML and CSS for energy
    progress_percentage = int(average_energy)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}
        </div>
    </div>
    """

    # Display the average energy (0-1 scale)
    st.write(f"The average energy of the songs in this playlist is: {int(average_energy)} / 100")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and energy
    df_energy = pd.DataFrame({
        'Track': track_names,
        # If your energy values are originally 0–1, multiply them by 100:
        'Energy': track_energy
    })

    # Define bins for energy (0–10, 10–20, ..., 90–100)
    bins = list(range(0, 101, 10))  # [0, 10, 20, ..., 100]

    # Assign each track to a bin
    df_energy['Energy Bin'] = pd.cut(
        df_energy['Energy'], 
        bins=bins, 
        right=False  # intervals: [0,10), [10,20), etc.
    )

    # Calculate the percentage of songs in each energy bin
    bin_counts = pd.Series(df_energy['Energy Bin']).value_counts(normalize=True) * 100

    # Sort the bins so they appear in ascending order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_energy = pd.DataFrame({
        'Energy Range': [
            f"{interval.left:.0f} - {interval.right:.0f}" for interval in bin_counts.index
        ],
        'Percentage of Songs (%)': bin_counts.values
    })

    # Create a vertical bar chart using Plotly
    fig_energy = go.Figure(
        go.Bar(
            x=df_bins_energy['Energy Range'],  # The energy categories
            y=df_bins_energy['Percentage of Songs (%)'],  # The percentages
            text=[f"{perc:.1f}%" for perc in df_bins_energy['Percentage of Songs (%)']],  # Text inside the bars
            textposition='auto',  
            marker=dict(
                color=[
                    '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
                    '#19D3F3', '#FF6692', '#FFB81C', '#B6E880', '#FFA07A'
                ]
            ),
        )
    )

    # Update layout for the vertical bar chart
    fig_energy.update_layout(
        title_text='Percentage of Songs by Energy Range',
        xaxis_title='Energy Range',
        yaxis_title='Percentage of Songs (%)',
        yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks
        showlegend=False  # Disable the legend
    )

    # Display the vertical bar chart in Streamlit
    st.plotly_chart(fig_energy)

    # Calculate the average happiness (valence)
    if track_valence:
        average_happiness = sum(track_valence) / len(track_valence)
    else:
        average_happiness = 0

    # Create a thicker progress bar using custom HTML and CSS for happiness
    progress_percentage = int(average_happiness)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}
        </div>
    </div>
    """

    # Display the average happiness (0-1 scale)
    st.write(f"The average happiness of the songs in this playlist is: {int(average_happiness)} / 100")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and happiness (valence)
    # Create a DataFrame to hold track names and happiness (valence)
    df_happiness = pd.DataFrame({
        'Track': track_names,
        # If your valence (happiness) values are in 0–1, multiply by 100 here:
        'Happiness (Valence)': track_valence
    })

    # Define the bins for happiness (valence) (0–10, 10–20, ..., 90–100)
    bins = list(range(0, 101, 10))

    # Assign each track to a bin
    df_happiness['Happiness Bin'] = pd.cut(
        df_happiness['Happiness (Valence)'], 
        bins=bins, 
        right=False  # intervals: [0,10), [10,20), etc.
    )

    # Calculate the percentage of songs in each happiness bin
    bin_counts = pd.Series(df_happiness['Happiness Bin']).value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_happiness = pd.DataFrame({
        'Happiness Range': [
            f"{interval.left:.0f} - {interval.right:.0f}" for interval in bin_counts.index
        ],
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
    progress_percentage = int(average_instrumentalness)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}
        </div>
    </div>
    """

    # Display the average instrumentalness (0-1 scale)
    st.write(f"The average instrumentalness of the songs in this playlist is: {int(average_instrumentalness)} / 100")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    
    # Create a DataFrame to hold track names and instrumentalness
    df_instrumentalness = pd.DataFrame({
        'Track': track_names,
        # If your instrumentalness values are originally 0–1, multiply by 100 here:
        'Instrumentalness': track_instrumentalness
    })

    # Define the bins for instrumentalness (0–10, 10–20, ..., 90–100)
    bins = list(range(0, 101, 10))

    # Assign each track to a bin
    df_instrumentalness['Instrumentalness Bin'] = pd.cut(
        df_instrumentalness['Instrumentalness'],
        bins=bins,
        right=False  # intervals: [0,10), [10,20), etc.
    )

    # Calculate the percentage of songs in each instrumentalness bin
    bin_counts = pd.Series(df_instrumentalness['Instrumentalness Bin']).value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_instrumentalness = pd.DataFrame({
        'Instrumentalness Range': [
            f"{interval.left:.0f} - {interval.right:.0f}" for interval in bin_counts.index
        ],
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
    key_counts = pd.Series(df_keys['Key']).value_counts(normalize=True) * 100  # Calculate percentage
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
    progress_percentage = int(average_liveness)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}
        </div>
    </div>
    """

    # Display the average liveness (0-1 scale)
    st.write(f"The average liveness of the songs in this playlist is: {int(average_liveness)} / 100")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and liveness
    # Create a DataFrame to hold track names and liveness
    df_liveness = pd.DataFrame({
        'Track': track_names,
        # If your liveness values are originally 0–1, multiply by 100 here:
        'Liveness': track_liveness
    })

    # Define the bins for liveness (0–10, 10–20, ..., 90–100)
    bins = list(range(0, 101, 10))

    # Assign each track to a bin
    df_liveness['Liveness Bin'] = pd.cut(
        df_liveness['Liveness'],
        bins=bins,
        right=False  # intervals: [0,10), [10,20), etc.
    )

    # Calculate the percentage of songs in each liveness bin
    bin_counts = pd.Series(df_liveness['Liveness Bin']).value_counts(normalize=True) * 100
    # Sort the bins in ascending order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_liveness = pd.DataFrame({
        'Liveness Range': [
            f"{interval.left:.0f} - {interval.right:.0f}" for interval in bin_counts.index
        ],
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
    loudness_binned_counts = pd.Series(loudness_binned).value_counts().sort_index()

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
    progress_percentage = int(average_speechiness)  # Multiply by 100 for percentage

    progress_bar_html = f"""
    <div style="width: 100%; background-color: #ddd; height: 30px; border-radius: 10px; overflow: hidden;">
        <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 100%; text-align: center; line-height: 30px; color: white; border-radius: 10px 0 0 10px;">
            {progress_percentage}
        </div>
    </div>
    """

    # Display the average speechiness (0-1 scale)
    st.write(f"The average speechiness of the songs in this playlist is: {int(average_speechiness)} / 100")

    # Display the custom thicker progress bar
    st.markdown(progress_bar_html, unsafe_allow_html=True)

    st.write("")

    # Create a DataFrame to hold track names and speechiness
    # Create a DataFrame to hold track names and speechiness
    df_speechiness = pd.DataFrame({
        'Track': track_names,
        # If your speechiness values are originally 0–1, multiply by 100 here:
        'Speechiness': track_speechiness
    })

    # Define bins for speechiness (0–10, 10–20, ..., 90–100)
    bins = list(range(0, 101, 10))

    # Assign each track to a bin
    df_speechiness['Speechiness Bin'] = pd.cut(
        df_speechiness['Speechiness'],
        bins=bins,
        right=False  # intervals: [0,10), [10,20), etc.
    )

    # Calculate the percentage of songs in each speechiness bin
    bin_counts = pd.Series(df_speechiness['Speechiness Bin']).value_counts(normalize=True) * 100

    # Sort the bins so they appear in order
    bin_counts = bin_counts.sort_index()

    # Create a DataFrame for the bar chart
    df_bins_speechiness = pd.DataFrame({
        'Speechiness Range': [
            f"{interval.left:.0f} - {interval.right:.0f}" for interval in bin_counts.index
        ],
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

    # # Create a DataFrame to hold track names and speechiness
    # df_speechiness = pd.DataFrame({
    #     'Track': track_names,
    #     'Speechiness': track_speechiness  # Keep speechiness in 0-1 range
    # })

    # # Assign each track to a bin
    # df_speechiness['Speechiness Bin'] = pd.cut(df_speechiness['Speechiness'], bins=bins, right=False)

    # # Calculate the percentage of songs in each speechiness bin
    # bin_counts = df_speechiness['Speechiness Bin'].value_counts(normalize=True) * 100

    # # Sort the bins so they appear in order
    # bin_counts = bin_counts.sort_index()

    # # Create a DataFrame for the bar chart
    # df_bins_speechiness = pd.DataFrame({
    #     'Speechiness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
    #     'Percentage of Songs (%)': bin_counts.values
    # })

    # # Create a colorful bar chart using Plotly
    # fig_speechiness = px.bar(
    #     df_bins_speechiness,
    #     x=df_bins_speechiness.index,
    #     y='Percentage of Songs (%)',
    #     title='Distribution of Speechiness',
    #     labels={'x': 'Speechiness Range', 'y': 'Percentage of Songs (%)'},
    #     color=df_bins_speechiness['Percentage of Songs (%)'],  # Use the percentage to color the bars
    #     color_continuous_scale='Rainbow'  # Choose a color scale
    # )

    # # Update layout for better visuals
    # fig_speechiness.update_layout(
    #     xaxis_title='Speechiness Range',
    #     yaxis_title='Percentage of Songs (%)',
    #     coloraxis_showscale=False  # Show the color scale
    # )

    # # Display the colorful bar chart in Streamlit
    # st.plotly_chart(fig_speechiness)

    # # Define the bins for speechiness (0-0.1, 0.1-0.2, etc.)
    # bins = [i/10 for i in range(0, 11)]  # Create bins for every 0.1

    # # Assign each track to a bin
    # df_speechiness['Speechiness Bin'] = pd.cut(df_speechiness['Speechiness'], bins=bins, right=False)

    # # Calculate the percentage of songs in each speechiness bin
    # bin_counts = df_speechiness['Speechiness Bin'].value_counts(normalize=True) * 100

    # # Sort the bins so they appear in order
    # bin_counts = bin_counts.sort_index()

    # # Create a DataFrame for the bar chart
    # df_bins_speechiness = pd.DataFrame({
    #     'Speechiness Range': [f"{interval.left:.1f} - {interval.right:.1f}" for interval in bin_counts.index],
    #     'Percentage of Songs (%)': bin_counts.values
    # })

    # # Set the Speechiness Range as the index for the chart
    # df_bins_speechiness.set_index('Speechiness Range', inplace=True)

    # # Display the bar chart of speechiness ranges using st.bar_chart
    # st.bar_chart(df_bins_speechiness, x_label="Speechiness Score", y_label="Percentage of Songs (%)")


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
    tempo_counts = pd.Series(df_tempo['Tempo Category']).value_counts(normalize=True) * 100
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
        'speechiness': track_speechiness
        # 'key': track_keys
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
    features = ['danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'liveness', 'happiness', 'tempo', 'speechiness']

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
    track2 = st.selectbox(
        "Select Song 2", 
        df_audio_features_scaled['name'].unique(), 
        index=1  # Default to the second item in the unique list
    )

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
            y=0.13,  # Adjust the position of the color bar title to be lower
            yref="paper",
        ),
        margin=dict(t=0),  # Remove the space at the top of the chart
    )

    # Display the heatmap in Streamlit
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Sort "Release Decade" in chronological order (e.g., 1960s, 1970s, ...)
    df["Release Decade"] = pd.Categorical(
        df["Release Decade"], categories=["1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"], ordered=True
    )

    histogram_numeric_columns = ["Popularity", "Acoustic", "Dance", "Release Decade", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]

    # Dropdown menu for selecting which column to display in the histogram
    selected_column = st.selectbox("Choose a feature to display in the histogram", histogram_numeric_columns)

    # Plotly's qualitative color scale
    color_scale = qualitative.Prism

    # Create the histogram using Plotly's go.Figure with nbinsx=20
    fig_histogram = go.Figure()

    # Create the histogram using Plotly's go.Figure with nbinsx=20
    fig_histogram = go.Figure()

    if selected_column == "Release Decade":
        # Handle the "Release Decade" separately to ensure it's sorted correctly
        sorted_data = df[selected_column].dropna().sort_values()
        fig_histogram.add_trace(go.Histogram(
            x=sorted_data,
            marker=dict(
                color=color_scale * (len(sorted_data) // len(color_scale) + 1)
            ),
            name=f"{selected_column} Distribution"
        ))
    else:
        # Handle numeric columns
        fig_histogram.add_trace(go.Histogram(
            x=df[selected_column],
            nbinsx=20,
            marker=dict(
                color=color_scale * (len(df[selected_column]) // len(color_scale) + 1)
            ),
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



    analysis_numeric_columns = ["Name", "Artist", "Release Date", "Release Decade", "Genre", "Popularity", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]

    # Bivariate Analysis
    st.write("### Bivariate Analysis")
    x_axis = st.selectbox("Select a variable for the x-axis:", analysis_numeric_columns)
    y_axis = st.selectbox("Select a variable for the y-axis:", analysis_numeric_columns)

   # Special handling for "Release Decade" if it's on the x-axis or y-axis
    if x_axis == "Release Decade" or y_axis == "Release Decade":
        fig_bivariate = px.scatter(
            df.sort_values("Release Decade"),  # Ensure "Release Decade" is sorted
            x=x_axis,
            y=y_axis,
            title=f"{x_axis} vs. {y_axis}",
            category_orders={"Release Decade": ["1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]}
        )
    else:
        fig_bivariate = px.scatter(df, x=x_axis, y=y_axis, title=f"{x_axis} vs. {y_axis}")

    fig_bivariate.update_traces(marker=dict(size=12))  # Adjust marker size here
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
    analysis_columns = ["Name", "Artist", "Release Date", "Release Decade", "Genre"] + numeric_columns

    # Select variables for the x-axis, y-axis, color, and size
    x_axis = st.selectbox("Select a variable for the x-axis:", numeric_columns)
    y_axis = st.selectbox("Select a variable for the y-axis:", numeric_columns)
    color_by = st.selectbox("Select a variable to color by:", analysis_columns)
    size_by = st.selectbox("Select a variable to size by:", numeric_columns)

    # Handle "Release Decade" special case for coloring
    if color_by == "Release Decade":
        fig_multivariate = px.scatter(
            df.sort_values("Release Decade"),  # Ensure "Release Decade" is sorted
            x=x_axis,
            y=y_axis,
            color=color_by,
            size=size_by,
            hover_name="Name",
            title=f"{x_axis} vs. {y_axis} Colored by {color_by} and Sized by {size_by}",
            category_orders={"Release Decade": ["1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]}
        )
    else:
        # Default behavior for non-special cases
        fig_multivariate = px.scatter(
            df, x=x_axis, y=y_axis, color=color_by, size=size_by, hover_name="Name",
            title=f"{x_axis} vs. {y_axis} Colored by {color_by} and Sized by {size_by}"
        )

    # Make the chart wider using the update_layout() method
    fig_multivariate.update_layout(width=1000, height=700)  # Adjust the width and height

    # Display the chart in Streamlit
    st.plotly_chart(fig_multivariate)

    