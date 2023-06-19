import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from spotipy.oauth2 import SpotifyOAuth
import webbrowser



client_id = 'your_id'
client_secret = 'your_secret'
redirect_uri = 'http://localhost:8080/callback' #can be changed


# Load tracks.csv into a DataFrame
tracks_df = pd.read_csv('tracks.csv')

# Create a hybrid data structure with the desired features
features = tracks_df[['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                      'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']]

# Normalize the features
scaler = MinMaxScaler()
features_normalized = scaler.fit_transform(features)

# Train the Nearest Neighbors model on the normalized features
model = NearestNeighbors(n_neighbors=5, algorithm='auto')
model.fit(features_normalized)

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to recommend songs for a given track
def recommend_songs(track_id):
    # Get the track features from the hybrid data structure
    track_features_df = tracks_df.loc[tracks_df['id'] == track_id, ['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']]

    if track_features_df.empty:
        print(f"No features found for track ID {track_id}")
        return

    track_features = scaler.transform(track_features_df)

    # Find the nearest neighbors based on the track features
    distances, indices = model.kneighbors(track_features)

    # Retrieve the recommended track IDs
    recommended_track_ids = tracks_df.iloc[indices[0]]['name']

    return recommended_track_ids

playlist_id = 'your_playlist_id' #this is the rock playlist 2y8MhYfjFPJzeQgBSfcxZH
#https://open.spotify.com/playlist/2vrctqRLlQKz6lfyRzLy9e?si=b37c32259e4e41d8 this is the apitest playlist

playlist_tracks = spotify.playlist_tracks(playlist_id)

recommended_songs_list = []

for track in playlist_tracks['items']:
    track_id = track['track']['id']
    track_name = track['track']['name']
    recommended_tracks = recommend_songs(track_id)
    if recommended_tracks is not None:
        print(f"Recommended songs for '{track_name}':")
        print(recommended_tracks)
        print("---------------------------")
        

        recommended_songs_list.extend(recommended_tracks)
    
print(recommended_songs_list)

scope = 'playlist-modify-public'  #we can make it public or private according to what we want
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

playlist_name = input('Playlist Name : ') 
playlist_description = input('Playlist Description : ')  
user_id = sp.me()['id']
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)

for song_name in recommended_songs_list:
    results = sp.search(q=song_name, type='track', limit=1)
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        sp.playlist_add_items(playlist_id=playlist['id'], items=[track_uri])
        print(f"Added '{song_name}' to the playlist.")
    else:
        print(f"No results found for '{song_name}'.")

print("Playlist creation complete.")

spotify_url = "spotify:"

webbrowser.open(spotify_url)
