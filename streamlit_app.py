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

# Initialize playlist_id as None or hardcoded here (Spotify)
playlist_id = "3BGJRi9zQrIjLDtBbRYy5n"

# YouTube API key and playlist ID (replace with your own)
api_key = "AIzaSyAxHBK8MxzePcos86BOaBwUtTurr_ZbpNg"  # Replace with your API key
youtube_playlist_url = "https://www.youtube.com/playlist?list=PLtg7R4Q_LfGU-WLVp5jeOoD7tdUiS6FHg"
youtube_playlist_id = youtube_playlist_url.split("list=")[-1]

# Define the CSV filename as a variable
song_features_csv = "Symphonia Bards-3.csv"

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
    df_audio_features = pd.read_csv(song_features_csv)

    # Extract individual audio feature columns
    track_danceability = df_audio_features["Dance"].tolist()
    track_duration = df_audio_features["Time"].tolist()
    track_energy = df_audio_features["Energy"].tolist()
    track_loudness = df_audio_features["Loud (Db)"].tolist()
    track_acousticness = df_audio_features["Acoustic"].tolist()
    track_instrumentalness = df_audio_features["Instrumental"].tolist()
    track_liveness = df_audio_features["Live"].tolist()
    track_valence = df_audio_features["Happy"].tolist()
    track_tempo = df_audio_features["BPM"].apply(round).tolist()
    track_signature = df_audio_features["Time Signature"].tolist()
    track_speechiness = df_audio_features["Speech"].tolist()
    track_keys_converted = df_audio_features["Key"].tolist()

    # Extract genres by fetching artist details
    track_genres = []
    for track in tracks:
        artist_id = track["track"]["artists"][0]["id"]  # Get the first artist for simplicity
        artist = sp.artist(artist_id)  # Fetch artist information
        genres = artist.get("genres", [])  # Extract genres from artist
        first_genre = genres[0] if genres else "No genre available"  # Get the first genre, or a default if no genres exist
        track_genres.append(first_genre)

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
            
    # 🔍 Fetch video details and extract track_video_id
    videos, track_video_id = fetch_playlist_videos(api_key, youtube_playlist_id)

    # 🟢 Combine All Data into One DataFrame
    df_tracks = pd.DataFrame({
        "Track ID": track_id,
        "Name": track_names,
        "Artist": track_artists,
        "Album": track_album,
        "Popularity": track_popularity,
        "Release Date": track_release_date,
        "Decade": track_decade,
        "Spotify URL": track_url,
        "Spotify Preview": track_preview,
        "Image": track_image,
        "Danceability": track_danceability,
        "Energy": track_energy,
        "Loudness (dB)": track_loudness,
        "Acousticness": track_acousticness,
        "Instrumentalness": track_instrumentalness,
        "Liveness": track_liveness,
        "Happiness": track_valence,
        "Tempo (BPM)": track_tempo,
        "Time Signature": track_signature,
        "Speechiness": track_speechiness,
        "Key": track_keys_converted,
        "Duration": track_duration,
        "Genre": track_genres,
        "YouTube Video ID": track_video_id[:len(track_id)],  # Ensure lengths match
    })

# Initialize user playlist in session state if it doesn’t exist
if "user_playlist" not in st.session_state:
    st.session_state.user_playlist = []

image = Image.open('data_adventures_logo.png')
col1, col2, col3 = st.columns([1,6,1])

with col1:
    st.write("")

with col2:
    st.image(image, width=int(image.width * 0.4))

with col3:
    st.write("")

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

# Ensure number input does not reset, but starts empty
loudness = st.number_input(
    "Enter the relative loudness of your song (in dB, typically between -60 and 0):",
    min_value=-60, max_value=0, value=None, step=1, format="%d"
)

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

# 🟢 Ensure both BPM & Loudness are entered before proceeding
if bpm is not None and loudness is not None:
    # 🎯 Find the closest matching song in the playlist
    if not df_tracks.empty:
        # Calculate differences in tempo and loudness
        df_tracks["Tempo Difference"] = abs(df_tracks["Tempo (BPM)"] - bpm)
        df_tracks["Loudness Difference"] = abs(df_tracks["Loudness (dB)"] - loudness)

        # Compute a "match score" (lower is better)
        df_tracks["Match Score"] = df_tracks["Tempo Difference"] + df_tracks["Loudness Difference"]

        # Get the best-matching song
        best_match = df_tracks.loc[df_tracks["Match Score"].idxmin()]

        # 🎵 Display the result
        st.subheader(f"🎵 Your song is **{best_match['Name']}** by **{best_match['Artist']}**")
        
        # Create columns for layout
        col1, spacer, col2 = st.columns([1, 0.5, 1]) 

        # Display album cover in first column
        with col1:
            st.image(best_match["Image"], caption=best_match["Name"], width=250)

        # Display BPM and Loudness in second column
        with col2:
            st.write(f"🎚️ **BPM:** {best_match['Tempo (BPM)']}")
            st.write(f"🔊 **Loudness:** {best_match['Loudness (dB)']} dB")

        # 🎥 Embed YouTube video if available
        if pd.notna(best_match["YouTube Video ID"]): # Ensure there is a valid video ID
            youtube_embed_url = f"https://www.youtube.com/embed/{best_match['YouTube Video ID']}"
            st.video(youtube_embed_url)
        else:
            st.write("⚠️ No YouTube video available for this track.")
    
        # ➕ Add Song to Playlist Button
        if "user_playlist" not in st.session_state:
            st.session_state.user_playlist = []  # Initialize playlist if not set
        
        if st.button("➕ Add to Playlist", key=best_match["Track ID"]):
            song_data = {
                "Track ID": best_match["Track ID"],
                "Name": best_match["Name"],
                "Artist": best_match["Artist"],
                "Album": best_match["Album"],
                "Popularity": best_match["Popularity"],
                "Release Date": best_match["Release Date"],
                "Decade": best_match["Decade"],
                "Spotify URL": best_match["Spotify URL"],
                "Spotify Preview": best_match["Spotify Preview"],
                "Image": best_match["Image"],
                "Danceability": best_match["Danceability"],
                "Energy": best_match["Energy"],
                "Loudness (dB)": best_match["Loudness (dB)"],
                "Acousticness": best_match["Acousticness"],
                "Instrumentalness": best_match["Instrumentalness"],
                "Liveness": best_match["Liveness"],
                "Happiness": best_match["Happiness"],
                "Tempo (BPM)": best_match["Tempo (BPM)"],
                "Time Signature": best_match["Time Signature"],
                "Speechiness": best_match["Speechiness"],
                "Key": best_match["Key"],
                "Duration": best_match["Duration"],
                "Genre": best_match["Genre"],
                "YouTube Video ID": best_match["YouTube Video ID"]
            }

            # Add song only if it's not already in the playlist
            if song_data not in st.session_state.user_playlist:
                st.session_state.user_playlist.append(song_data)
                st.success(f"✅ Added {best_match['Name']} to your playlist!")
            else:
                st.warning("⚠️ This song is already in your playlist!")


        # 🎵 Display the User's Playlist Below
        st.subheader("🎶 Your Playlist")
        if st.session_state.user_playlist:
            for song in st.session_state.user_playlist:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(song["Image"], width=80)
                with col2:
                    st.write(f"**{song['Name']}** by {song['Artist']}")
                    st.markdown(f"**Tempo:** {song['Tempo (BPM)']} BPM &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; **Loudness:** {song['Loudness (dB)']} dB")
        else:
                st.write("Your playlist is empty. Add songs to create one!")  
    