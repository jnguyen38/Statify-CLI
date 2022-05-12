############################
# SONG GENERATOR FUNCTIONS #
############################
#
#   This module handles all of the song
#   generator functions. Each generator
#   yields an info dict of at least a URI
#   and a song name that can be accessed
#   by the handler.
#

from colored import fg
import pprint

red = fg(196)
default = fg(254)
green = fg(40)
blue = fg(69)
grey = fg(243)

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
    num_playlists = user_playlist_info['total']
    pp = pprint.PrettyPrinter(indent=1, compact=True)
    song_total = 1
    added_per = 0
    playlist_total = 1

    while user_playlist_info:
        for playlist in user_playlist_info['items']:
            print(f"\n{grey}(Playlist {playlist_total}/{num_playlists}) {default}{green}{playlist['name']}{default} by {playlist['owner']['display_name']} ({playlist['owner']['id']})")

            playlist_total += 1
            song_total = 1
            if playlist['owner']['id'] == sp.current_user()['id'] and 'Auto-Generated' not in playlist['name']:
                songs = sp.playlist_tracks(playlist['id'])
                while songs:
                    for song in songs['items']:
                        if song and song['track']:
                            song_name   = song['track']['name']
                            # song_artist = song['track']['artists'][0]['name']
                            # song_pop    = song['track']['popularity']
                            song_uri    = song['track']['uri']
                            try:
                                # print(f"{num+offset}: {song_name} by {song_artist}\n\tPopularity: {song_pop}, URI: {song_uri}\n")
                                yield {'uri': song_uri, 'name': song_name, 'count': song_total}
                            except:
                                pass
                            song_total += 1
                    if songs['next']:
                        songs = sp.next(songs)
                    else:
                        songs = None
            else:
                print("Playlist Skipped")
        if user_playlist_info['next']:
            user_playlist_info = sp.next(user_playlist_info)
        else:
            user_playlist_info = None


def generate_from_artists(sp, top_limit=20, top_range='medium_term'):
    artists = sp.current_user_top_artists(time_range=top_range)
    while artists:
        for artist in artists['items']:
            artist_name   = artist['name']
            # song_artist = song['track']['artists'][0]['name']
            # song_pop    = song['track']['popularity']
            artist_uri    = artist['uri']
            try:
                # print(f"{num+offset}: {song_name} by {song_artist}\n\tPopularity: {song_pop}, URI: {song_uri}\n")
                yield {'uri': artist_uri, 'name': artist_name}
            except:
                pass
        if artists['next']:
            artists = sp.next(artists)
        else:
            artists = None
