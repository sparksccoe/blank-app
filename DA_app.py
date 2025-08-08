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
import pandas as pd
import numpy as np
import soundfile as sf
import sounddevice as sd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Data Adventures: Symphonia",
    page_icon="🎵",
    layout="wide",  # Changed to wide for better tablet experience
    initial_sidebar_state="collapsed",
)

# ============================================
# CUSTOM CSS FOR PROFESSIONAL DESIGN
# ============================================
st.markdown("""
    <style>
    /* Main container optimization for tablets */
    .main > div {
        max-width: 1024px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* Professional color scheme */
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --accent-color: #F18F01;
        --success-color: #06D6A0;
        --background-light: #F7F9FB;
        --text-dark: #2D3436;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, header, footer, .css-1dp5vir {
        visibility: hidden;
    }
    
    /* Custom header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .subtitle {
        font-size: 1.2rem;
        opacity: 0.95;
        margin-top: 0.5rem;
    }
    
    /* Card-style sections */
    .card-section {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Professional button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 134, 171, 0.4);
    }
    
    /* Input field styling */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #E0E6ED;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
    }
    
    /* Metric cards for BPM and Loudness display */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Song card styling */
    .song-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: transform 0.2s ease;
    }
    
    .song-card:hover {
        transform: translateX(5px);
    }
    
    /* Playlist section */
    .playlist-header {
        background: linear-gradient(135deg, var(--success-color), var(--accent-color));
        color: white;
        padding: 1.5rem;
        border-radius: 15px 15px 0 0;
        margin-bottom: 0;
    }
    
    /* Success/Info messages */
    .stSuccess, .stInfo {
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid var(--success-color);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: var(--background-light);
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Table styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Responsive design for tablets */
    @media (max-width: 768px) {
        .main > div {
            padding: 0.5rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .card-section {
            padding: 1.5rem;
        }
    }
    
    /* Hide default Streamlit styling */
    .css-1629p8f h1, .css-1629p8f h2, .css-1629p8f h3 {
        padding: 0;
    }
    
    /* Progress indicator */
    .progress-step {
        display: inline-block;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #E0E6ED;
        color: white;
        text-align: center;
        line-height: 40px;
        font-weight: bold;
        margin: 0 0.5rem;
        transition: all 0.3s ease;
    }
    
    .progress-step.active {
        background: var(--primary-color);
        transform: scale(1.1);
    }
    
    .progress-step.completed {
        background: var(--success-color);
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE SESSION STATE
# ============================================
if "user_playlist" not in st.session_state:
    st.session_state.user_playlist = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "bpm_value" not in st.session_state:
    st.session_state.bpm_value = None
if "loudness_value" not in st.session_state:
    st.session_state.loudness_value = None

# ============================================
# SPOTIFY CONFIGURATION
# ============================================
client_id = '922604ee2b934fbd9d1223f4ec023fba'
client_secret = '1bdf88cb16d64e54ba30220a8f126997'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# ============================================
# DATA LOADING
# ============================================
playlist_id = "3BGJRi9zQrIjLDtBbRYy5n"
api_key = "AIzaSyAxHBK8MxzePcos86BOaBwUtTurr_ZbpNg"
youtube_playlist_url = "https://www.youtube.com/playlist?list=PLtg7R4Q_LfGU-WLVp5jeOoD7tdUiS6FHg"
youtube_playlist_id = youtube_playlist_url.split("list=")[-1]
song_features_csv = "Symphonia Bards-3.csv"

@st.cache_data
def load_song_data():
    """Load and cache song data"""
    df_audio_features = pd.read_csv(song_features_csv)
    
    # Process decades
    df_decades = pd.DataFrame({'Release Date': df_audio_features["Album Date"]})
    df_decades['Year'] = pd.to_datetime(df_decades['Release Date']).dt.year
    df_decades['Decade'] = (df_decades['Year'] // 10) * 10
    track_decade = df_decades['Decade'].astype(str) + "s"
    
    # Fetch YouTube videos
    videos, track_video_id = fetch_playlist_videos(api_key, youtube_playlist_id)
    
    # Create main dataframe
    df_tracks = pd.DataFrame({
        "Track ID": df_audio_features["Spotify Track Id"].tolist(),
        "Name": df_audio_features["Song"].tolist(),
        "Artist": df_audio_features["Artist"].tolist(),
        "Album": df_audio_features["Album"].tolist(),
        "Popularity": df_audio_features["Popularity"].tolist(),
        "Release Date": df_audio_features["Album Date"].tolist(),
        "Decade": track_decade,
        "Image": df_audio_features["Image"].tolist(),
        "Danceability": df_audio_features["Dance"].tolist(),
        "Energy": df_audio_features["Energy"].tolist(),
        "Loudness (dB)": df_audio_features["Loud (Db)"].tolist(),
        "Acousticness": df_audio_features["Acoustic"].tolist(),
        "Instrumentalness": df_audio_features["Instrumental"].tolist(),
        "Liveness": df_audio_features["Live"].tolist(),
        "Happiness": df_audio_features["Happy"].tolist(),
        "Tempo (BPM)": df_audio_features["BPM"].apply(round).tolist(),
        "Time Signature": df_audio_features["Time Signature"].tolist(),
        "Speechiness": df_audio_features["Speech"].tolist(),
        "Key": df_audio_features["Key"].tolist(),
        "Duration": df_audio_features["Time"].tolist(),
        "Bard": df_audio_features["Bard"].tolist(),
        "YouTube Video ID": track_video_id[:len(df_audio_features)],
    })
    
    return df_tracks

@st.cache_data
def load_creature_data():
    """Load and cache creature data"""
    creatures_csv = "DA Creatures.csv"
    return pd.read_csv(creatures_csv)

def fetch_playlist_videos(api_key, youtube_playlist_id):
    """Fetch YouTube playlist videos"""
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
        return [], []

# Load data
df_tracks = load_song_data()
df_creatures_data = load_creature_data()

# ============================================
# HEADER SECTION
# ============================================
st.markdown("""
    <div class="main-header">
        <h1>🎵 Data Adventures: Symphonia</h1>
        <div class="subtitle">Create Your Magical Creature Concerto</div>
    </div>
""", unsafe_allow_html=True)

# ============================================
# PROGRESS INDICATOR
# ============================================
col1, col2, col3, col4, col5 = st.columns(5)
steps = ["🎹 BPM", "🔊 Volume", "🎯 Match", "🐾 Creature", "📝 Save"]
for i, (col, step) in enumerate(zip([col1, col2, col3, col4, col5], steps), 1):
    with col:
        if i < st.session_state.current_step:
            status = "completed"
        elif i == st.session_state.current_step:
            status = "active"
        else:
            status = ""
        st.markdown(f"""
            <div style="text-align: center;">
                <div class="progress-step {status}">{i}</div>
                <div style="margin-top: 0.5rem; font-size: 0.9rem;">{step}</div>
            </div>
        """, unsafe_allow_html=True)

# ============================================
# SAVED PLAYLIST RETRIEVAL
# ============================================
with st.container():
    st.markdown('<div class="card-section">', unsafe_allow_html=True)
    with st.expander("🗝️ **Load Saved Playlist**", expanded=False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("Enter your playlist code:")
            entered_code = st.text_input("", label_visibility="collapsed", placeholder="Enter code").strip().lower()
        
        if entered_code:
            playlist_dir = "saved_user_playlists"
            os.makedirs(playlist_dir, exist_ok=True)
            
            matching_files = [
                f for f in os.listdir(playlist_dir)
                if f.lower().endswith(f"{entered_code}.csv")
            ]
            
            if matching_files:
                playlist_file = matching_files[0]
                filepath = os.path.join(playlist_dir, playlist_file)
                retrieved_df = pd.read_csv(filepath)
                st.session_state.user_playlist = retrieved_df.to_dict(orient="records")
                playlist_base_name = playlist_file.rsplit("_", 1)[0].replace("_", " ")
                st.session_state.saved_playlist_name = playlist_base_name
                st.success(f"✅ Playlist '{playlist_base_name}' loaded successfully!")
                st.session_state.current_step = 5
            else:
                st.error("❌ No playlist found with that code.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# STEP 1: BPM INPUT
# ============================================
st.markdown('<div class="card-section">', unsafe_allow_html=True)
st.markdown("### 🎹 Step 1: Set Your Tempo")

col1, col2 = st.columns([2, 1])
with col1:
    bpm = st.number_input(
        "Enter BPM (40-250)",
        min_value=40,
        max_value=250,
        value=st.session_state.bpm_value,
        step=1,
        help="Beats Per Minute - the tempo of your song"
    )
    
    if bpm:
        st.session_state.bpm_value = bpm
        if st.session_state.current_step < 2:
            st.session_state.current_step = 2
        
        # Display tempo interpretation
        if bpm < 60:
            tempo_desc = "🐌 **Extremely Slow** - Meditative & Peaceful"
        elif bpm < 90:
            tempo_desc = "🚶 **Slow** - Relaxed & Groovy"
        elif bpm < 120:
            tempo_desc = "🚶‍♂️ **Moderate** - Walking Pace"
        elif bpm < 150:
            tempo_desc = "🏃 **Fast** - Energetic & Upbeat"
        else:
            tempo_desc = "⚡ **Very Fast** - Intense & Driving"
        
        st.info(tempo_desc)

with col2:
    if bpm:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Current BPM</div>
                <div class="metric-value">{bpm}</div>
            </div>
        """, unsafe_allow_html=True)

