import os
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
import requests
import pandas as pd
import pprint
from colored import fg

red = fg(196)
default = fg(254)
green = fg(40)
blue = fg(69)
grey = fg(243)

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

##########################
# Get features of a song #
##########################
# Return value:
#   On success, get_features() returns a dictionary with the
#       following keys:
#       ['danceability', 'energy', 'key', 'loudness', 'mode',
#        'speechiness', 'acousticness', 'instrumentalness', 'liveness',
#        'valence', 'tempo', 'type', 'id', 'uri', 'track_href',
#        'analysis_url', 'duration_ms', 'time_signature']

def get_features(sp, track_id: str) -> dict:
    pp = pprint.PrettyPrinter(indent=1, compact=True)

    try:
        features = sp.audio_features([track_id])
        # pp.pprint(features[0])
        yield features[0]
    except:
        yield None


############################
# SONG GENERATOR FUNCTIONS #
############################

##########################
# Generate Library songs #
##########################

def generate_from_library(sp):
    songs = sp.current_user_saved_tracks()
    print(f"There are {blue}{songs['total']} {default}songs in your library")

    while songs:
        for song in songs['items']:
            song_name   = song['track']['name']
            # song_artist = song['track']['artists'][0]['name']
            # song_pop    = song['track']['popularity']
            song_uri    = song['track']['uri']
            try:
                # print(f"{num+offset}: {song_name} by {song_artist}\n\tPopularity: {song_pop}, URI: {song_uri}\n")
                yield {'uri': song_uri, 'name': song_name}
            except:
                pass
        if songs['next']:
            songs = sp.next(songs)
        else:
            songs = None


######################
# Generate top songs #
######################

def generate_from_top(sp, top_limit=50, top_range='medium_term'):
    songs = sp.current_user_top_tracks(time_range=top_range)
    while songs:
        for song in songs['items']:
            song_name   = song['name']
            # song_artist = song['track']['artists'][0]['name']
            # song_pop    = song['track']['popularity']
            song_uri    = song['uri']
            try:
                # print(f"{num+offset}: {song_name} by {song_artist}\n\tPopularity: {song_pop}, URI: {song_uri}\n")
                yield {'uri': song_uri, 'name': song_name}
            except:
                pass
        if songs['next']:
            songs = sp.next(songs)
        else:
            songs = None


#################################
# Generate songs from playlists #
#################################
#
# ['collaborative', 'description', 'external_urls',
#  'href', 'id', 'images', 'name', 'owner', 'primary_color',
#  'public', 'snapshot_id', 'tracks', 'type', 'uri']

def generate_from_playlists(sp):
    user_playlist_info = sp.current_user_playlists()
    pp = pprint.PrettyPrinter(indent=1, compact=True)
    total = 0

    while user_playlist_info:
        for playlist in user_playlist_info['items']:
            print(f"\n'{playlist['name']}' by {playlist['owner']['display_name']} ({playlist['owner']['id']})")
            songs = sp.playlist_tracks(playlist['id'])
            while songs:
                for count, song in enumerate(songs['items']):
                    song_name   = song['track']['name']
                    # song_artist = song['track']['artists'][0]['name']
                    # song_pop    = song['track']['popularity']
                    song_uri    = song['track']['uri']
                    try:
                        # print(f"{num+offset}: {song_name} by {song_artist}\n\tPopularity: {song_pop}, URI: {song_uri}\n")
                        total = total + 1
                        yield {'uri': song_uri, 'name': song_name, 'count': count + total + 1}
                    except:
                        pass
                if songs['next']:
                    songs = sp.next(songs)
                else:
                    songs = None
        if user_playlist_info['next']:
            user_playlist_info = sp.next(user_playlist_info)
        else:
            user_playlist_info = None


#########################################
# Create a playlist and get playlist id #
#########################################
# Parameters:
#   playlist_name: What you want to name the playlist/search for
#   playlist_desc (optional): What you want the playlist description
#   username: username of the current user
#   sp: spotipy.Spotify() client with auth token
#
# Return value:
#   On success, the function will return the playlist id string
#       of the created/found playlist

def get_playlist_id(sp, username: str, create: bool, playlist_name: str, playlist_desc: str = '') -> str:

    # Cycle through all user playlists to see if playlist already exists
    playlist_exists = False
    user_playlist_info = sp.current_user_playlists()
    num_playlists = user_playlist_info['total']
    print(f"There are {blue}{num_playlists} {default}playlists in your library")

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
    if not playlist_exists and create:
        playlist_info = sp.user_playlist_create(username, playlist_name, description=playlist_desc)
        playlist_id = playlist_info['id']
        print("Playlist created")
    else:
        print("Playlist not created")

    return playlist_id


#####################################
# Generate existing song dictionary #
#####################################
# Parameters:
#   playlist_id: The id string of the playlist you want to
#       find the songs of
#   sp: spotipy.Spotify() client with auth token
#
# Return value:
#   On success, the function will return a dictionary of all
#       songs in the playlist with uri as the key and the
#       song name as the value - { uri : name, ... }

