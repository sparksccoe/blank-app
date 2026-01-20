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
import uuid
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import soundfile as sf
import sounddevice as sd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Data Adventures",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- CSS STYLING ---
def enlarge_table_controls():
    """Injects CSS to enlarge the toolbar and show it ONLY on hover."""
    st.markdown("""
        <style>
        [data-testid="stElementToolbar"] {
            transform: scale(2.0);
            transform-origin: top right;
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
            z-index: 99999 !important;
            right: 5px !important;
            top: 5px !important;
        }
        [data-testid="stDataFrame"]:hover [data-testid="stElementToolbar"] {
            opacity: 1;
        }
        [data-testid="stElementToolbarButton"] svg {
            width: 24px !important;
            height: 24px !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Inject custom CSS
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 1200px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

hide_streamlit_style = """
    <style>
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    header,
    footer {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
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
        opacity: 0.5;
    }
    </style>
    <div class="background-container"></div>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

try:
    with open("style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- SESSION PERSISTENCE IMPROVED ---
SESSION_DIR = "temp_user_sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

# 1. Cleanup Stale Sessions (Garbage Collection)
def cleanup_old_sessions(max_age_hours=24):
    """Deletes temporary session files older than max_age_hours to prevent disk bloat."""
    now = datetime.now()
    cutoff = now - timedelta(hours=max_age_hours)
    
    if os.path.exists(SESSION_DIR):
        for filename in os.listdir(SESSION_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(SESSION_DIR, filename)
                try:
                    # Check file modification time
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_mod_time < cutoff:
                        os.remove(filepath)
                except Exception:
                    pass

# Run cleanup once on script load
cleanup_old_sessions()

# 2. Get Session ID from URL or Generate New One
if "session_id" not in st.query_params:
    new_id = str(uuid.uuid4())
    st.query_params["session_id"] = new_id
    session_id = new_id
else:
    session_id = st.query_params["session_id"]

# Define the file path for this specific user
session_file_path = os.path.join(SESSION_DIR, f"{session_id}.json")

# 3. Define Helper Functions for Auto-Saving/Loading
def auto_save_session():
    """Saves the current playlist and context to a JSON file linked to the session ID."""
    try:
        state_data = {
            "user_playlist": st.session_state.get("user_playlist", []),
            "saved_playlist_name": st.session_state.get("saved_playlist_name", ""),
            # 🟢 IMPROVEMENT: Persist the filename link so autosave works after refresh
            "current_playlist_filename": st.session_state.get("current_playlist_filename", None),
            "youtube_video_ids": st.session_state.get("youtube_video_ids", []),
            "last_active": datetime.now().isoformat()
        }
        with open(session_file_path, "w") as f:
            json.dump(state_data, f)
    except Exception as e:
        print(f"Session Save Error: {e}")

def auto_load_session():
    """Loads the playlist from file if session_state is empty but file exists."""
    # Only load if we haven't already loaded data into session_state
    if os.path.exists(session_file_path) and not st.session_state.get("user_playlist"):
        try:
            with open(session_file_path, "r") as f:
                data = json.load(f)
                
            # Restore state variables
            st.session_state.user_playlist = data.get("user_playlist", [])
            st.session_state.saved_playlist_name = data.get("saved_playlist_name", "")
            # 🟢 IMPROVEMENT: Restore the filename link
            st.session_state.current_playlist_filename = data.get("current_playlist_filename", None)
            st.session_state.youtube_video_ids = data.get("youtube_video_ids", [])
            
            # Touch the file to update modification time (prevents cleanup while active)
            os.utime(session_file_path, None)
            
        except Exception:
            pass # If file is corrupt, just start fresh

# 4. Trigger Load on App Startup
if "user_playlist" not in st.session_state:
    st.session_state.user_playlist = []
    
auto_load_session()

def get_img_base64(img_path):
    """Encodes a local image file or remote URL to base64 for Plotly."""
    if img_path and img_path.startswith(('http://', 'https://')):
        try:
            response = requests.get(img_path, timeout=5)
            if response.status_code == 200:
                encoded = base64.b64encode(response.content).decode()
                ext = img_path.split('.')[-1].lower()
                if ext not in ['png', 'jpg', 'jpeg', 'gif', 'webp']: ext = 'png'
                return f"data:image/{ext};base64,{encoded}"
        except:
            pass
        return None
    elif img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(img_path)[1].replace(".", "")
        return f"data:image/{ext};base64,{encoded}"
    return None

# Helper to update the permanent file if one is selected
def save_updates_to_file():
    if st.session_state.get("current_playlist_filename"):
        playlist_dir = "saved_user_playlists"
        if not os.path.exists(playlist_dir):
            os.makedirs(playlist_dir)
            
        filepath = os.path.join(playlist_dir, st.session_state.current_playlist_filename)
        
        # Save CSV
        pd.DataFrame(st.session_state.user_playlist).to_csv(filepath, index=False)
        
        # Update Meta Timestamp (expires in 2 weeks)
        meta_path = filepath.replace(".csv", ".meta")
        with open(meta_path, "w") as meta_file:
            meta_file.write((datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d %H:%M:%S"))

# Remove song now triggers the file update
def remove_song(idx):
    if "user_playlist" in st.session_state and idx < len(st.session_state.user_playlist):
        st.session_state.user_playlist.pop(idx)
        auto_save_session()    # Save to temporary session
        save_updates_to_file() # Save to permanent file (if linked)

# --- DATA LOADING ---
client_id = '922604ee2b934fbd9d1223f4ec023fba'
client_secret = '1bdf88cb16d64e54ba30220a8f126997'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlist_id = "3BGJRi9zQrIjLDtBbRYy5n"
api_key = "AIzaSyAxHBK8MxzePcos86BOaBwUtTurr_ZbpNg" 
youtube_playlist_url = "https://www.youtube.com/playlist?list=PLtg7R4Q_LfGU-WLVp5jeOoD7tdUiS6FHg"
youtube_playlist_id = youtube_playlist_url.split("list=")[-1]

song_features_csv = "Symphonia Bards-3.csv"
creatures_csv = "DA Creatures 2.csv"

# Load Songs
df_audio_features = pd.read_csv(song_features_csv)
df_decades = pd.DataFrame({'Release Date': df_audio_features["Album Date"]})
df_decades['Year'] = pd.to_datetime(df_decades['Release Date']).dt.year
df_decades['Decade'] = (df_decades['Year'] // 10) * 10
track_decade = df_decades['Decade'].astype(str) + "s"

# Function to fetch playlist details using the YouTube API
def fetch_playlist_videos(api_key, youtube_playlist_id):
    base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "snippet",
        "playlistId": youtube_playlist_id,
        "maxResults": 50,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        videos = [
            {
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
                "video_id": item["snippet"]["resourceId"].get("videoId", None)
            }
            for item in data.get("items", [])
        ]
        track_video_id = [video["video_id"] for video in videos if video["video_id"] is not None]
        return videos, track_video_id
    else:
        st.error("❌ Failed to fetch playlist details.")
        return [], []

videos, track_video_id = fetch_playlist_videos(api_key, youtube_playlist_id)

# Combine Data
df_tracks = pd.DataFrame({
    "Track ID": df_audio_features["Spotify Track Id"],
    "Name": df_audio_features["Song"],
    "Artist": df_audio_features["Artist"],
    "Album": df_audio_features["Album"],
    "Popularity": df_audio_features["Popularity"],
    "Release Date": df_audio_features["Album Date"],
    "Decade": track_decade,
    "Image": df_audio_features["Image"],
    "Bard Image": df_audio_features["Bard Image"],
    "Song Symbol": df_audio_features["Song Symbol"],
    "Danceability": df_audio_features["Dance"],
    "Energy": df_audio_features["Energy"],
    "Loudness (dB)": df_audio_features["Loud (Db)"],
    "Acousticness": df_audio_features["Acoustic"],
    "Instrumentalness": df_audio_features["Instrumental"],
    "Liveness": df_audio_features["Live"],
    "Happiness": df_audio_features["Happy"],
    "Tempo (BPM)": df_audio_features["BPM"].apply(round),
    "Time Signature": df_audio_features["Time Signature"],
    "Speechiness": df_audio_features["Speech"],
    "Key": df_audio_features["Key"],
    "Duration": df_audio_features["Time"],
    "Bard": df_audio_features["Bard"],
    "YouTube Video ID": track_video_id[:len(df_audio_features)],
})

# Load Creatures
df_creatures_data = pd.read_csv(creatures_csv)

# ----------------------------------------------------
# 🟢 1. MAIN APP INTERFACE (Student View)
# ----------------------------------------------------
def main_app():
    # --- UI HEADER ---
    image = Image.open('data_adventures_logo.png')
    col1, col2, col3 = st.columns([1,6,1])
    with col2:
        st.image(image, width=int(image.width * 0.4))

    st.markdown(
        "<div style='text-align: center; font-size: 24px; font-weight: normal;'>"
        "Welcome to Symphonia! Let's start our Creature Concerto."
        "</div><br>", 
        unsafe_allow_html=True
    )

    # --- LOAD SAVED PLAYLIST ---
    with st.expander("**🗝️ Have a Saved Playlist? Tap Here to Load**", expanded=False):
        st.write("Enter your 1-word Playlist Code to load your saved playlist:")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            entered_code = st.text_input(label=" ", label_visibility="collapsed", key="playlist_code_input").strip().lower()
            
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            summon_clicked = st.button("Summon Playlist", type="primary")

        playlist_dir = "saved_user_playlists"

        if summon_clicked and entered_code:
            matching_files = [f for f in os.listdir(playlist_dir) if f.lower().endswith(f"{entered_code}.csv")]
            if matching_files:
                playlist_file = matching_files[0]
                filepath = os.path.join(playlist_dir, playlist_file)
                retrieved_df = pd.read_csv(filepath)
                st.session_state.user_playlist = retrieved_df.to_dict(orient="records")
                st.session_state.saved_playlist_name = playlist_file.rsplit("_", 1)[0].replace("_", " ")
                
                # Link this session to the file for autosave
                st.session_state.current_playlist_filename = playlist_file 
                
                auto_save_session()
                st.success(f"🪄 Playlist summoned! Changes will now autosave to code: **{entered_code}**")
            else:
                st.error("❌ No playlist found with that code.")

    # --- BPM INPUT ---
    st.header("🎚️ Tempo (BPM)")
    st.markdown("<div style='margin-bottom: 0.5rem; font-weight: 500; font-size: 1rem;'>Enter the BPM (Beats Per Minute) of your song (40–250):</div>", unsafe_allow_html=True)

    reset_counter = st.session_state.get("reset_counter", 0)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        bpm = st.number_input(label=" ", min_value=40, max_value=250, value=None, step=1, format="%d", label_visibility="collapsed", key=f"bpm_input_{reset_counter}")

    if bpm is not None:
        if bpm < 60: st.write("This is a **super chill, slow-tempo song**—perfect for relaxation or deep focus.")
        elif bpm < 90: st.write("A **laid-back groove**, great for R&B, lo-fi beats, or smooth jazz.")
        elif bpm < 120: st.write("A **mid-tempo track**—probably a good dance groove or pop beat!")
        elif bpm < 150: st.write("A **fast-paced song**, great for working out or getting pumped up!")
        else: st.write("This is **ultra-fast**—likely a drum & bass, punk, or extreme techno beat!")

    # Drum Generation
    def generate_drum_sound(sample_rate=44100, drum_type="kick"):
        duration = 0.15
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        if drum_type == "kick":
            envelope = np.exp(-t / 0.05)
            sound = 0.8 * envelope * np.sin(2 * np.pi * 60 * t)
        elif drum_type == "snare":
            envelope = np.exp(-t / 0.04)
            noise = np.random.normal(0, 0.5, t.shape)
            sound = 0.5 * envelope * noise
        elif drum_type == "hihat":
            envelope = np.exp(-t / 0.02)
            noise = np.random.normal(0, 0.3, t.shape)
            sound = 0.3 * envelope * noise
        return np.clip(sound, -1, 1)

    def generate_drum_beat(bpm, duration=20, sample_rate=44100):
        interval = 60 / bpm
        num_beats = int(duration / interval)
        audio = np.zeros(int(sample_rate * duration))
        kick = generate_drum_sound("kick")
        snare = generate_drum_sound("snare")
        hihat = generate_drum_sound("hihat")

        for i in range(num_beats):
            start = int(i * interval * sample_rate)
            end = start + len(kick)
            if i % 4 in [0, 2]: audio[start:end] += kick
            if i % 4 == 1 or i % 4 == 3: audio[start:end] += snare
            hh_start = int(i * interval * sample_rate)
            hh_end = hh_start + len(hihat)
            audio[hh_start:hh_end] += hihat
        return np.clip(audio, -1, 1)

    if bpm is not None:
        if st.button("🥁 Play Your Tempo as a Drum Loop", type="primary"):
            drum_beat = generate_drum_beat(bpm)
            sf.write("drum_beat.wav", drum_beat, 44100)
            st.audio("drum_beat.wav")

    # --- LOUDNESS INPUT ---
    st.header("🔊 Loudness (dB)")
    st.markdown("<div style='margin-bottom: 0.5rem; font-weight: 500; font-size: 1rem;'>Enter the relative loudness of your song (in dB, between -60 and 0):</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        loudness = st.number_input(label=" ", min_value=-60, max_value=0, value=None, step=1, format="%d", label_visibility="collapsed", key=f"loudness_input_{reset_counter}")

    if loudness is not None:
        if loudness < -50: st.write("This is **super quiet**! Like a ghost whispering.")
        elif loudness < -40: st.write("This is **very quiet**. Like studying in a library.")
        elif loudness < -30: st.write("This is **quiet**. Chill vibes, background music.")
        elif loudness < -20: st.write("This is **medium volume**. Like a normal conversation.")
        elif loudness < -10: st.write("This is **loud**! Like a busy cafeteria.")
        elif loudness < -5: st.write("This is **really loud**! Like a school assembly.")
        else: st.write("**Max volume!** Like a rock concert!")

    # --- MATCHING LOGIC ---
    if bpm is not None and loudness is not None:
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
            try: return tuple(map(int, r.split(" - ")))
            except: return (None, None)

        for _, row in df.iterrows():
            tempo_low, tempo_high = parse_range(row["Tempo Preference"])
            loud_low, loud_high = parse_range(row["Loudness Preference"])
            tempo_match = (tempo_low is not None and tempo_high is not None and tempo_low <= tempo <= tempo_high)
            loudness_match = (loud_low is not None and loud_high is not None and loud_low <= loudness <= loud_high)
            if tempo_match or loudness_match: matched.append(row)
        return matched

    # --- MATCH RESULT DISPLAY ---
    if "best_match" in st.session_state:
        best_match = st.session_state.best_match
        st.subheader(f"🎵 Your song is **{best_match['Name']}**")
        col1, spacer, col2 = st.columns([1, 0.5, 1])
        with col1:
            st.image(best_match["Image"], caption=best_match["Name"], width=250)
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
            st.markdown("#### Loudness Visualization")
            
            # Calculate visual parameters
            raw_dur = best_match.get("Duration", 0)
            try:
                if isinstance(raw_dur, str) and ":" in raw_dur:
                    parts = raw_dur.split(":")
                    duration_sec = int(parts[0]) * 60 + int(parts[1])
                else:
                    duration_sec = float(raw_dur) / 1000
            except:
                duration_sec = 0

            x_axis = np.linspace(0, duration_sec, len(db_values))
            
            # Rectified Waveform (0 to 1 scale)
            y_values = [max(0, db + 60) for db in db_values]
            
            fig_wave = go.Figure()
            
            # 1. The Waveform (Lavender)
            fig_wave.add_trace(go.Scatter(
                x=x_axis,
                y=y_values,
                fill='tozeroy',
                fillcolor='#AD98B0',
                line=dict(color='#AD98B0', width=1.5),
                opacity=0.9,
                name=song_name,
                hoverinfo="x+text",
                text=[f"{db} dB" for db in db_values]
            ))
            
            # 2. Average Loudness Line (Neon Orange)
            avg_loudness = best_match.get("Loudness (dB)", -60)
            avg_y = avg_loudness + 60
            
            fig_wave.add_trace(go.Scatter(
                x=[0, duration_sec],
                y=[avg_y, avg_y],
                mode='lines',
                line=dict(color='#FF5F1F', width=4), # Thicker line
                name="Avg Loudness",
                hoverinfo="text",
                text=[f"Average: {avg_loudness} dB"]*2
            ))

            # 3. Explicit Text Label for the Line
            fig_wave.add_annotation(
                x=duration_sec * 0.02, # Near the start
                y=avg_y - 5,           # Slightly above the line
                text=f"Average: {avg_loudness} dB",
                showarrow=False,
                font=dict(color='#FF5F1F', size=18, family="Arial Black"),
                xanchor="left",
                yanchor="top"
            )
            
            fig_wave.update_layout(
                xaxis=dict(title="Duration (s)", showgrid=False, zeroline=True, showticklabels=True),
                yaxis=dict(
                    title="Loudness",
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.1)',
                    zeroline=False,
                    showticklabels=True,
                    # ZOOMED RANGE: 30 (-30dB) to 65 (+5dB headroom)
                    range=[30, 65],
                    tickmode='array',
                    # Ticks every 10dB within the new view
                    tickvals=[30, 40, 50, 60],
                    ticktext=['-30 dB', '-20 dB', '-10 dB', '0 dB']
                ),
                height=250, 
                margin=dict(l=60, r=20, t=20, b=40),
                plot_bgcolor='white',
                showlegend=False
            )
            st.plotly_chart(fig_wave, use_container_width=True)
            
        if pd.notna(best_match["YouTube Video ID"]):
            st.video(f"https://www.youtube.com/embed/{best_match['YouTube Video ID']}")
        else:
            st.write("⚠️ No YouTube video available for this track.")
        
        matched_creatures = find_matching_creatures_either(best_match["Tempo (BPM)"], best_match["Loudness (dB)"], df_creatures_data)

        # --- CREATURE SELECTION & AUTO TASK ASSIGNMENT ---
        if "creature_pair_selection" not in st.session_state:
            st.session_state.creature_pair_selection = "-- Select Creature --"

        if matched_creatures:
            if st.session_state.creature_pair_selection == "-- Select Creature --":
                # GRID VIEW
                st.markdown("### This song activates the following creatures. Which one did you pair up in the game?")
                
                # Get list of creatures already in the playlist
                used_creatures = [song.get("Creature") for song in st.session_state.user_playlist]

                cols_per_row = 3
                for i in range(0, len(matched_creatures), cols_per_row):
                    cols = st.columns(cols_per_row)
                    batch = matched_creatures[i:i + cols_per_row]
                    for col, creature in zip(cols, batch):
                        with col:
                            st.markdown(f"**{creature['Creature name']}**")
                            try: st.image(creature["Creature Image"], use_container_width=True)
                            except: st.warning("No Image")
                            
                            # Check if this creature is already used
                            if creature["Creature name"] in used_creatures:
                                st.button("🚫 Already Added", key=f"btn_{creature['Creature name']}", disabled=True, use_container_width=True)
                            else:
                                if st.button("Select", key=f"btn_{creature['Creature name']}", type="secondary", use_container_width=True):
                                    st.session_state.creature_pair_selection = creature["Creature name"]
                                    st.session_state.scroll_to_summary = True
                                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
            else:
                # SUMMARY VIEW
                st.markdown('<div id="summary-section"></div>', unsafe_allow_html=True)
                
                if st.session_state.get("scroll_to_summary", False):
                    # Scrolls the element to the center of the viewport
                    st.markdown(
                        """
                        <script>
                        setTimeout(function() {
                            var element = document.getElementById('summary-section');
                            if(element){
                                element.scrollIntoView({behavior: 'smooth', block: 'center'});
                            }
                        }, 100);
                        </script>
                        """, 
                        unsafe_allow_html=True
                    )
                    del st.session_state.scroll_to_summary

                selected_creature_name = st.session_state.creature_pair_selection
                selected_creature_obj = next((creature for creature in matched_creatures if creature["Creature name"] == selected_creature_name), None)

                if selected_creature_obj is not None:
                    st.info(f"✅ You have selected **{selected_creature_name}**")
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        try: st.image(selected_creature_obj["Creature Image"], use_container_width=True)
                        except: st.write("No Image")
                    with col2:
                        if st.button("🔄 Change Creature", type="secondary"):
                            st.session_state.creature_pair_selection = "-- Select Creature --"
                            st.rerun()

                    # Retrieve the Revised Task and Photo BEFORE the header
                    revised_task = selected_creature_obj.get("Revised Task", "No task available.")
                    revised_task_photo = selected_creature_obj.get("Revised Task Image", None)

                    # --- SHOW REVISED TASK (Auto) ---
                    # The Task string is now the Header
                    st.markdown(f"### {revised_task}")
                    
                    # TRIPLE IMAGE SIZE: Ratio [3, 4]
                    col_t1, col_t2 = st.columns([3, 4])
                    with col_t1:
                        try:
                            if revised_task_photo and pd.notna(revised_task_photo):
                                st.image(revised_task_photo, use_container_width=True)
                            else: st.write("📷")
                        except: st.write("Image Error")
                    with col_t2:
                        pass

        # ➕ ADD TO PLAYLIST BUTTON
        selected_creature_name = st.session_state.get("creature_pair_selection", "-- Select Creature --")

        if selected_creature_name != "-- Select Creature --":
            if st.button("✨ Add to Playlist", key=f"add_{best_match['Track ID']}", type="primary"):        
                
                # Safety check for duplicates
                used_creatures = [song.get("Creature") for song in st.session_state.user_playlist]
                track_ids = [song["Track ID"] for song in st.session_state.user_playlist]

                if selected_creature_name in used_creatures:
                     st.error(f"⚠️ **{selected_creature_name}** is already in your party! Please select a different creature.")
                elif best_match["Track ID"] in track_ids:
                    st.warning("⚠️ This song is already in your playlist!")
                else:
                    # Proceed to Add
                    selected_creature_obj = next((creature for creature in matched_creatures if creature["Creature name"] == selected_creature_name), None)

                    song_with_context = best_match.copy()
                    song_with_context["Creature"] = selected_creature_name
                    
                    if selected_creature_obj is not None:
                        song_with_context["Task Selected"] = selected_creature_obj.get("Revised Task", "")
                        song_with_context["Task Category"] = selected_creature_obj.get("Task Category", "")
                        song_with_context["Loot"] = selected_creature_obj.get("Loot", 1)
                    else:
                        song_with_context["Task Selected"] = ""
                        song_with_context["Task Category"] = ""
                        song_with_context["Loot"] = 1

                    st.session_state.user_playlist.append(song_with_context)
                    
                    auto_save_session()    # Save to temp session
                    save_updates_to_file() # Save to permanent file (if linked)
                    
                    st.session_state.reset_counter = st.session_state.get("reset_counter", 0) + 1
                    if "creature_pair_selection" in st.session_state: del st.session_state.creature_pair_selection
                    if "best_match" in st.session_state: del st.session_state.best_match
                    st.session_state.scroll_to_playlist = True
                    st.rerun()

    # --- PLAYLIST DISPLAY (MAIN) ---
    if st.session_state.user_playlist:
        st.markdown("---")
        st.markdown('<div id="playlist-section"></div>', unsafe_allow_html=True)
        st.subheader(f"🎶 Your Playlist: {st.session_state.get('saved_playlist_name', '')}".strip())

        if st.session_state.get("scroll_to_playlist", False):
            st.markdown("""<script>setTimeout(function() {var element = document.getElementById('playlist-section'); var offsetPosition = element.offsetTop - 250; window.scrollTo({top: offsetPosition, behavior: 'smooth'});}, 100);</script>""", unsafe_allow_html=True)
            del st.session_state.scroll_to_playlist
        
        for idx, song in enumerate(st.session_state.user_playlist):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(song["Image"], width=80)
            with col2:
                st.write(f"**{song['Name']}**")
                st.markdown(f"**Tempo:** {song['Tempo (BPM)']} BPM &nbsp;|&nbsp; **Loudness:** {song['Loudness (dB)']} dB")
            with col3:
                st.markdown("<div style='margin-top: 1.5em;'></div>", unsafe_allow_html=True)
                st.button("🧹 Remove", key=f"remove_{idx}", type="primary", on_click=remove_song, args=(idx,))

        # TABLE SUMMARY
        playlist_summary_df = pd.DataFrame([{
            "Song": song.get("Name", "Unknown"),
            "Tempo(BPM)": song.get("Tempo (BPM)", ""),
            "Loudness(dB)": song.get("Loudness (dB)", ""),
            "Symbol": song.get("Song Symbol", ""), 
            "Creature": song.get("Creature", ""),
            "Task": song.get("Task Selected", ""), 
            "Loot": song.get("Loot", "")
        } for idx, song in enumerate(st.session_state.user_playlist)])

        st.markdown("### 📋 Playlist Table")
        enlarge_table_controls()
        st.markdown("""<style>.element-container:has(.stDataFrame) {max-width: 1400px !important; width: 100% !important;} .stDataFrame table {min-width: 1400px !important;}</style>""", unsafe_allow_html=True)
        
        st.dataframe(
            playlist_summary_df.reset_index(drop=True), 
            use_container_width=True, 
            hide_index=True, 
            column_config={
                "Symbol": st.column_config.ImageColumn("Symbol", width="small")
            }
        )

        # YOUTUBE PLAYLIST EMBED
        st.subheader("🎧 Listen to your playlist on YouTube")
        if "youtube_video_ids" not in st.session_state: st.session_state.youtube_video_ids = []
        new_video_ids = [song["YouTube Video ID"] for song in st.session_state.user_playlist if pd.notna(song["YouTube Video ID"])]
        if set(new_video_ids) != set(st.session_state.youtube_video_ids): st.session_state.youtube_video_ids = new_video_ids

        if st.session_state.youtube_video_ids:
            if len(st.session_state.youtube_video_ids) == 1: youtube_embed_url = f"https://www.youtube.com/embed/{st.session_state.youtube_video_ids[0]}"
            else:
                first_video = st.session_state.youtube_video_ids[0]
                playlist_videos = ",".join(st.session_state.youtube_video_ids)
                youtube_embed_url = f"https://www.youtube.com/embed/{first_video}?playlist={playlist_videos}"
            st.markdown(f'<iframe width="100%" height="400" src="{youtube_embed_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)

        # VISUALIZATION TOGGLE
        current_song_count = len(st.session_state.user_playlist)
        if current_song_count < 3:
            st.info(f"📊 **Data Visualization Unlock:** Add {3 - current_song_count} more songs to unlock graph views! ({current_song_count}/3 songs added)")
        else:
            st.success(f"🎉 **Data Visualization Unlocked!**")
            if "show_data_visualization" not in st.session_state: st.session_state.show_data_visualization = False
            if st.button("📊 View Data" if not st.session_state.show_data_visualization else "🗺️ Hide Data Visualization", type="primary"):
                st.session_state.show_data_visualization = not st.session_state.show_data_visualization

    # --- VISUALIZATION SECTION ---
    if st.session_state.get("show_data_visualization", False) and len(st.session_state.user_playlist) >= 3:
        st.markdown("### **📊 Playlist Data Visualization**")
        
        viz_df = playlist_summary_df[["Song", "Tempo(BPM)", "Loudness(dB)", "Symbol"]].copy()
        viz_df.columns = ["Name", "Tempo", "Loudness", "Symbol"]

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
            text=[f"<b>{row['Name']}</b><br>{row['Tempo']} BPM" for _, row in viz_df.iterrows()],
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
            text=[f"<b>{row['Name']}</b><br>{row['Loudness']} dB" for _, row in viz_df.iterrows()],
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

    # --- SAVE / AUTOSAVE SECTION ---
    if st.session_state.user_playlist:
        st.markdown("---")
        
        # Check if the playlist is already linked to a file
        if st.session_state.get("current_playlist_filename"):
            # STATE: Playlist is saved. Show status.
            filename = st.session_state.current_playlist_filename
            try:
                # Parse filename "Name_Code.csv"
                clean_name = filename.rsplit("_", 1)[0].replace("_", " ")
                code = filename.rsplit("_", 1)[-1].replace(".csv", "")
                
                st.subheader(f"🔮 Enchantment Active: {clean_name}")
                st.success(f"🎶 Playlist linked to code: **{code}**")
                st.info(f"ℹ🕯️ **Remember:** Your code is **{code}**. Make sure you have it written down to reload this playlist next time!")
            except:
                st.subheader("🔮 Enchantment Active")
        else:
            # STATE: Not saved yet. Suggest saving.
            st.subheader("📜 Chronicle Your Concerto")
            
            st.markdown("✨ **Magic Tip:** Save your playlist to enable **Autosave**. Any changes will be updated automatically.")
            
            playlist_name = st.text_input("Enter a name for your playlist:")
            invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '#', '%', '&', '{', '}', '$', '!', "'", '`', '@']
            found_invalid = [char for char in invalid_chars if char in playlist_name]
            
            if found_invalid and playlist_name:
                st.error(f"❌ Invalid characters: {' '.join(found_invalid)}")
            
            elif st.button("🖋️ Inscribe to Archives", type="primary") and playlist_name:
                playlist_dir = "saved_user_playlists"
                if not os.path.exists(playlist_dir): os.makedirs(playlist_dir)
                
                word_choices = ["Graph", "Tempo", "Volume", "Loud", "Soft", "Fast", "Slow", "Numeric", "Data", "Creature", "Bard", "Adventure"]
                base_word = random.choice(word_choices).lower()
                existing_codes = {f.rsplit("_", 1)[-1].replace(".csv", "").lower() for f in os.listdir(playlist_dir) if f.endswith(".csv")}
                
                playlist_code = base_word
                suffix = 1
                while playlist_code in existing_codes:
                    playlist_code = f"{base_word}{suffix}"
                    suffix += 1

                filename = f"{playlist_name.replace(' ', '_')}_{playlist_code}.csv"
                
                # Set the filename in session state
                st.session_state.current_playlist_filename = filename
                
                # Trigger the save
                save_updates_to_file()

                st.success("✅ Concerto Inscribed Successfully!")
                
                st.markdown(f"## 🗝️ CODE: `{playlist_code}`")
                
                st.warning("⚠️ **IMPORTANT:** Write this code down now! You will need to enter this code to bring up your playlist next time.")
                
                st.rerun()

def cleanup_old_playlists():
    playlist_dir = "saved_user_playlists"
    now = datetime.now()
    if os.path.exists(playlist_dir):
        for file in os.listdir(playlist_dir):
            if file.endswith(".meta"):
                meta_filepath = os.path.join(playlist_dir, file)
                try:
                    with open(meta_filepath, "r") as meta_file:
                        if now > datetime.strptime(meta_file.read().strip(), "%Y-%m-%d %H:%M:%S"):
                            os.remove(meta_filepath)
                            csv_path = meta_filepath.replace(".meta", "")
                            if os.path.exists(csv_path): os.remove(csv_path)
                except: pass
cleanup_old_playlists()

# ----------------------------------------------------
# 🔐 2. ADMIN PAGE INTERFACE
# ----------------------------------------------------
def admin_page():
    st.title("🔐 Admin Access")
    
    playlist_dir = "saved_user_playlists"

    # Initialize session state for admin login
    if "is_admin" not in st.session_state: st.session_state.is_admin = False

    if not st.session_state.is_admin:
        if st.text_input("Enter Admin Password:", type="password") == os.environ.get("ADMIN_PASSWORD", "secret123"):
            st.session_state.is_admin = True
            st.rerun()
        st.info("Please enter the password to manage saved playlists.")
    
    if st.session_state.is_admin:
        st.success("✅ Logged in")
        
        if os.path.exists(playlist_dir):
            files = [f for f in os.listdir(playlist_dir) if f.endswith(".csv")]
            
            # --- GROUPING LOGIC ---
            grouped_playlists = {}
            
            for filename in files:
                try:
                    # Parse Filename: "My_Cool_Song_tempo1.csv"
                    # Split by the last underscore to separate Name from Code
                    parts = filename.rsplit("_", 1)
                    
                    if len(parts) == 2:
                        raw_name = parts[0]
                        clean_name = raw_name.replace("_", " ") # "My Cool Song"
                        code = parts[1].replace(".csv", "")     # "tempo1"
                    else:
                        clean_name = "Uncategorized"
                        code = filename

                    filepath = os.path.join(playlist_dir, filename)
                    mod_time = os.path.getmtime(filepath)
                    time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %I:%M %p')

                    # Add to dictionary
                    if clean_name not in grouped_playlists:
                        grouped_playlists[clean_name] = []
                    
                    grouped_playlists[clean_name].append({
                        "filename": filename,
                        "code": code,
                        "time_val": mod_time,
                        "time_str": time_str,
                        "path": filepath
                    })
                except:
                    continue

            # --- DISPLAY LOGIC ---
            if not grouped_playlists:
                st.warning("No saved playlists found.")
            else:
                st.write(f"**Found {len(files)} saved files across {len(grouped_playlists)} unique playlists:**")
                st.markdown("---")

                # Sort groups alphabetically by Name
                for group_name in sorted(grouped_playlists.keys()):
                    versions = grouped_playlists[group_name]
                    
                    # Sort versions by Time (Newest First)
                    versions.sort(key=lambda x: x['time_val'], reverse=True)
                    
                    latest_time = versions[0]['time_str']
                    
                    # Create an Expander for the Group
                    with st.expander(f"📂 **{group_name}** ({len(versions)} versions) — Last update: {latest_time}"):
                        
                        # Table Headers inside the expander
                        h1, h2, h3 = st.columns([1, 2, 1])
                        with h1: st.caption("Code")
                        with h2: st.caption("Saved Time")
                        with h3: st.caption("Download")
                        
                        for v in versions:
                            c1, c2, c3 = st.columns([1, 2, 1])
                            with c1: 
                                st.markdown(f"**`{v['code']}`**")
                            with c2: 
                                st.text(v['time_str'])
                            with c3:
                                with open(v['path'], "r") as f:
                                    st.download_button("⬇️", f, v['filename'], "text/csv", key=f"dl_{v['filename']}")
        else:
            st.warning("No saved playlists directory found.")

        if st.button("🔒 Log Out"):
            st.session_state.is_admin = False
            st.rerun()

# ----------------------------------------------------
# 🔀 3. PAGE ROUTER
# ----------------------------------------------------
# Check the URL for ?mode=admin
# If found, show admin page. Otherwise, show main app.

query_params = st.query_params
mode = query_params.get("mode", "app")

if mode == "admin":
    admin_page()
else:
    main_app()