# Generate drum sound functions (kept from original)
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
    
    kick = generate_drum_sound(drum_type="kick")
    snare = generate_drum_sound(drum_type="snare")
    hihat = generate_drum_sound(drum_type="hihat")
    
    for i in range(num_beats):
        start = int(i * interval * sample_rate)
        end = start + len(kick)
        
        if i % 4 in [0, 2]:
            audio[start:end] += kick
        if i % 4 == 1 or i % 4 == 3:
            audio[start:end] += snare
        
        hh_start = int(i * interval * sample_rate)
        hh_end = hh_start + len(hihat)
        audio[hh_start:hh_end] += hihat
    
    return np.clip(audio, -1, 1)

if bpm:
    if st.button("🥁 Preview Tempo", use_container_width=True):
        drum_beat = generate_drum_beat(bpm)
        sf.write("drum_beat.wav", drum_beat, 44100)
        st.audio("drum_beat.wav")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# STEP 2: LOUDNESS INPUT
# ============================================
if st.session_state.bpm_value:
    st.markdown('<div class="card-section">', unsafe_allow_html=True)
    st.markdown("### 🔊 Step 2: Set Your Volume")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        loudness = st.number_input(
            "Enter Loudness (-60 to 0 dB)",
            min_value=-60,
            max_value=0,
            value=st.session_state.loudness_value,
            step=1,
            help="Relative loudness in decibels"
        )
        
        if loudness is not None:
            st.session_state.loudness_value = loudness
            if st.session_state.current_step < 3:
                st.session_state.current_step = 3
            
            # Display loudness interpretation
            if loudness < -40:
                loud_desc = "🔇 **Very Quiet** - Whisper Soft"
            elif loudness < -25:
                loud_desc = "🔈 **Quiet** - Background Music"
            elif loudness < -15:
                loud_desc = "🔉 **Moderate** - Comfortable Listening"
            elif loudness < -5:
                loud_desc = "🔊 **Loud** - Party Volume"
            else:
                loud_desc = "📢 **Very Loud** - Maximum Impact"
            
            st.info(loud_desc)
    
    with col2:
        if loudness is not None:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div class="metric-label">Current Volume</div>
                    <div class="metric-value">{loudness} dB</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# STEP 3: FIND MATCH