def get_playlist_songs_dict(sp, playlist_id: str) -> dict:
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


def handle_song_generator(sp, info: dict, attr: str, threshhold, playlist_id: str, playlist_dict: dict, count, added):
    attr_dict = {'acousticness': 'acoustic', 'danceability': 'dancy'}
    if info['count']:
        count = info['count']
    for feature in get_features(sp, info['uri']):
        if feature:
            if feature[attr] > threshhold:
                try:
                    if info['uri'] not in playlist_dict:
                        sp.playlist_add_items(playlist_id, [info['uri']])
                        print(f"{grey}({count}) {green}Added song: {default}{info['name']}: {feature[attr]}")
                        playlist_dict[info['uri']] = info['name']
                        added = added + 1
                    else:
                        print(f"{grey}({count}) {blue}Song already exists: {default}{info['name']}")
                except:
                    pass
            else:
                print(f"{grey}({count}) {red}Not {attr_dict[attr]} enough: {default}{info['name']}: {feature[attr]}")
        else:
            print(f"{red}Error:{default} Received {red}None{default} type for {info['name']}")
            cont = input("Continue? ")
            if cont == 'N' or cont == 'n' or cont == 'no' or cont == 'No':
                quit()
    count = count + 1

    return count, added

##############################
# Generate acoustic playlist #
##############################

def create_playlist(sp, playlist_type: str, op: str, username: str, threshhold):
    # Initialize type_dict
    type_dict = {'acousticness': {'title': "Acoustic - Auto-Generated", 'desc': "Auto-generated acoustic playlist"},
        'danceability': {'title': "Dance - Auto-Generated", 'desc': "Auto-generated danceable playlist"}}

    # Get playlist id (Create or find the id)
    print("Searching Playlists...")
    params = type_dict[playlist_type]
    playlist_id = get_playlist_id(sp=sp, username=username, create=True, playlist_name=params['title'], playlist_desc=params['desc'])

    # Get dictionary of playlist songs
    print("\nGetting Playlist Songs...")
    playlist_dict = get_playlist_songs_dict(sp=sp, playlist_id=playlist_id)
    print("Playlist Songs Received\n")

    ###########################################
    # Generate Library, Filter acoustic songs #
    ###########################################

    added = 0
    count = 1

    # Search through liked songs
    if op =='liked':
        print("Generating Liked Songs...")
        for info in generate_from_library(sp=sp):
            count, added = handle_song_generator(sp, info, playlist_type, threshhold, playlist_id, playlist_dict, count, added)

    elif op == 'top':
        print("Generating Top Songs...")
        print("\nYour top songs of the past month")
        for info in generate_from_top(sp, top_range='short_term'):
            count, added = handle_song_generator(sp, info, playlist_type, threshhold, playlist_id, playlist_dict, count, added)

        count = 1
        print("\nYour top songs of the past 6 months")
        for info in generate_from_top(sp, top_range='medium_term'):
            count, added = handle_song_generator(sp, info, playlist_type, threshhold, playlist_id, playlist_dict, count, added)

        count = 1
        print("\nYour top songs of all time")
        for info in generate_from_top(sp, top_range='long_term'):
            count, added = handle_song_generator(sp, info, playlist_type, threshhold, playlist_id, playlist_dict, count, added)

    elif op == 'playlists':
        print("Generating Playlist Songs...")
        for info in generate_from_playlists(sp=sp):
            count, added = handle_song_generator(sp, info, playlist_type, threshhold, playlist_id, playlist_dict, count, added)

    print(f"Added {added} songs to playlist")


#################
# Main function #
#################

def main():
    print(default)
    os.system('cls' if os.name == 'nt' else 'clear')

    user = 'perc'
    user_dict = {'jon': '2252hcksg34ije4ap56y55fsq', 'andrea': 'cbddct', 'donny': 'k8vhilc5vejkzlcivj2d4v61e', 'perc': 'ajhennessee'}
    username = user_dict[user]
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
    curr_user_info = sp.current_user()
    curr_user = curr_user_info['display_name']
    print(f"User: {blue}{user}{default}, User_ID: {blue}{username}{default}, Logged In As: {blue}{curr_user}{default}")

    # playlist_type = input("Input playlist type ('acousticness', 'danceability')\n> ")
    # op = input("Input song source(s) ('top', 'liked', 'playlists', 'artists')\n> ")
    # threshhold = input("Input song threshold\n> ")

    create_playlist(sp=sp, playlist_type='acousticness', op='playlists', username=username, threshhold=.8)

    # # id = get_id('Memories (feat. Kid Cudi) - 2021 Remix', token, 'David Guetta')
    # id = get_id('This is the end', token, 'The Ghost of Paul Revere')
    # for feature in get_features(sp, id):
    #     print(feature)

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
