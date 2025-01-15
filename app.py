import pandas as pd
import numpy as np
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API Credentials
CLIENT_ID = "4da10aae52c04c8ab5c4a5300212c9d5"
CLIENT_SECRET = "cfc4944866a943c9984b87cce8167b91"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load data from CSV file
@st.cache_data  # Cache the dataset for faster reloads
def load_data():
    return pd.read_csv("data/dataset.csv")

music = load_data()

# Preprocessing for Similarity Calculation
@st.cache_data
def calculate_similarity(df):
    # Select relevant numerical features for similarity calculation
    features = ['danceability', 'energy', 'valence', 'tempo', 'speechiness', 
                'acousticness', 'instrumentalness', 'liveness']
    
    # Scale the features to normalize values
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[features])
    
    # Compute cosine similarity
    similarity_matrix = cosine_similarity(scaled_features)
    return similarity_matrix

similarity = calculate_similarity(music)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend(song):
    index = music[music['track_name'] == song].index[0]
    distances = list(enumerate(similarity[index]))
    distances = sorted(distances, reverse=True, key=lambda x: x[1])  # Sort by similarity score
    
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:4]:  # Recommend only 3 songs
        artist = music.iloc[i[0]].artists
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].track_name, artist))
        recommended_music_names.append(music.iloc[i[0]].track_name)

    return recommended_music_names, recommended_music_posters

# Streamlit UI Design
st.set_page_config(page_title="Music Recommender", page_icon="🎶", layout="centered")
st.markdown("<style>body {background-color: #f7f9fc;}</style>", unsafe_allow_html=True)

st.title('🎶 Music Recommender System')
st.subheader('Discover your next favorite song!')

# User Input
music_list = music['track_name'].values
selected_song = st.selectbox(
    "Type or select a song from the dropdown",
    music_list,
    help="Select a song to get similar recommendations"
)

if st.button('Show Recommendation'):
    recommended_music_names, recommended_music_posters = recommend(selected_song)
    
    st.markdown("---")
    st.subheader(f"If you like '{selected_song}', you might also enjoy:")

    # Display recommendations in a visually appealing layout
    cols = st.columns(3, gap="large")
    for i, col in enumerate(cols):
        with col:
            st.image(recommended_music_posters[i], width=200)
            st.write(recommended_music_names[i])
            st.markdown("<style>img {border-radius: 15px;}</style>", unsafe_allow_html=True)