# ============================================
if st.session_state.bpm_value and st.session_state.loudness_value is not None:
    st.markdown('<div class="card-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Step 3: Find Your Musical Match")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔮 Reveal Musical Match", use_container_width=True, type="primary"):
            if not df_tracks.empty:
                df_tracks["Tempo Difference"] = abs(df_tracks["Tempo (BPM)"] - st.session_state.bpm_value)
                df_tracks["Loudness Difference"] = abs(df_tracks["Loudness (dB)"] - st.session_state.loudness_value)
                df_tracks["Match Score"] = df_tracks["Tempo Difference"] + df_tracks["Loudness Difference"]
                
                best_match = df_tracks.loc[df_tracks["Match Score"].idxmin()]
                st.session_state.best_match = best_match.to_dict()
                if st.session_state.current_step < 4:
                    st.session_state.current_step = 4
    
    # Display match if found
    if "best_match" in st.session_state:
        best_match = st.session_state.best_match
        
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(best_match["Image"], use_column_width=True)
        
        with col2:
            st.markdown(f"### 🎵 {best_match['Name']}")
            st.markdown(f"**Artist:** {best_match['Bard']}")
            
            # Display match metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("BPM", f"{best_match['Tempo (BPM)']} BPM")
            with col_b:
                st.metric("Loudness", f"{best_match['Loudness (dB)']} dB")
        
        # YouTube embed
        if pd.notna(best_match.get("YouTube Video ID")):
            youtube_embed_url = f"https://www.youtube.com/embed/{best_match['YouTube Video ID']}"
            st.video(youtube_embed_url)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# STEP 4: CREATURE PAIRING
# ============================================
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
            tempo_low is not None and tempo_high is not None and 
            tempo_low <= tempo <= tempo_high
        )
        loudness_match = (
            loud_low is not None and loud_high is not None and 
            loud_low <= loudness <= loud_high
        )
        
        if tempo_match or loudness_match:
            matched.append(row)
    
    return matched

