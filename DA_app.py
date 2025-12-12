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

import uuid
import json

# --- SESSION PERSISTENCE SETUP ---
# Create a folder to store temporary session files
SESSION_DIR = "temp_user_sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

# 1. Get Session ID from URL or Generate New One
if "session_id" not in st.query_params:
    # Generate a unique ID
    new_id = str(uuid.uuid4())
    st.query_params["session_id"] = new_id
    session_id = new_id
else:
    session_id = st.query_params["session_id"]

# Define the file path for this specific user
session_file_path = os.path.join(SESSION_DIR, f"{session_id}.json")

# 2. Define Helper Functions for Auto-Saving/Loading
def auto_save_session():
    """Saves the current playlist to a JSON file linked to the session ID."""
    state_data = {
        "user_playlist": st.session_state.get("user_playlist", []),
        "saved_playlist_name": st.session_state.get("saved_playlist_name", "")
    }
    with open(session_file_path, "w") as f:
        json.dump(state_data, f)

def auto_load_session():
    """Loads the playlist from file if session_state is empty but file exists."""
    if os.path.exists(session_file_path) and not st.session_state.get("user_playlist"):
        try:
            with open(session_file_path, "r") as f:
                data = json.load(f)
                st.session_state.user_playlist = data.get("user_playlist", [])
                st.session_state.saved_playlist_name = data.get("saved_playlist_name", "")
        except:
            pass # If file is corrupt, just start fresh

# 3. Trigger Load on App Startup
if "user_playlist" not in st.session_state:
    st.session_state.user_playlist = []
auto_load_session()

def get_img_base64(img_path):
    """Encodes a local image file or remote URL to base64 for Plotly."""
    # Check if it's a URL
    if img_path and img_path.startswith(('http://', 'https://')):
        try:
            response = requests.get(img_path, timeout=5)
            if response.status_code == 200:
                encoded = base64.b64encode(response.content).decode()
                # Determine extension from URL
                ext = img_path.split('.')[-1].lower()
                if ext not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                    ext = 'png'  # Default to png
                return f"data:image/{ext};base64,{encoded}"
        except Exception as e:
            pass  # Fall through to return None
        return None
    # Otherwise, check for local file
    elif img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        ext = os.path.splitext(img_path)[1].replace(".", "")
        return f"data:image/{ext};base64,{encoded}"
    return None

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
        auto_save_session()  # <--- Add this line

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
    track_bard_image = df_audio_features["Bard Image"].tolist()
    track_bard_symbol = df_audio_features["Bard Symbol"].tolist()
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
        "Bard Image": track_bard_image,
        "Bard Symbol": track_bard_symbol,
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
    creatures_csv = "DA Creatures 2.csv"
    df_creatures_data = pd.read_csv(creatures_csv)

    # Extract individual creature attributes
    creature_names = df_creatures_data["Creature name"].tolist()
    creature_tempo_preferences = df_creatures_data["Tempo Preference"].tolist()
    creature_loudness_preferences = df_creatures_data["Loudness Preference"].tolist()
    creature_task_categories = df_creatures_data["Task Category"].tolist()
    creature_task_specific_1 = df_creatures_data["Task Specific 1"].tolist()
    creature_task_specific_2 = df_creatures_data["Task Specific 2"].tolist()
    creature_image = df_creatures_data["Creature Image"].tolist()

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

            auto_save_session()

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
                        st.image(song["Bard Image"], width=80)
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

