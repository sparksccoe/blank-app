import streamlit as st
import requests
import streamlit.components.v1 as components
import os
import random
import string
import shutil
import base64
from datetime import datetime, timedelta
from PIL import Image

st.set_page_config(
    page_title="Data Adventures",  # 👈 This is what shows in the browser tab
    page_icon="🧭",                # Optional: shows in the tab as a favicon
    layout="centered",                 # Optional: "centered" or "wide"
    initial_sidebar_state="auto",  # Optional: "expanded", "collapsed", or "auto"
)

# Inject custom CSS to adjust the max-width of the main content area
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 1200px; /* Adjust this value as needed */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Combine hiding UI elements and background image styling
hide_streamlit_style = """
    <style>
    /* Hide Streamlit default UI elements */
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    #MainMenu,
    header,
    footer {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }

    /* Add a full-screen background image with transparency */
    .background-container {
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        width: 100%;
        z-index: -1;
        background-image: url('zelda.jpg');
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.5; /* Adjust transparency */
    }
    </style>

    <div class="background-container"></div>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
with open("style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

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

def remove_song(idx):
    if "user_playlist" in st.session_state and idx < len(st.session_state.user_playlist):
        st.session_state.user_playlist.pop(idx)

# Initialize playlist_id as None or hardcoded here (Spotify)
playlist_id = "3BGJRi9zQrIjLDtBbRYy5n"

# YouTube API key and playlist ID (replace with your own)
api_key = "AIzaSyAxHBK8MxzePcos86BOaBwUtTurr_ZbpNg"  # Replace with your API key
youtube_playlist_url = "https://www.youtube.com/playlist?list=PLtg7R4Q_LfGU-WLVp5jeOoD7tdUiS6FHg"
youtube_playlist_id = youtube_playlist_url.split("list=")[-1]

# Define the CSV filename as a variable
song_features_csv = "Symphonia Bards-3.csv"

if playlist_id:
    # 🟢 Load additional song features from CSV
    df_audio_features = pd.read_csv(song_features_csv)

    # Extract individual audio feature columns
    track_id = df_audio_features["Spotify Track Id"].tolist()
    track_names = df_audio_features["Song"].tolist()
    track_artists = df_audio_features["Artist"].tolist()
    track_popularity = df_audio_features["Popularity"].tolist()
    track_duration = df_audio_features["Time"].tolist()
    track_album = df_audio_features["Album"].tolist()
    track_image = df_audio_features["Image"].tolist()
    track_release_date = df_audio_features["Album Date"].tolist()
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
    track_bard = df_audio_features["Bard"].tolist()

     # Create a DataFrame for track decades
    df_decades = pd.DataFrame({'Release Date': track_release_date})
    df_decades['Year'] = pd.to_datetime(df_decades['Release Date']).dt.year
    df_decades['Decade'] = (df_decades['Year'] // 10) * 10
    track_decade = df_decades['Decade'].astype(str) + "s"

    # # Extract genres by fetching artist details
    # track_genres = []
    # for track in tracks:
    #     artist_id = track["track"]["artists"][0]["id"]  # Get the first artist for simplicity
    #     artist = sp.artist(artist_id)  # Fetch artist information
    #     genres = artist.get("genres", [])  # Extract genres from artist
    #     first_genre = genres[0] if genres else "No genre available"  # Get the first genre, or a default if no genres exist
    #     track_genres.append(first_genre)

    # # Extract genres using artist IDs from CSV
    # track_genres = []
    # for artist_name in track_artists:
    #     # Search for the artist on Spotify
    #     results = sp.search(q=artist_name, type="artist", limit=1)
        
    #     if results["artists"]["items"]:
    #         artist = results["artists"]["items"][0]  # Get the first matching artist
    #         genres = artist.get("genres", [])  # Extract genres from artist data
    #         first_genre = genres[0] if genres else "No genre available"
    #     else:
    #         first_genre = "No genre available"  # Handle case where artist is not found
        
    #     track_genres.append(first_genre)

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
        "Bard": track_bard,
        # "Genre": track_genres,
        "YouTube Video ID": track_video_id[:len(track_id)],  # Ensure lengths match
    })

# Load creature data
if playlist_id:
    creatures_csv = "DA Creatures.csv"
    df_creatures_data = pd.read_csv(creatures_csv)

    # Extract individual creature attributes
    creature_names = df_creatures_data["Name"].tolist()
    creature_tempo_preferences = df_creatures_data["Tempo Preference"].tolist()
    creature_loudness_preferences = df_creatures_data["Loudness Preference"].tolist()
    creature_task_categories = df_creatures_data["Task Category"].tolist()
    creature_task_specific_1 = df_creatures_data["Task Specific 1"].tolist()
    creature_task_specific_2 = df_creatures_data["Task Specific 2"].tolist()

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

st.markdown(
    "<div style='text-align: center; font-size: 24px; font-weight: normal;'>"
    "Welcome to Symphonia! Let's start our Creature Concerto."
    "</div>", 
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# 📂 Retrieve Saved Playlist Section
with st.expander("**🗝️ Treasure Hunt: Tap to Find Your Saved Playlist**", expanded=False):
    # Full-width label
    st.write("Enter your 1-word Playlist Code to load your saved playlist:")

    # Narrow input field only
    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust to control width
    with col2:
        entered_code = st.text_input(label=" ", label_visibility="collapsed").strip().lower()

    # Define the directory where playlists are saved
    playlist_dir = "saved_user_playlists"

    if entered_code:
        # Case-insensitive match
        matching_files = [
            f for f in os.listdir(playlist_dir)
            if f.lower().endswith(f"{entered_code}.csv")
        ]

        if matching_files:
            playlist_file = matching_files[0]
            filepath = os.path.join(playlist_dir, playlist_file)

            # Load the playlist into session state
            retrieved_df = pd.read_csv(filepath)
            st.session_state.user_playlist = retrieved_df.to_dict(orient="records")

            # Extract playlist name from filename
            playlist_base_name = playlist_file.rsplit("_", 1)[0].replace("_", " ")

            # Store in session state
            st.session_state.saved_playlist_name = playlist_base_name

            st.success(f"🪄 Your playlist was summoned! Let's keep building your playlist.")

            # 🎶 Display Playlist
            if "saved_playlist_name" in st.session_state:
                st.markdown(f"#### 🎶 Your Playlist: **{st.session_state.saved_playlist_name}**")
            else:
                st.subheader("🎶 Your Playlist")

            if st.session_state.user_playlist:
                for song in st.session_state.user_playlist:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(song["Image"], width=80)
                    with col2:
                        st.write(f"**{song['Name']}** by {song['Artist']}")
                        st.markdown(f"**Tempo:** {song['Tempo (BPM)']} BPM &nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp; **Loudness:** {song['Loudness (dB)']} dB")

                # 🎥 Toggle YouTube Embed Section
                show_youtube = st.checkbox("📺 Show YouTube Playlist", value=False)

                if show_youtube:
                    st.subheader("🎧 Listen to your playlist on YouTube")

                    if "youtube_video_ids" not in st.session_state:
                        st.session_state.youtube_video_ids = []

                    new_video_ids = [
                        song["YouTube Video ID"]
                        for song in st.session_state.user_playlist
                        if pd.notna(song.get("YouTube Video ID"))
                    ]

                    if set(new_video_ids) != set(st.session_state.youtube_video_ids):
                        st.session_state.youtube_video_ids = new_video_ids

                    if st.session_state.youtube_video_ids:
                        if len(st.session_state.youtube_video_ids) == 1:
                            youtube_embed_url = f"https://www.youtube.com/embed/{st.session_state.youtube_video_ids[0]}"
                        else:
                            first_video = st.session_state.youtube_video_ids[0]
                            playlist_videos = ",".join(st.session_state.youtube_video_ids)
                            youtube_embed_url = f"https://www.youtube.com/embed/{first_video}?playlist={playlist_videos}"

                        st.markdown(
                            f'<iframe width="100%" height="400" src="{youtube_embed_url}" frameborder="0" allowfullscreen></iframe>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("⚠️ No YouTube videos available for your playlist.")
        else:
            st.error("❌ No playlist found with that code. Please double-check and try again.")

st.header("🎚️ Metronome Master")
# 🎼 Show relatable response only after the user enters BPM

# 🎵 Ask for BPM input (default None)

# Full-width prompt with inline-block container
st.markdown(
    """
    <div style='margin-bottom: 0.5rem; font-weight: 500; font-size: 1rem;'>
        Enter the BPM (Beats Per Minute) of your song (40–250):
    </div>
    """,
    unsafe_allow_html=True
)

# Create a unique key that changes when we want to reset
reset_counter = st.session_state.get("reset_counter", 0)

# Centered number input with dynamic key
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    bpm = st.number_input(
        label=" ",
        min_value=40,
        max_value=250,
        value=None,
        step=1,
        format="%d",
        label_visibility="collapsed",
        key=f"bpm_input_{reset_counter}"  # Dynamic key
    )

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
def generate_drum_beat(bpm, duration=20, sample_rate=44100):
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
    if st.button("🥁 Play Your Tempo as a Drum Loop", type="primary"):
        drum_beat = generate_drum_beat(bpm)
        sf.write("drum_beat.wav", drum_beat, 44100)
        st.audio("drum_beat.wav")


# 🔊 Section: Loudness Analysis
st.header("🔊 Volume Virtuoso")

# 🎧 Ask for Loudness input (default None)

# Full-width prompt with a small gap below
st.markdown(
    """
    <div style='margin-bottom: 0.5rem; font-weight: 500; font-size: 1rem;'>
        Enter the relative loudness of your song (in dB, between -60 and 0):
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    loudness = st.number_input(
        label=" ",
        min_value=-60,
        max_value=0,
        value=None,
        step=1,
        format="%d",
        label_visibility="collapsed",
        key=f"loudness_input_{reset_counter}"  # Dynamic key
    )

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
def generate_drum_beat(bpm, duration=20, sample_rate=44100):
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

