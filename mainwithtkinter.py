import tkinter as tk
from tkinter import messagebox
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from spotipy.oauth2 import SpotifyOAuth
import webbrowser


client_id = 'id'
client_secret = 'secret'
redirect_uri = 'http://localhost:8080/callback'

tracks_df = pd.read_csv('tracks.csv')

features = tracks_df[['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                      'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']]

scaler = MinMaxScaler()
features_normalized = scaler.fit_transform(features)

model = NearestNeighbors(n_neighbors=5, algorithm='auto')
model.fit(features_normalized)

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def recommend_songs(track_id):
    track_features_df = tracks_df.loc[tracks_df['id'] == track_id, ['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']]

    if track_features_df.empty:
        print(f"No features found for track ID {track_id}")
        return []

    track_features = scaler.transform(track_features_df)

    distances, indices = model.kneighbors(track_features)     # nn based on the track features

    recommended_track_ids = tracks_df.iloc[indices[0]]['name']     # get the recommended track names

    return recommended_track_ids.tolist()

def create_playlist():
    playlist_id = playlist_id_entry.get()
    playlist_name = playlist_name_entry.get()
    playlist_description = playlist_description_entry.get()

    playlist_tracks = spotify.playlist_tracks(playlist_id)

    recommended_songs_list = []

    for track in playlist_tracks['items']:
        track_id = track['track']['id']
        track_name = track['track']['name']
        recommended_tracks = recommend_songs(track_id)
        if recommended_tracks:
            recommended_songs_list.extend(recommended_tracks)

    scope = 'playlist-modify-public'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)

    for song_name in recommended_songs_list:
        results = sp.search(q=song_name, type='track', limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.playlist_add_items(playlist_id=playlist['id'], items=[track_uri])

    messagebox.showinfo("Playlist Creation", "Playlist created successfully!")

# Create a Tkinter window
window = tk.Tk()
window.title("Song Recommender")
window.geometry("400x300")

# Create labels and entry fields
playlist_id_label = tk.Label(window, text="Playlist ID:")
playlist_id_label.pack()
playlist_id_entry = tk.Entry(window)
playlist_id_entry.pack()

playlist_name_label = tk.Label(window, text="Playlist Name:")
playlist_name_label.pack()
playlist_name_entry = tk.Entry(window)
playlist_name_entry.pack()

playlist_description_label = tk.Label(window, text="Playlist Description:")
playlist_description_label.pack()
playlist_description_entry = tk.Entry(window)
playlist_description_entry.pack()

# Create a button to trigger the playlist creation process
create_playlist_button = tk.Button(window, text="Create Playlist", command=create_playlist)
create_playlist_button.pack()

# Start the Tkinter event loop
window.mainloop()