# 🎼 Show relatable response only after the user enters loudness
if loudness is not None:
    if loudness < -50:
        st.write("This is **super quiet**! Like a ghost whispering or leaves rustling in the wind.")
    elif loudness < -40:
        st.write("This is **very quiet**. Like studying in a library or whispering to a friend.")
    elif loudness < -30:
        st.write("This is **quiet**. Chill vibes, like background music while you do homework.")
    elif loudness < -20:
        st.write("This is **medium volume**. Like a normal conversation or a singer with an acoustic guitar.")
    elif loudness < -10:
        st.write("This is **loud**! Like a busy cafeteria or your favorite pop song on the radio.")
    elif loudness < -5:
        st.write("This is **really loud**! Like a school assembly or a marching band passing by.")
    else:
        st.write("**Max volume!** Like a rock concert or a firework show—super intense!")


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
        st.image(best_match["Bard Image"], caption=best_match["Bard"], width=250)

    with col2:
        st.write(f"🎚️ **BPM:** {best_match['Tempo (BPM)']}")
        st.write(f"🔊 **Loudness:** {best_match['Loudness (dB)']} dB")

    # --- Single Song Waveform Visualization ---

    # Load Waveform Data (Global load, usually done once but fine here for safety)
    waveform_db = {}
    if os.path.exists("song_waveforms.json"):
        with open("song_waveforms.json", "r") as f:
            waveform_db = json.load(f)
            
    # Check if we have data for THIS song
    song_name = best_match["Name"]
    db_values = waveform_db.get(song_name)
    
    if db_values:
        st.markdown("#### 🌊 Audio Waveform")
        
        # Calculate visual parameters
        raw_dur = best_match.get("Duration", 0)
        try:
            # Handle "MM:SS" format (e.g., "2:45")
            if isinstance(raw_dur, str) and ":" in raw_dur:
                parts = raw_dur.split(":")
                duration_sec = int(parts[0]) * 60 + int(parts[1])
            # Handle milliseconds (numeric)
            else:
                duration_sec = float(raw_dur) / 1000
        except:
            duration_sec = 0

        x_axis = np.linspace(0, duration_sec, len(db_values))
        
        # Rectified Waveform (0 to 1 scale)
        y_values = [max(0, db + 60) for db in db_values]
        
        fig_wave = go.Figure()
        
        # The Waveform
        fig_wave.add_trace(go.Scatter(
            x=x_axis,
            y=y_values,
            fill='tozeroy',
            fillcolor='#AD98B0', # Lavender
            line=dict(color='#AD98B0', width=1.5),
            opacity=0.9,
            name=song_name,
            hoverinfo="x+text",
            text=[f"{db} dB" for db in db_values]
        ))
        
        # Average Loudness Line
        avg_loudness = best_match["Loudness (dB)"]
        avg_y = avg_loudness + 60
        
        fig_wave.add_trace(go.Scatter(
            x=[0, duration_sec],
            y=[avg_y, avg_y],
            mode='lines',
            line=dict(color='#FF5F1F', width=3), # Neon Orange
            name="Average Loudness",
            hoverinfo="name+text",
            text=[f"{avg_loudness} dB"]*2
        ))
        
        fig_wave.update_layout(
            xaxis=dict(title="Duration (s)", showgrid=False, zeroline=True, showticklabels=True),
            yaxis=dict(showgrid=False, showticklabels=False, range=[0, 65]),
            height=200, # Compact height
            margin=dict(l=10, r=10, t=10, b=10), # Tight margins
            plot_bgcolor='white',
            showlegend=False
        )
        st.plotly_chart(fig_wave, use_container_width=True)
        
    else:
        # Optional: Message if no data exists
        # st.caption("Waveform data not available for this track.")
        pass

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

    # 🧠 Creature selection logic
    # Initialize selection in session state if not present
    if "creature_pair_selection" not in st.session_state:
        st.session_state.creature_pair_selection = "-- Select Creature --"

    if matched_creatures:
        # Check if a selection has already been made
        if st.session_state.creature_pair_selection == "-- Select Creature --":
            # --- VIEW 1: SELECTION GRID (Visible when nothing is selected) ---
            st.markdown("### This song activates the following creatures. Which one did you pair up in the game?")
            
            cols_per_row = 3
            for i in range(0, len(matched_creatures), cols_per_row):
                cols = st.columns(cols_per_row)
                batch = matched_creatures[i:i + cols_per_row]
                
                for col, creature in zip(cols, batch):
                    with col:
                        st.markdown(f"**{creature['Creature name']}**")
                        try:
                            st.image(creature["Creature Image"], use_container_width=True)
                        except:
                            st.warning("No Image")
                        
                        # Selection Button
                        if st.button("Select", key=f"btn_{creature['Creature name']}", type="secondary", use_container_width=True):
                            st.session_state.creature_pair_selection = creature["Creature name"]
                            st.session_state.scroll_to_summary = True
                            st.rerun() # Rerun to collapse the grid
                st.markdown("<br>", unsafe_allow_html=True)

        else:
            # --- VIEW 2: SUMMARY VIEW (Visible after selection) ---
            # Anchor point for scrolling
            st.markdown('<div id="summary-section"></div>', unsafe_allow_html=True)

            # Check if we need to scroll
            if st.session_state.get("scroll_to_summary", False):
                 st.markdown(
                    """
                    <script>
                    setTimeout(function() {
                        var element = document.getElementById('summary-section');
                        if (element) {
                            var elementPosition = element.offsetTop;
                            var offsetPosition = elementPosition - 150; // Adjust offset as needed
                            window.scrollTo({
                                top: offsetPosition,
                                behavior: 'smooth'
                            });
                        }
                    }, 100);
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                 del st.session_state.scroll_to_summary

            # Find the selected object
            selected_creature_name = st.session_state.creature_pair_selection
            selected_creature_obj = next(
                (creature for creature in matched_creatures if creature["Creature name"] == selected_creature_name),
                None
            )

            if selected_creature_obj is not None:
                # Create a compact summary banner
                st.info(f"✅ You have selected **{selected_creature_name}**")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    try:
                        st.image(selected_creature_obj["Creature Image"], use_container_width=True)
                    except:
                        st.write("No Image")
                with col2:
                    # "Change Selection" Button
                    if st.button("🔄 Change Creature", type="secondary"):
                        # Reset selection to bring back the grid
                        st.session_state.creature_pair_selection = "-- Select Creature --"
                        st.session_state.music_task_selection = "-- Select Task --" # Reset task too
                        st.rerun()

                # --- SHOW TASK SELECTION (Only visible in Summary View) ---
                st.markdown("---")
                st.markdown(f"### Which music task would you like **{selected_creature_obj['Creature name']}** to complete?")
                
                if "music_task_selection" not in st.session_state:
                    st.session_state.music_task_selection = "-- Select Task --"
                
                if st.session_state.music_task_selection == "-- Select Task --":
                    # Task Selection Grid
                    col1, col2 = st.columns(2)
                    
                    # Task 1
                    with col1:
                        st.markdown(f"**{selected_creature_obj['Task Specific 1']}**")
                        try:
                            st.image(selected_creature_obj['Task 1 Image'], use_container_width=True)
                        except:
                            st.warning("No Image")
                        if st.button("Select", key="btn_task_1", type="secondary", use_container_width=True):
                            st.session_state.music_task_selection = selected_creature_obj["Task Specific 1"]
                            st.rerun()

                    # Task 2
                    with col2:
                        st.markdown(f"**{selected_creature_obj['Task Specific 2']}**")
                        try:
                            st.image(selected_creature_obj['Task 2 Image'], use_container_width=True)
                        except:
                            st.warning("No Image")
                        if st.button("Select", key="btn_task_2", type="secondary", use_container_width=True):
                            st.session_state.music_task_selection = selected_creature_obj["Task Specific 2"]
                            st.rerun()

                else:
                    # Selected Task Summary
                    st.info(f"✅ You have selected **{st.session_state.music_task_selection}**")
                    
                    # Determine which task was selected to show correct image
                    selected_task_name = st.session_state.music_task_selection
                    if selected_task_name == selected_creature_obj["Task Specific 1"]:
                         task_img = selected_creature_obj["Task 1 Image"]
                    else:
                         task_img = selected_creature_obj["Task 2 Image"]
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                         try:
                            st.image(task_img, use_container_width=True)
                         except:
                            st.write("No Image")
                    with col2:
                         if st.button("🔄 Change Task", type="secondary"):
                             st.session_state.music_task_selection = "-- Select Task --"
                             st.rerun()

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
                (creature for creature in matched_creatures if creature["Creature name"] == selected_creature_name),
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
                
                auto_save_session()

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

                # Set a flag to scroll to playlist after rerun
                st.session_state.scroll_to_playlist = True

                # Force a rerun to reset the inputs
                st.rerun()
            else:
                st.warning("⚠️ This song is already in your playlist!")

# 🎵 MOVED OUTSIDE: Display Playlist (always show if playlist exists)
if st.session_state.user_playlist:
    st.markdown("---")
    # Add an anchor point for scrolling
    st.markdown('<div id="playlist-section"></div>', unsafe_allow_html=True)
    st.subheader(f"🎶 Your Playlist: {st.session_state.get('saved_playlist_name', '')}".strip())

    # Check if we should scroll to playlist
    if st.session_state.get("scroll_to_playlist", False):
        # Add JavaScript to scroll to the playlist section
        st.markdown(
            """
            <script>
            setTimeout(function() {
                var element = document.getElementById('playlist-section');
                var elementPosition = element.offsetTop;
                var offsetPosition = elementPosition - 250; // Increased from 200 to 250
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }, 100);
            </script>
            """,
            unsafe_allow_html=True
        )
        # Clear the scroll flag
        del st.session_state.scroll_to_playlist
    
    for idx, song in enumerate(st.session_state.user_playlist):
        col1, col2, col3 = st.columns([1, 3, 1])  # Third column for the button

        with col1:
            st.image(song["Bard Image"], width=80)

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


# 🎼 Display Playlist Table Summary (also moved outside)
if st.session_state.user_playlist:
    playlist_summary_df = pd.DataFrame([{
        "Bard": song.get("Bard", "Unknown"),
        "Song Name": song.get("Name", "Unknown"),
        "Tempo(BPM)": song.get("Tempo (BPM)", ""),
        "Loudness(dB)": song.get("Loudness (dB)", ""),
        "Bard Symbol": song.get("Bard Symbol", ""),
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
        hide_index=True,
        column_config={
            "Bard Symbol": st.column_config.ImageColumn(
                "Bard Symbol",
                help="The bard's symbol",
                width="small"
            )
        }
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

# After the playlist table display, add a message about graph availability
if st.session_state.user_playlist:
    # ... existing playlist table code ...
    
    # st.dataframe(
    #     playlist_summary_df.reset_index(drop=True),
    #     use_container_width=True,
    #     hide_index=True
    # )
    
    # NEW: Add message about data visualization availability
    current_song_count = len(st.session_state.user_playlist)
    
    if current_song_count < 3:
        songs_needed = 3 - current_song_count
        st.info(
            f"📊 **Data Visualization Unlock:** Add {songs_needed} more song{'s' if songs_needed > 1 else ''} "
            f"to unlock graph and chart views of your playlist data! "
            f"({current_song_count}/3 songs added)"
        )
    else:
        st.success(
            f"🎉 **Data Visualization Unlocked!** You have {current_song_count} songs in your playlist. "
            "You can now view detailed graphs and charts of your playlist data!"
        )
        
        # Initialize session state variable to track visibility of data visualization
        if "show_data_visualization" not in st.session_state:
            st.session_state.show_data_visualization = False

        # Button to toggle display of data visualization
        if st.button(
            "📊 View Data" if not st.session_state.show_data_visualization else "🗺️ Hide Data Visualization",
            type="primary"
        ):
            st.session_state.show_data_visualization = not st.session_state.show_data_visualization

# Only show visualization if button was pressed and enough songs exist
if st.session_state.get("show_data_visualization", False) and len(st.session_state.user_playlist) >= 3:
    st.markdown("### **📊 Playlist Data Visualization**")
    st.markdown("_Here's a visual analysis of your playlist's tempo and loudness characteristics._")

    # Use existing playlist_summary_df if available, otherwise create minimal DataFrame
    if 'playlist_summary_df' in locals():
        viz_df = playlist_summary_df[["Song Name", "Bard", "Tempo(BPM)", "Loudness(dB)", "Bard Symbol"]].copy()
        viz_df.columns = ["Name", "Bard", "Tempo", "Loudness", "Symbol"]
    else:
        # Fallback: create minimal DataFrame
        viz_df = pd.DataFrame({
            "Name": [song["Name"] for song in st.session_state.user_playlist],
            "Bard": [song["Bard"] for song in st.session_state.user_playlist],
            "Tempo": [song["Tempo (BPM)"] for song in st.session_state.user_playlist],
            "Loudness": [song["Loudness (dB)"] for song in st.session_state.user_playlist],
            "Symbol": [song.get("Bard Symbol", "") for song in st.session_state.user_playlist],
        })
    
    # # Full-width Tempo Bar Chart
    # st.write("#### Tempo Distribution (BPM)")
    # fig_tempo = px.bar(
    #     viz_df, 
    #     x="Name", 
    #     y="Tempo", 
    #     color="Name",
    #     labels={"Tempo": "Tempo (BPM)", "Name": "Songs"},
    #     color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    # )
    # fig_tempo.update_layout(
    #     xaxis_title="Songs",
    #     yaxis_title="Tempo (BPM)",
    #     xaxis_tickangle=45, 
    #     margin=dict(t=0), 
    #     showlegend=False
    # )
    # fig_tempo.update_traces(hovertemplate='<b>%{x}</b><br>Tempo: %{y} BPM<extra></extra>')
    # st.plotly_chart(fig_tempo, use_container_width=True)
    
    # # Full-width Loudness Bar Chart  
    # st.write("#### Loudness Distribution (dB)")
    # # Convert loudness to positive values for upward bars
    # viz_df_loudness = viz_df.copy()
    # viz_df_loudness["Loudness_Positive"] = viz_df_loudness["Loudness"] * -1
    # fig_loudness = px.bar(
    #     viz_df_loudness, 
    #     x="Name", 
    #     y="Loudness_Positive", 
    #     color="Name",
    #     labels={"Loudness_Positive": "Loudness (dB)", "Name": "Songs"},
    #     color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    # )
    # fig_loudness.update_layout(
    #     xaxis_title="Songs",
    #     yaxis_title="Loudness (dB)",
    #     xaxis_tickangle=45, 
    #     margin=dict(t=0), 
    #     showlegend=False
    # )
    # fig_loudness.update_traces(hovertemplate='<b>%{x}</b><br>Loudness: %{y} dB<extra></extra>')
    # st.plotly_chart(fig_loudness, use_container_width=True)
    
    # --- TEMPO NUMBER LINE WITH IMAGES ---
    st.write("#### Tempo Number Line (BPM)")
    fig_tempo_line = go.Figure()

    # 1. The Line
    fig_tempo_line.add_trace(go.Scatter(
        x=[0, 200], y=[0, 0], 
        mode='lines',
        line=dict(color='lightgray', width=3),
        showlegend=False, hoverinfo='skip'
    ))

    # 2. Invisible markers for Hover Data
    fig_tempo_line.add_trace(go.Scatter(
        x=viz_df['Tempo'], 
        y=[0] * len(viz_df),
        mode='markers',
        marker=dict(size=20, opacity=0), # Invisible markers to catch hover events
        name="Songs",
        text=[f"<b>{row['Name']}</b><br>{row['Bard']}<br>{row['Tempo']} BPM" for _, row in viz_df.iterrows()],
        hovertemplate='%{text}<extra></extra>',
        showlegend=False
    ))

    # 3. Add Images as Layout Elements
    tempo_images = []
    for _, row in viz_df.iterrows():
        img_b64 = get_img_base64(row['Symbol'])
        if img_b64:
            tempo_images.append(dict(
                source=img_b64,
                xref="x", yref="y",
                x=row['Tempo'], y=0,
                sizex=15, sizey=0.3, # Adjust these values to scale the icons
                xanchor="center", yanchor="middle",
                layer="above"
            ))

    fig_tempo_line.update_layout(
        xaxis=dict(range=[-10, 210], title="Beats Per Minute (BPM)", showgrid=True, dtick=20),
        yaxis=dict(range=[-0.2, 0.2], showticklabels=False, showgrid=False, zeroline=False),
        height=200,
        images=tempo_images, # <--- Attach images here
        margin=dict(t=20, b=50, l=50, r=50),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_tempo_line, use_container_width=True)

    # --- LOUDNESS NUMBER LINE WITH IMAGES ---
    st.write("#### Loudness Number Line (dB)")
    fig_loudness_line = go.Figure()

    # 1. The Line
    fig_loudness_line.add_trace(go.Scatter(
        x=[-60, 0], y=[0, 0], 
        mode='lines',
        line=dict(color='lightgray', width=3),
        showlegend=False, hoverinfo='skip'
    ))

    # 2. Invisible markers for Hover Data
    fig_loudness_line.add_trace(go.Scatter(
        x=viz_df['Loudness'], 
        y=[0] * len(viz_df),
        mode='markers',
        marker=dict(size=20, opacity=0),
        name="Songs",
        text=[f"<b>{row['Name']}</b><br>{row['Bard']}<br>{row['Loudness']} dB" for _, row in viz_df.iterrows()],
        hovertemplate='%{text}<extra></extra>',
        showlegend=False
    ))

    # 3. Add Images as Layout Elements
    loudness_images = []
    for _, row in viz_df.iterrows():
        img_b64 = get_img_base64(row['Symbol'])
        if img_b64:
            loudness_images.append(dict(
                source=img_b64,
                xref="x", yref="y",
                x=row['Loudness'], y=0,
                sizex=4, sizey=0.3, # Note: sizex is smaller here because dB range is smaller (-60 to 0)
                xanchor="center", yanchor="middle",
                layer="above"
            ))

    fig_loudness_line.update_layout(
        xaxis=dict(range=[-65, 5], title="Loudness (dB)", showgrid=True, dtick=10),
        yaxis=dict(range=[-0.2, 0.2], showticklabels=False, showgrid=False, zeroline=False),
        height=200,
        images=loudness_images, # <--- Attach images here
        margin=dict(t=20, b=50, l=50, r=50),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_loudness_line, use_container_width=True)

    # # Simple scatter plot
    # st.write("#### Tempo vs Loudness Relationship")
    # fig_scatter = px.scatter(
    #     viz_df, 
    #     x="Tempo", 
    #     y="Loudness", 
    #     color="Bard", 
    #     size_max=15,
    #     labels={"Tempo": "Tempo (BPM)", "Loudness": "Loudness (dB)"},
    #     hover_data={"Name": True},
    #     color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    # )
    # fig_scatter.update_layout(
    #     xaxis_title="Tempo (BPM)",
    #     yaxis_title="Loudness (dB)",
    #     margin=dict(t=0)
    # )
    # fig_scatter.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Tempo: %{x} BPM<br>Loudness: %{y} dB<extra></extra>')
    # st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Create creature task analysis charts
    if len(st.session_state.user_playlist) > 0:
        # Extract creature and task data
        creature_task_data = []
        for song in st.session_state.user_playlist:
            if song.get("Creature") and song.get("Task Category"):
                creature_task_data.append({
                    "Creature": song["Creature"],
                    "Task Category": song["Task Category"],
                    "Song": song["Name"]
                })
        
        if creature_task_data:
            df_creatures = pd.DataFrame(creature_task_data)
            
            # Stacked bar chart of task categories by creature - full width
            st.write("#### Creature Task Distribution")
            creature_counts = df_creatures.groupby(['Task Category', 'Creature']).size().reset_index(name='Count')
            
            # Calculate y-axis range based on max count
            max_count = creature_counts['Count'].max()
            if max_count == 1:
                y_range = [0, 4]  # Make it take up only a quarter of the axis
            else:
                y_range = [0, max_count + 0.5]  # Add small buffer above max
            
            fig_creature_bar = px.bar(
                creature_counts,
                x="Task Category",
                y="Count",
                color="Creature",
                color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            )
            fig_creature_bar.update_layout(
                xaxis_title="Task Category",
                yaxis_title="Count",
                yaxis=dict(
                    range=y_range,
                    dtick=1,  # Force whole number ticks
                    tickmode='linear'
                ),
                margin=dict(t=0),
                legend_title="Motivated Creature"
            )
            st.plotly_chart(fig_creature_bar, use_container_width=True)
            
            # # Scatter plot of creatures by task category - full width
            # st.write("#### Creature Task Scatter")
            # # Add some jitter for better visualization
            # import random
            # df_creatures_scatter = df_creatures.copy()
            # df_creatures_scatter['jitter'] = [random.uniform(-0.2, 0.2) for _ in range(len(df_creatures_scatter))]
            
            # fig_creature_scatter = px.scatter(
            #     df_creatures_scatter,
            #     x="Task Category", 
            #     y="jitter",
            #     color="Creature",
            #     color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
            #     hover_data={"Song": True, "jitter": False}
            # )
            # fig_creature_scatter.update_layout(
            #     xaxis_title="Task Category",
            #     yaxis_title="",
            #     yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            #     margin=dict(t=0),
            #     legend_title="Motivated Creature"
            # )
            # fig_creature_scatter.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>%{fullData.name}<br>%{x}<extra></extra>')
            # st.plotly_chart(fig_creature_scatter, use_container_width=True)
    
    # Continue with existing YouTube embed section...

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

    # Define invalid characters for filenames
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '#', '%', '&', '{', '}', '$', '!', "'", '`', '@']
    
    # Check for invalid characters
    found_invalid = [char for char in invalid_chars if char in playlist_name]
    
    if found_invalid and playlist_name:
        st.error(f"❌ Oops! Your playlist name has a character we can't use yet: {' '.join(found_invalid)}")
        st.caption("These characters are not allowed: / \\ : * ? \" < > | # % & { } $ ! ' ` @")
    elif st.button("📝 Save Playlist", type="primary") and playlist_name:
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