if "best_match" in st.session_state:
    st.markdown('<div class="card-section">', unsafe_allow_html=True)
    st.markdown("### 🐾 Step 4: Pair with a Creature")
    
    best_match = st.session_state.best_match
    matched_creatures = find_matching_creatures_either(
        best_match["Tempo (BPM)"], 
        best_match["Loudness (dB)"], 
        df_creatures_data
    )
    
    if matched_creatures:
        creature_names = ["-- Select Creature --"] + [creature["Name"] for creature in matched_creatures]
        
        selected_creature_name = st.selectbox(
            "Which creature did you pair with?",
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
                music_tasks = [
                    "-- Select Task --",
                    selected_creature_obj["Task Specific 1"],
                    selected_creature_obj["Task Specific 2"]
                ]
                
                selected_task = st.selectbox(
                    f"What task should {selected_creature_name} complete?",
                    music_tasks,
                    index=0,
                    key="music_task_selection"
                )
                
                # Add to playlist button
                if selected_task != "-- Select Task --":
                    if st.button("✨ Add to Playlist", use_container_width=True, type="primary"):
                        song_with_context = best_match.copy()
                        song_with_context["Creature"] = selected_creature_name
                        song_with_context["Task Selected"] = selected_task
                        song_with_context["Task Category"] = selected_creature_obj["Task Category"]
                        
                        track_ids = [song["Track ID"] for song in st.session_state.user_playlist]
                        if best_match["Track ID"] not in track_ids:
                            st.session_state.user_playlist.append(song_with_context)
                            st.success("✅ Added to playlist!")
                            
                            # Reset for next song
                            st.session_state.bpm_value = None
                            st.session_state.loudness_value = None
                            if "best_match" in st.session_state:
                                del st.session_state.best_match
                            st.session_state.current_step = 1
                            st.rerun()
                        else:
                            st.warning("⚠️ This song is already in your playlist!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# PLAYLIST DISPLAY
# ============================================
if st.session_state.user_playlist:
    st.markdown('<div class="card-section">', unsafe_allow_html=True)
    st.markdown(f"### 🎶 Your Playlist {st.session_state.get('saved_playlist_name', '')}")
    
    # Display each song
    for idx, song in enumerate(st.session_state.user_playlist):
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col1:
            st.image(song["Image"], use_column_width=True)
        
        with col2:
            st.markdown(f"**{song['Name']}** by {song['Bard']}")
            st.caption(f"BPM: {song['Tempo (BPM)']} | Volume: {song['Loudness (dB)']} dB")
            if song.get("Creature"):
                st.caption(f"🐾 {song['Creature']} - {song.get('Task Selected', '')}")
        
        with col3:
            if st.button("🗑️", key=f"remove_{idx}", help="Remove from playlist"):
                st.session_state.user_playlist.pop(idx)
                st.rerun()
    
    # Playlist summary table
    if len(st.session_state.user_playlist) > 1:
        with st.expander("📊 View Detailed Playlist Summary"):
            playlist_df = pd.DataFrame(st.session_state.user_playlist)
            display_df = playlist_df[["Name", "Bard", "Tempo (BPM)", "Loudness (dB)", 
                                     "Creature", "Task Selected"]].copy()
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # YouTube playlist
    with st.expander("🎧 Play on YouTube"):
        video_ids = [song["YouTube Video ID"] for song in st.session_state.user_playlist 
                    if pd.notna(song.get("YouTube Video ID"))]
        
        if video_ids:
            if len(video_ids) == 1:
                youtube_embed_url = f"https://www.youtube.com/embed/{video_ids[0]}"
            else:
                first_video = video_ids[0]
                playlist_videos = ",".join(video_ids)
                youtube_embed_url = f"https://www.youtube.com/embed/{first_video}?playlist={playlist_videos}"
            
            st.markdown(
                f'<iframe width="100%" height="400" src="{youtube_embed_url}" '
                f'frameborder="0" allowfullscreen></iframe>',
                unsafe_allow_html=True
            )
        else:
            st.info("No YouTube videos available for this playlist.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SAVE PLAYLIST SECTION
# ============================================
if st.session_state.user_playlist:
    st.markdown('<div class="card-section">', unsafe_allow_html=True)
    st.markdown("### 💾 Save Your Playlist")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        playlist_name = st.text_input(
            "Playlist Name",
            placeholder="Enter a memorable name for your playlist"
        )
    
    with col2:
        if st.button("💾 Save", use_container_width=True, type="primary") and playlist_name:
            # Word list for code generation
            word_choices = [
                "Graph", "Tempo", "Volume", "Loud", "Soft", "Fast", "Slow", 
                "Data", "Creature", "Bard", "Village", "Music", "Band"
            ]
            
            playlist_dir = "saved_user_playlists"
            os.makedirs(playlist_dir, exist_ok=True)
            
            # Generate unique code
            base_word = random.choice(word_choices).lower()
            existing_codes = {
                f.rsplit("_", 1)[-1].replace(".csv", "").lower()
                for f in os.listdir(playlist_dir) if f.endswith(".csv")
            }
            
            playlist_code = base_word
            suffix = 1
            while playlist_code in existing_codes:
                playlist_code = f"{base_word}{suffix}"
                suffix += 1
            
            # Save playlist
            filename = f"{playlist_name.replace(' ', '_')}_{playlist_code}.csv"
            filepath = os.path.join(playlist_dir, filename)
            
            df_playlist = pd.DataFrame(st.session_state.user_playlist)
            df_playlist.to_csv(filepath, index=False)
            
            # Set expiration
            expiration_date = datetime.now() + timedelta(weeks=2)
            meta_filepath = os.path.join(playlist_dir, f"{filename}.meta")
            with open(meta_filepath, "w") as meta_file:
                meta_file.write(expiration_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            st.success(f"✅ Playlist saved successfully!")
            st.info(f"**Your Playlist Code:** `{playlist_code}`\n\nUse this code to reload your playlist anytime within 2 weeks.")
            st.session_state.current_step = 5
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# CLEANUP OLD PLAYLISTS
# ============================================
def cleanup_old_playlists():
    """Remove expired playlists"""
    playlist_dir = "saved_user_playlists"
    if not os.path.exists(playlist_dir):
        return
    
    now = datetime.now()
    for file in os.listdir(playlist_dir):
        if file.endswith(".meta"):
            meta_filepath = os.path.join(playlist_dir, file)
            try:
                with open(meta_filepath, "r") as meta_file:
                    expiration_str = meta_file.read().strip()
                    expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S")
                    
                    if now > expiration_date:
                        playlist_csv = meta_filepath.replace(".meta", "")
                        os.remove(meta_filepath)
                        if os.path.exists(playlist_csv):
                            os.remove(playlist_csv)
            except:
                continue

# Run cleanup
cleanup_old_playlists()