# 🎚️🔊 Combined Input Section - Fantasy themed
st.markdown(
    """
    <div style='
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 30px;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 3px solid #f39c12;
        position: relative;
    '>
        <div style='
            position: absolute;
            top: -10px;
            left: 20px;
            background: #f39c12;
            color: #2c3e50;
            padding: 5px 15px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 14px;
        '>MUSICAL QUEST</div>
        <h2 style='color: #f39c12; text-align: center; margin-bottom: 25px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>🎚️ Metronome Master & 🔊 Volume Virtuoso</h2>
        <div style='display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;'>
            <div style='flex: 1; min-width: 300px;'>
                <h3 style='color: #ecf0f1; text-align: center; margin-bottom: 10px;'>🎚️ Tempo Discovery</h3>
                <p style='color: #bdc3c7; text-align: center; font-size: 14px; margin-bottom: 15px;'>
                    Enter the BPM (Beats Per Minute) of your song (40–250):
                </p>
            </div>
            <div style='flex: 1; min-width: 300px;'>
                <h3 style='color: #ecf0f1; text-align: center; margin-bottom: 10px;'>🔊 Volume Analysis</h3>
                <p style='color: #bdc3c7; text-align: center; font-size: 14px; margin-bottom: 15px;'>
                    Enter the relative loudness of your song (in dB, between -60 and 0):
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Create a unique key that changes when we want to reset
reset_counter = st.session_state.get("reset_counter", 0)

# Two-column layout for inputs
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h4 style='text-align: center;'>🎚️ BPM Input</h4>", unsafe_allow_html=True)
    bpm = st.number_input(
        label=" ",
        min_value=40,
        max_value=250,
        value=None,
        step=1,
        format="%d",
        label_visibility="collapsed",
        key=f"bpm_input_{reset_counter}"
    )
    
    # BPM response text
    if bpm is not None:
        if bpm < 60:
            st.write("**Super chill** 🧘‍♀️ - perfect for relaxation")
        elif bpm < 90:
            st.write("**Laid-back groove** 🎷 - smooth vibes")
        elif bpm < 120:
            st.write("**Mid-tempo** 💃 - good dance beat!")
        elif bpm < 150:
            st.write("**Fast-paced** 🏃‍♂️ - workout energy!")
        else:
            st.write("**Ultra-fast** ⚡ - extreme beats!")
    
    # Drum beat button
    if bpm is not None:
        if st.button("🥁 Play Drum Loop", type="primary", key="drum_button"):
            drum_beat = generate_drum_beat(bpm)
            sf.write("drum_beat.wav", drum_beat, 44100)
            st.audio("drum_beat.wav")

with col2:
    st.markdown("<h4 style='text-align: center;'>🔊 Loudness Input</h4>", unsafe_allow_html=True)
    loudness = st.number_input(
        label=" ",
        min_value=-60,
        max_value=0,
        value=None,
        step=1,
        format="%d",
        label_visibility="collapsed",
        key=f"loudness_input_{reset_counter}"
    )
    
    # Loudness response text
    if loudness is not None:
        if loudness < -40:
            st.write("**Super quiet** 🤫 - peaceful vibes")
        elif loudness < -25:
            st.write("**Soft & gentle** 🌙 - calm melodies")
        elif loudness < -15:
            st.write("**Moderate** 🎵 - balanced energy")
        elif loudness < -5:
            st.write("**Fairly loud** 🎉 - dynamic & exciting")
        else:
            st.write("**Max loudness** 🔥 - club-ready!")

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

    # 👉 Wait for user to trigger matching with a button
    if st.button("🔮 Reveal the Musical Match", type="primary"):
        if not df_tracks.empty:
            df_tracks["Tempo Difference"] = abs(df_tracks["Tempo (BPM)"] - bpm)
            df_tracks["Loudness Difference"] = abs(df_tracks["Loudness (dB)"] - loudness)
            df_tracks["Match Score"] = df_tracks["Tempo Difference"] + df_tracks["Loudness Difference"]

            best_match = df_tracks.loc[df_tracks["Match Score"].idxmin()]
            st.session_state.best_match = best_match.to_dict()

def find_matching_creatures_either(tempo, loudness, df):
    matched = []

    def parse_range(r):
        try:
            return tuple(map(int, r.split(" - ")))
        except:
            return (None, None)

    for _, row in df.iterrows():
        tempo_low, tempo_high = parse_range(row["Tempo Preference"])
        loud_low, loud_high = parse_range(row["Loudness Preference"])

        tempo_match = (
            tempo_low is not None and tempo_high is not None and tempo_low <= tempo <= tempo_high
        )
        loudness_match = (
            loud_low is not None and loud_high is not None and loud_low <= loudness <= loud_high
        )

        if tempo_match or loudness_match:
            matched.append(row)

    return matched

# 🪄 Display best match if it's stored in session
if "best_match" in st.session_state:
    best_match = st.session_state.best_match

    st.subheader(f"🎵 Your song is **{best_match['Name']}** by **{best_match['Bard']}**")
    col1, spacer, col2 = st.columns([1, 0.5, 1])

    with col1:
        st.image(best_match["Image"], caption=best_match["Name"], width=250)

    with col2:
        st.write(f"🎚️ **BPM:** {best_match['Tempo (BPM)']}")
        st.write(f"🔊 **Loudness:** {best_match['Loudness (dB)']} dB")

    # 🎥 Embed YouTube video if available
    if pd.notna(best_match["YouTube Video ID"]):
        youtube_embed_url = f"https://www.youtube.com/embed/{best_match['YouTube Video ID']}"
        st.video(youtube_embed_url)
    else:
        st.write("⚠️ No YouTube video available for this track.")
    
    # Matching with creatures
    matched_creatures = find_matching_creatures_either(
        best_match["Tempo (BPM)"], best_match["Loudness (dB)"], df_creatures_data
    )

    # 🧠 Creature selection dropdown
    selected_creature_name = "-- Select Creature --"
    if matched_creatures:
        st.markdown("### This song activates the following creatures. Which one did you pair up in the game?")

        creature_names = ["-- Select Creature --"] + [creature["Name"] for creature in matched_creatures]

        selected_creature_name = st.selectbox(
            "Select your paired creature:",
            creature_names,
            index=0,
            key="creature_pair_selection"
        )

        if selected_creature_name != "-- Select Creature --":
            selected_creature_obj = next(
                (creature for creature in matched_creatures if creature["Name"] == selected_creature_name),
                None
            )

            if selected_creature_obj is not None:
                st.markdown(f"### Which music task would you like {selected_creature_obj['Name']} to complete?")

                music_tasks = [
                    "-- Select Task --",
                    selected_creature_obj["Task Specific 1"],
                    selected_creature_obj["Task Specific 2"]
                ]

                selected_task = st.selectbox(
                    "Choose a music task:",
                    music_tasks,
                    index=0,
                    key="music_task_selection"
                )

    # ➕ Add Song to Playlist Button
    if "user_playlist" not in st.session_state:
        st.session_state.user_playlist = []

    selected_creature_name = st.session_state.get("creature_pair_selection", "-- Select Creature --")
    selected_task = st.session_state.get("music_task_selection", "-- Select Task --")

    # ✅ Only show button *after* a task has been selected
    if selected_creature_name != "-- Select Creature --" and selected_task != "-- Select Task --":
        if st.button("✨ Add to Playlist", key=f"add_{best_match['Track ID']}", type="primary"):        
            # Build song object with context
            song_with_context = best_match.copy()
            song_with_context["Creature"] = selected_creature_name if selected_creature_name != "-- Select Creature --" else ""
            song_with_context["Task Selected"] = selected_task if selected_task != "-- Select Task --" else ""

            # Add task category if available
            selected_creature_obj = next(
                (creature for creature in matched_creatures if creature["Name"] == selected_creature_name),
                None
            )
            if selected_creature_obj is not None:
                song_with_context["Task Category"] = selected_creature_obj["Task Category"]
            else:
                song_with_context["Task Category"] = ""

            # Avoid duplicates
            track_ids = [song["Track ID"] for song in st.session_state.user_playlist]
            if best_match["Track ID"] not in track_ids:
                st.session_state.user_playlist.append(song_with_context)
                
                # Increment reset counter to create new widget keys
                st.session_state.reset_counter = st.session_state.get("reset_counter", 0) + 1
                
                # Clear creature and task selections for next song
                if "creature_pair_selection" in st.session_state:
                    del st.session_state.creature_pair_selection
                if "music_task_selection" in st.session_state:
                    del st.session_state.music_task_selection
                
                # Clear the best match so user needs to make a new match
                if "best_match" in st.session_state:
                    del st.session_state.best_match
                    
                # Force a rerun to reset the inputs
                st.rerun()
            else:
                st.warning("⚠️ This song is already in your playlist!")

# 🎵 MOVED OUTSIDE: Display Playlist (always show if playlist exists)
if st.session_state.user_playlist:
    st.subheader(f"🎶 Your Playlist: {st.session_state.get('saved_playlist_name', '')}".strip())
    
    for idx, song in enumerate(st.session_state.user_playlist):
        col1, col2, col3 = st.columns([1, 3, 1])  # Third column for the button

        with col1:
            st.image(song["Image"], width=80)

        with col2:
            st.write(f"**{song['Name']}** by {song['Bard']}")
            st.markdown(
                f"**Tempo:** {song['Tempo (BPM)']} BPM &nbsp;&nbsp;&nbsp;&nbsp; | "
                f"&nbsp;&nbsp;&nbsp;&nbsp; **Loudness:** {song['Loudness (dB)']} dB"
            )

        with col3:
            st.markdown("<div style='margin-top: 1.5em;'></div>", unsafe_allow_html=True)
            st.button("🧹 Remove", key=f"remove_{idx}", type="primary",
                    on_click=remove_song, args=(idx,))
else:
    st.write("📜 Your playlist scroll is blank. Add songs to bring Symphonia to life!")

# 🎼 Display Playlist Table Summary (also moved outside)
if st.session_state.user_playlist:
    playlist_summary_df = pd.DataFrame([{
        "Bard": song.get("Bard", "Unknown"),
        "Song Name": song.get("Name", "Unknown"),
        "Tempo(BPM)": song.get("Tempo (BPM)", ""),
        "Loudness(dB)": song.get("Loudness (dB)", ""),
        "Creature": song.get("Creature", ""),
        "Task Category": song.get("Task Category", ""),
        "Task Selected": song.get("Task Selected", "")
    } for idx, song in enumerate(st.session_state.user_playlist)])

    st.markdown("### 📋 Playlist Table")
    
    # Inject CSS to widen the table only
    st.markdown(
        """
        <style>
        /* Target the most recent .stDataFrame rendered */
        .element-container:has(.stDataFrame) {
            max-width: 1400px !important;
            width: 100% !important;
        }
        .stDataFrame table {
            min-width: 1400px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        playlist_summary_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

# 🎥 Embed YouTube playlist (also moved outside)
if st.session_state.user_playlist:
    st.subheader("🎧 Listen to your playlist on YouTube")
    if "youtube_video_ids" not in st.session_state:
        st.session_state.youtube_video_ids = []

    new_video_ids = [song["YouTube Video ID"] for song in st.session_state.user_playlist if pd.notna(song["YouTube Video ID"])]
    if set(new_video_ids) != set(st.session_state.youtube_video_ids):
        st.session_state.youtube_video_ids = new_video_ids

    if st.session_state.youtube_video_ids:
        if len(st.session_state.youtube_video_ids) == 1:
            youtube_embed_url = f"https://www.youtube.com/embed/{st.session_state.youtube_video_ids[0]}"
        else:
            first_video = st.session_state.youtube_video_ids[0]
            playlist_videos = ",".join(st.session_state.youtube_video_ids)
            youtube_embed_url = f"https://www.youtube.com/embed/{first_video}?playlist={playlist_videos}"

        st.markdown(
            f'<iframe width="100%" height="400" src="{youtube_embed_url}" frameborder="0" allowfullscreen></iframe>',
            unsafe_allow_html=True
        )
    else:
        st.write("⚠️ No YouTube videos available for your playlist.")
else:
    st.write("⚠️ No YouTube videos available for your playlist.")

# Ensure 'saved_user_playlists' directory exists
playlist_dir = "saved_user_playlists"
os.makedirs(playlist_dir, exist_ok=True)

# Word list for playlist code generation
word_choices = [
    "Graph", "Tempo", "Volume", "Loud", "Soft", "Fast", "Slow", "Numeric", "Data",
    "Creature", "Bard", "Village", "Journal", "Game", "Adventure", "Visualize",
    "Activate", "Concert", "Music", "Band", "Quartet", "Trio"
]

# 📝 Save Playlist Section
if st.session_state.user_playlist:
    st.markdown("---")
    st.subheader("📝 Save Your Playlist")

    # Prompt user to enter a playlist name first
    playlist_name = st.text_input("Enter a name for your playlist:")

    if st.button("📝 Save Playlist", type="primary") and playlist_name:
        # Generate a unique, lowercase one-word playlist code
        base_word = random.choice(word_choices).lower()

        # Get all existing codes (case-insensitive)
        existing_codes = {
            f.rsplit("_", 1)[-1].replace(".csv", "").lower()
            for f in os.listdir(playlist_dir) if f.endswith(".csv")
        }

        # Initialize playlist code and ensure uniqueness
        playlist_code = base_word
        suffix = 1
        while playlist_code in existing_codes:
            playlist_code = f"{base_word}{suffix}"
            suffix += 1

        # Format the filename using the playlist name and unique code
        filename = f"{playlist_name.replace(' ', '_')}_{playlist_code}.csv"
        filepath = os.path.join(playlist_dir, filename)

        # Convert playlist to a DataFrame
        df_playlist = pd.DataFrame(st.session_state.user_playlist)
        df_playlist.to_csv(filepath, index=False)

        # Set expiration date (2 weeks from now)
        expiration_date = datetime.now() + timedelta(weeks=2)
        meta_filepath = os.path.join(playlist_dir, f"{filename}.meta")
        with open(meta_filepath, "w") as meta_file:
            meta_file.write(expiration_date.strftime("%Y-%m-%d %H:%M:%S"))

        # 🎉 Confirm to the user that their playlist has been saved
        st.success(f"📜 Playlist '{playlist_name}' has been inscribed in the archives.")
        st.info(f"🪄 **Your Playlist Code:**\n\n### `{playlist_code}`\n\nUse this code to summon your playlist again. The magic holds for **two weeks**.")


# 🗑️ Cleanup Function (Run Periodically)
def cleanup_old_playlists():
    now = datetime.now()
    for file in os.listdir(playlist_dir):
        if file.endswith(".meta"):
            meta_filepath = os.path.join(playlist_dir, file)
            with open(meta_filepath, "r") as meta_file:
                expiration_str = meta_file.read().strip()
                expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S")

                # If expired, delete the playlist and metadata
                if now > expiration_date:
                    playlist_csv = meta_filepath.replace(".meta", "")
                    os.remove(meta_filepath)
                    if os.path.exists(playlist_csv):
                        os.remove(playlist_csv)

cleanup_old_playlists()

# Ensure session state for playlist tracking
if "user_playlist" not in st.session_state:
    st.session_state.user_playlist = []

# # Display full playlist analysis button only if at least one song is added
# if len(st.session_state.user_playlist) > 0:
#     # st.markdown("✅ **You’ve added at least one song to your playlist!** Now, you can explore the full playlist analysis.")
#     # Encourage users to keep matching and adding songs
#     st.markdown(
#         "**Keep matching and adding more songs to your playlist!** "
#         "Once you're satisfied with your selections, explore the **full playlist analysis** below."
#     )

#     # Initialize session state variable to track visibility
#     if "show_playlist_analysis" not in st.session_state:
#         st.session_state.show_playlist_analysis = False

#     # Button to toggle display of playlist analysis
#     if st.button(
#         "📊 View Full Playlist Analysis" if not st.session_state.show_playlist_analysis else "🔽 Hide Playlist Analysis"
#     ):
#         st.session_state.show_playlist_analysis = not st.session_state.show_playlist_analysis

# def display_playlist_analysis():
#     """Displays the full playlist insights and analysis."""
    
#     st.markdown("### **🔍 Playlist Insights & Analysis**")
#     st.markdown("_Here's a deep dive into your playlist's characteristics, trends, and audio features._")

#     # Extract data from session state playlist
#     playlist_songs = st.session_state.user_playlist

#     # Construct DataFrame
#     data = {
#         "Image": [song["Image"] for song in playlist_songs],
#         "Name": [song["Name"] for song in playlist_songs],
#         "Artist": [song["Artist"] for song in playlist_songs],
#         "Genre": [song.get("Genre", "Unknown") for song in playlist_songs],
#         "Release Date": [song["Release Date"] for song in playlist_songs],
#         "Release Decade": [song["Decade"] for song in playlist_songs],
#         "Popularity": [song["Popularity"] for song in playlist_songs],
#         "Duration": [song["Duration"] for song in playlist_songs],
#         "Acoustic": [song["Acousticness"] for song in playlist_songs],
#         "Dance": [song["Danceability"] for song in playlist_songs],
#         "Energy": [song["Energy"] for song in playlist_songs],
#         "Happy": [song["Happiness"] for song in playlist_songs],
#         "Instrumental": [song["Instrumentalness"] for song in playlist_songs],
#         "Key": [song["Key"] for song in playlist_songs],
#         "Live": [song["Liveness"] for song in playlist_songs],
#         "Loud (Db)": [song["Loudness (dB)"] for song in playlist_songs],
#         "Speech": [song["Speechiness"] for song in playlist_songs],
#         "Tempo": [song["Tempo (BPM)"] for song in playlist_songs],
#     }

#     df = pd.DataFrame(data)
#     df.index += 1  # Start index at 1
#     num_total_tracks = len(df)

#     # Inform users about table interactivity
#     st.write(
#         "📋 The table below is **scrollable** both horizontally and vertically. "
#         "Click on column headers to **sort** and **hover** for explanations."
#     )

#     # Display the playlist analysis table with sorting and image preview
#     st.data_editor(
#         df,
#         column_config={
#             "Image": st.column_config.ImageColumn(
#                 "Album Art", help="Click on the album cover to enlarge"
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
#             "Release Decade": st.column_config.TextColumn(
#                 "Release Decade", help="The decade when the track or album was released"
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

#     # 🎥 YouTube Dropdown for Playing Playlist Songs
#     song_options = [song["Name"] for song in st.session_state.user_playlist]

#     if song_options:
#         selected_song = st.selectbox(
#             "🎥 Choose a song from your playlist to play on YouTube:",
#             options=song_options
#         )

#         # Attempt to find a corresponding YouTube video
#         matched_video = None
#         for video in videos:
#             if selected_song.lower() in video["title"].lower():
#                 matched_video = video
#                 break  # Stop searching after first match

#         if matched_video:
#             selected_video_url = matched_video["url"]
#             youtube_video_id = selected_video_url.split("v=")[-1].split("&")[0]

#             # Embed the selected YouTube video
#             youtube_embed_html = f"""
#             <iframe width="100%" height="350" src="https://www.youtube.com/embed/{youtube_video_id}" 
#             frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
#             allowfullscreen></iframe>
#             """
#             st.markdown(youtube_embed_html, unsafe_allow_html=True)
#         else:
#             st.write(f"⚠️ No YouTube video found for **{selected_song}**. Playing YouTube playlist instead.")

#        # Add some spacing
#     st.markdown("<br><br>", unsafe_allow_html=True)

#     # 🎼 Features to choose from in the dropdown
#     features = ["Popularity", "Duration", "Acoustic", "Dance", "Energy", "Happy", "Instrumental", "Key", "Live", "Loud (Db)", "Speech", "Tempo"]
#     features_with_descriptions = [
#         "Popularity: The popularity score of the track (0 to 100)",
#         "Duration: The duration of the track",
#         "Acoustic: A measure of the acoustic quality of the track (0 to 1)",
#         "Dance: How suitable the track is for dancing (0 to 1)",
#         "Energy: The intensity and activity level of the track (0 to 1)",
#         "Happy: A measure of the musical positivity of the track (0 to 1)",
#         "Instrumental: The likelihood that the track is instrumental (0 to 1)",
#         "Key: The musical key the track is composed in (0 to 11)",
#         "Live: The probability that the track was performed live (0 to 1)",
#         "Loud (Db): The overall loudness of the track in decibels",
#         "Speech: The presence of spoken words in the track (0 to 1)",
#         "Tempo: The tempo of the track in beats per minute (BPM)"
#     ]

#     selected_feature_with_description = st.selectbox("🔢 Select an audio feature to rank tracks by:", features_with_descriptions)
    
#     # Extract the feature name from the selected option (before the colon)
#     selected_feature = selected_feature_with_description.split(":")[0]

#     # 🎚️ Number of tracks to display in ranking
#     num_tracks = st.slider(f"🎼 How many tracks do you want to display?", min_value=1, max_value=num_total_tracks, value=3)

#     # 🎵 Display Top & Lowest Tracks by Feature
#     sorted_df = df.sort_values(by=selected_feature, ascending=False)
#     st.write(f"### 🎖️ Top {num_tracks} Tracks by {selected_feature}")
#     st.dataframe(sorted_df.head(num_tracks)[["Name", "Artist", selected_feature]], hide_index=True)

#     sorted_df_ascending = df.sort_values(by=selected_feature, ascending=True)
#     st.write(f"### 🛑 Lowest {num_tracks} Tracks by {selected_feature}")
#     st.dataframe(sorted_df_ascending.head(num_tracks)[["Name", "Artist", selected_feature]], hide_index=True)

#     # # 🎭 **Genre Distribution Analysis**
#     # if "Genre" in df.columns:
#     #     st.write("### 🎭 Main Genres of Songs in Your Playlist")

#     #     # Convert genres to DataFrame
#     #     df_genres = pd.DataFrame(df["Genre"], columns=["Genre"])

#     #     # Count occurrences of each genre
#     #     genre_counts = df_genres["Genre"].value_counts()

#     #     # Calculate percentage of each genre
#     #     genre_percentages = (genre_counts / genre_counts.sum()) * 100

#     #     # Sort genres by percentage in descending order
#     #     genre_percentages_sorted = genre_percentages.sort_values(ascending=False)

#     #     # Calculate the cumulative sum and filter to include genres up to 80% of total
#     #     cumulative_percentages = genre_percentages_sorted.cumsum()
#     #     top_genres_80 = genre_percentages_sorted[cumulative_percentages <= 80]

#     #     # **Fix: Convert Series to DataFrame explicitly**
#     #     df_top_genres = pd.DataFrame({
#     #         "Genre": top_genres_80.index,
#     #         "Percentage": top_genres_80.values
#     #     })

#     #     # 🎨 Create a colorful horizontal bar chart using Plotly
#     #     fig_genres = px.bar(
#     #         df_top_genres,  # Use correctly formatted DataFrame
#     #         x="Percentage",
#     #         y="Genre",
#     #         orientation="h",  # Horizontal bar chart
#     #         labels={"Percentage": "Percentage of Songs (%)", "Genre": "Genres"},
#     #         color="Genre",  # Use genre names for color categories
#     #         color_discrete_sequence=px.colors.qualitative.Set3  # Use a qualitative color palette
#     #     )

#     #     # Customize hovertemplate to show only the percentage
#     #     fig_genres.update_traces(hovertemplate='%{x:.1f}%<extra></extra>')

#     #     # Customize the bar chart appearance
#     #     fig_genres.update_layout(
#     #         xaxis_title="Percentage of Songs (%)",
#     #         yaxis_title="Genres",
#     #         xaxis=dict(range=[0, 100]),  # Ensure range is 0-100%
#     #         margin=dict(t=0),  # Remove top margin
#     #         showlegend=False
#     #     )

#     #     # Display the bar chart in Streamlit
#     #     st.plotly_chart(fig_genres)

#     # Create DataFrame from the constructed 'data' dictionary
#     df_playlist = pd.DataFrame(data)

#     # Extract "Name" and "Release Decade" for decade analysis
#     df_decades = df_playlist[['Name', 'Release Decade']].copy()

#     # Calculate the percentage of songs in each decade
#     decade_counts = df_decades['Release Decade'].value_counts(normalize=True) * 100

#     # Sort decades in chronological order
#     decade_counts = decade_counts.sort_index()

#     # Create a DataFrame for visualization
#     df_bins_decades = pd.DataFrame({
#         'Decade': decade_counts.index,
#         'Percentage': decade_counts.values
#     })

#     # Create a vertical bar chart using Plotly
#     fig_decades = go.Figure(go.Bar(
#         x=df_bins_decades['Decade'],  # The decade categories
#         y=df_bins_decades['Percentage'],  # The percentages
#         text=[f"{perc:.1f}%" for perc in df_bins_decades['Percentage']],  # Display percentages as text inside the bars
#         textposition='auto',  # Position text inside bars
#         marker=dict(
#             color=px.colors.qualitative.Plotly  # Automatically assign colors
#         )
#     ))

#     # Update layout for better visualization
#     fig_decades.update_layout(
#         title_text='Percentage of Songs by Decade',
#         xaxis_title='Decade',
#         yaxis_title='Percentage of Songs (%)',
#         yaxis=dict(tickvals=[0, 20, 40, 60, 80, 100]),  # Custom y-axis ticks
#         showlegend=False  # Hide legend
#     )

#     # Count occurrences of each genre
#     genre_counts = df["Genre"].value_counts()

#     # Calculate the percentage for each genre
#     genre_percentages = (genre_counts / genre_counts.sum()) * 100

#     # Sort genres by percentage in descending order
#     genre_percentages_sorted = genre_percentages.sort_values(ascending=False)

#     # If no genre data is available
#     if genre_percentages_sorted.empty:
#         st.warning("⚠️ No genre data available to display.")

#     # If only one genre is in the playlist
#     elif len(genre_percentages_sorted) == 1:
#         st.write("### 🎶 Genre of the Song in Your Playlist")
#         genre = genre_percentages_sorted.index[0]
#         percent = genre_percentages_sorted.iloc[0]
#         st.write(f"Your song is categorized as **{genre}**, which makes up **{percent:.2f}%** of your playlist.")

#     # If multiple genres, show the top contributors to 80%
#     else:
#         cumulative_percentages = genre_percentages_sorted.cumsum()
#         top_genres_80 = genre_percentages_sorted[cumulative_percentages <= 80]

#     if len(top_genres_80) == 0:
#         top_genres_80 = genre_percentages_sorted.head(5)

#     # Create DataFrame for plotting
#     df_top_genres = pd.DataFrame({
#         "Genre": top_genres_80.index.tolist(),
#         "Percentage": top_genres_80.values.tolist()
#     })

#     st.write("### 🎶 Main Genres of Songs in Your Playlist")

#     fig = px.bar(
#         df_top_genres,
#         x="Percentage",
#         y="Genre",
#         orientation='h',
#         labels={"Percentage": "Percentage of Songs (%)", "Genre": "Genres"},
#     )

#     fig.update_traces(hovertemplate='%{x:.2f}%<extra></extra>')
#     fig.update_layout(
#         xaxis_title="Percentage of Songs (%)",
#         yaxis_title="Genres",
#         xaxis=dict(range=[0, 100]),
#         margin=dict(t=0)
#     )

#     st.plotly_chart(fig)

# # 📌 Call the function **after** the button logic
# if st.session_state.get("show_playlist_analysis", False):
#     display_playlist_analysis() 


