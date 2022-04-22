import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
import requests
import pandas as pd
import pprint

def get_id(track_name: str, token: str, artist: str = '') -> str:
    pp = pprint.PrettyPrinter(indent=1, compact=True)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer ' + token,
        }
    params = [
        ('q', track_name + ' ' + artist),
        ('type', 'track'),
        ]

    try:
        response = requests.get(
            'https://api.spotify.com/v1/search',
            headers = headers,
            params = params,
            timeout = 5
            )

        json = response.json()
        results = json['tracks']['items']
        # pp.pprint(results[0])
        first_result = json['tracks']['items'][0]
        track_id = first_result['id']
        return track_id
    except:
        return None

def get_features(track_id: str, sp) -> dict:
    pp = pprint.PrettyPrinter(indent=1, compact=True)

    try:
        features = sp.audio_features([track_id])
        # pp.pprint(features[0])
        yield features[0]
    except:
        yield None

##########################
# Generate Library songs #
##########################

def generate_library(sp):
    offset = 0
    limit = 50
    num_songs = sp.current_user_saved_tracks()['total']

    if num_songs < limit:
        limit = num_songs

    while (offset <= num_songs):
        # Get liked songs
        library_songs = sp.current_user_saved_tracks(limit=limit, offset=offset)['items']

        # Get track info
        for num, song in enumerate(library_songs):
            song_name   = song['track']['name']
            song_artist = song['track']['artists'][0]['name']
            song_pop    = song['track']['popularity']
            song_uri    = song['track']['uri']
            try:
                # print(f"{num+offset}: {song_name} by {song_artist}\n\tPopularity: {song_pop}, URI: {song_uri}\n")
                yield {'uri': song_uri, 'name': song_name, 'pop': song_pop, 'artist':song_artist}
            except:
                pass

        # Increment offset
        if offset + 50 >= num_songs:
            offset = num_songs - offset
        else:
            offset = offset + 50

#########################################
# Create a playlist and get playlist id #
#########################################

def get_playlist_id(playlist_name: str, playlist_desc: str, username: str, sp) -> str:

    # Cycle through all user playlists to see if playlist already exists
    playlist_exists = False
    user_playlist_info = sp.current_user_playlists()

    while user_playlist_info:
        for playlist in user_playlist_info['items']:
            if playlist['name'] == playlist_name:
                playlist_exists = True
                playlist_id = playlist['id']
        if user_playlist_info['next']:
            user_playlist_info = sp.next(user_playlist_info)
        else:
            user_playlist_info = None

    # Create Playlist based on 'playlist_exists' boolean
    if not playlist_exists:
        playlist_info = sp.user_playlist_create(username, playlist_name, description=playlist_desc)
        playlist_id = playlist_info['id']
        print("Playlist created")
    else:
        print("Playlist not created")

    return playlist_id

#####################################
# Generate existing song dictionary #
#####################################

def get_playlist_songs(playlist_id: str, sp) -> dict:
    playlist_dict = {}
    playlist_songs = sp.playlist_items(playlist_id)

    while playlist_songs:
        for song in playlist_songs['items']:
            playlist_dict[song['track']['uri']] = song['track']['name']
        if playlist_songs['next']:
            playlist_songs = sp.next(playlist_songs)
        else:
            playlist_songs = None

    return playlist_dict

##############################
# Generate acoustic playlist #
##############################

def create_acoustic_playlist(username: str, sp):
    # Get playlist id (Create or find the id)
    playlist_id = get_playlist_id("Acoustic - Auto-Generated", "Auto-generated acoustic playlist", username, sp)

    # Get dictionary of playlist songs
    playlist_dict = get_playlist_songs(playlist_id, sp)

    ###########################################
    # Generate Library, Filter acoustic songs #
    ###########################################
    added = 0
    count = 0

    for info in generate_library(sp):
        for features in get_features(info['uri'], sp):
            if features and features['acousticness'] > 0.85:
                try:
                    if info['uri'] not in playlist_dict:
                        sp.playlist_add_items(playlist_id, [info['uri']])
                        print(f"({count}) Added song: {info['name']}: {features['acousticness']}")
                        playlist_dict[info['uri']] = playlist_dict[info['name']]
                        added = added + 1
                    else:
                        print(f"({count}) Song already exists: {info['name']}")
                except:
                    pass
            else:
                print(f"({count}) Not acoustic enough: {info['name']}: {features['acousticness']}")
        count = count + 1

    print(f"Added {count} songs to playlist")


#################
# Main function #
#################

def main():
    user = {'jon': '2252hcksg34ije4ap56y55fsq', 'andrea': 'cbddct'}
    username = user['andrea']
    print(username)
    client_id ='5c42b63580e74a5d98548a11638db40f'
    client_secret = '3492e9ea712d4d48ac81478933e0fb18'
    redirect_uri = 'http://localhost:7777/callback'
    scope = 'user-read-recently-played user-top-read playlist-modify-public playlist-modify-private playlist-read-collaborative playlist-read-private user-library-read \
        user-library-modify app-remote-control'

    token = util.prompt_for_user_token(
        username=username,
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
        )

    # token = oauth2.get_cached_token()

    sp = spotipy.Spotify(auth=token)
    pp = pprint.PrettyPrinter(indent=1, compact=True)

    create_acoustic_playlist(username, sp)

    #################
    # Test Programs #
    #################

    # print(f"Token: {token}")
    # id = get_id('Lucy', token)
    # print(f"ID: {id}")
    # features = get_features(id, token)
    # print(f"Features: {features}")
    #
    # streamings = get_streamings()
    # unique_tracks = list(set([streaming['trackName'] for streaming in streamings]))

    # unique_tracks = [("This Is the End", "The Ghost of Paul Revere"), ("Mt. Joy", "Mt. Joy"), ("Hold Me Down", "Yolk Lore"),
    #     ("Head Right -Acoustic", "Wilderado")]

    # all_features = {}
    # for track in unique_tracks:
    #     track_id = get_id(track[0], token, track[1])
    #     features = get_features(track_id, token)
    #     if features:
    #         all_features[track[0]] = features
    #
    # with_features = []
    # for track_name, features in all_features.items():
    #     with_features.append({'name': track_name, **features})

    #################################
    # Export Data Frame to CSV file #
    #################################

    # df = pd.DataFrame(with_features)
    # df.to_csv('streaming_history.csv', 'w')

if __name__ == "__main__":
    main()
