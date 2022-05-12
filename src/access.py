import json
import requests
import pandas as pd
import pprint
import generator as gen
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
    try:
        features = sp.audio_features([track_id])
        return features[0]
    except:
        return None


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

##########################
# Handle Song Generators #
##########################

def handle_song_generator(sp, info: dict, uri_dict: dict, database, attr: str, threshhold, playlist_id: str, suppress: bool, count):
    attr_dict = {'acousticness': 'Not acoustic enough', 'danceability': 'Not dancy enough', 'energy': 'Not energetic enough',
        'loudness': 'Not loud enough', 'liveness': 'Probably not live'}

    if info['uri'] in database:
        feature = database[info['uri']]
    else:
        feature = get_features(sp, info['uri'])
        database[info['uri']] = feature

    if info['uri'] not in uri_dict:
        if feature:
            if feature[attr] > threshhold:
                try:
                    sp.playlist_add_items(playlist_id, [info['uri']])
                    print(f"{grey}({count}) {green}Added song: {default}{info['name']}: {feature[attr]}")
                    return True
                except:
                    pass
            elif not suppress:
                print(f"{grey}({count}) {red}{attr_dict[attr]}: {default}{info['name']}: {feature[attr]}")
        else:
            print(f"{red}Error:{default} Received {red}None{default} type for {info['name']}")
            cont = input("Continue? ")
            if cont == 'N' or cont == 'n' or cont == 'no' or cont == 'No':
                quit()
        uri_dict[info['uri']] = 1
    elif not suppress:
        print(f"{grey}({count}) {blue}Song exists/already seen: {default}{info['name']}")

    return False

##############################
# Generate acoustic playlist #
##############################

def create_playlist(sp, playlist_type: str, op: str, username: str, threshhold, suppress: bool, artist_lim):
    # Initialize dictionaries
    uri_dict = {}
    type_dict = {'acousticness': {'title': "Acoustic - Auto-Generated", 'desc': "Auto-generated acoustic playlist"},
        'danceability': {'title': "Dance - Auto-Generated", 'desc': "Auto-generated danceable playlist"},
        'energy' : {'title': 'Energizing - Auto-Generated', 'desc': 'Auto-generated energetic playlist'},
        'loudness' : {'title': 'LOUD - Auto-Generated', 'desc': 'Auto-generated loud music playlist'},
        'liveness' : {'title': 'Live - Auto-Generated', 'desc': 'Auto-generated live music playlist'}}

    # Get playlist id (Create or find the id)
    print("Searching Playlists...")
    params = type_dict[playlist_type]
    playlist_id = get_playlist_id(sp=sp, username=username, create=True, playlist_name=params['title'], playlist_desc=params['desc'])

    # Get dictionary of playlist songs
    print("\nGetting Playlist Songs...")
    uri_dict = get_playlist_songs_dict(sp=sp, playlist_id=playlist_id)
    print("Playlist Songs Received\n")

    # Get dictionary of locally saved songs
    print("\nGetting Database Songs...")
    read_file = open("./data/song_database.json", "r")
    database = json.load(read_file)
    print("Database Songs Received\n")

    # Generate Library, Filter acoustic songs
    added = 0
    count = 1
    total = 0

    # Search through liked songs
    if op =='liked' or op == 'all':
        print("\nGenerating Liked Songs...")
        for info in gen.generate_from_library(sp=sp):
            if handle_song_generator(sp, info, uri_dict, database, playlist_type, threshhold, playlist_id, suppress, count):
                added += 1
            count += 1
        total += (count - 1)

    # Search through top songs
    if op == 'top' or op == 'all':
        range_list = ['short_term', 'medium_term', 'long_term']
        range_dict = {'short_term': '\nYour top songs of the past month', 'medium_term': '\nYour top songs of the past 6 months',
            'long_term': '\nYour top songs of all time'}

        print("\nGenerating Top Songs...")
        for range in range_list:
            count = 1
            print(range_dict[range])
            for info in gen.generate_from_top(sp, top_range=range):
                if handle_song_generator(sp, info, uri_dict, database, playlist_type, threshhold, playlist_id, suppress, count):
                    added += 1
                count += 1
            total += (count - 1)

    # Search through playlist songs
    if op == 'playlists' or op == 'all':
        count = 1
        print("\nGenerating Playlist Songs...")
        for info in gen.generate_from_playlists(sp=sp):
            last_count = count
            count = info['count']
            if handle_song_generator(sp, info, uri_dict, database, playlist_type, threshhold, playlist_id, suppress, count):
                added += 1
            if last_count > count:
                total += (last_count - 1)

    # Search through top artists
    if op == 'artists' or op == 'all':
        range_list = ['short_term', 'medium_term', 'long_term']
        range_dict = {'short_term': '\nYour top artists of the past month', 'medium_term': '\nYour top artists of the past 6 months',
            'long_term': '\nYour top artists of all time'}
        count = 1
        print("\nGenerating Artist Songs...")
        for range in range_list:
            count = 1
            print(range_dict[range])
            for info in gen.generate_from_artists(sp=sp, top_range=range):
                # count, added = handle_song_generator(sp, info, playlist_type, threshhold, playlist_id, playlist_dict, suppress, count, added)
                print(f"{count:>3}. {info['name']}")
                count += 1

    print(f"\nAdded {added} songs to playlist out of {total} songs analyzed\n")

    # Dump database to json file
    write_file = open("./data/song_database.json", "w")
    json.dump(database, write_file)
