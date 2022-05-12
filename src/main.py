#################
# Main function #
#################
#
#   This holds the main function execution
#

import os
import access
import spotipy
import spotipy.util as util
import pprint
import access
from colored import fg

red = fg(196)
default = fg(254)
green = fg(40)
blue = fg(69)
grey = fg(243)

def main():
    print(default)
    os.system('cls' if os.name == 'nt' else 'clear')

    user = 'jon'
    user_dict = {'jon': '2252hcksg34ije4ap56y55fsq', 'andrea': 'cbddct', 'donny': 'k8vhilc5vejkzlcivj2d4v61e', 'perc': 'ajhennessee',
        'lo': 'laurenostdiek', 'sleepy':'brookemack910'}
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

    test = False

    if not test:
        playlist_type_list = ['acousticness', 'danceability', 'energy', 'loudness', 'liveness']
        playlist_type = int(input("Pick a playlist type (Choose a number):\n\
        1. Acoustic Music\n\
        2. Danceable Music\n\
        3. Energetic Music\n\
        4. Loud Music\n\
        5. Live Music\n> ")) - 1

        op_list = ['top', 'liked', 'playlists', 'artists', 'all']
        op = int(input("\nPick a song source (Choose a number):\n\
        1. From my most listened to songs\n\
        2. From my liked songs library\n\
        3. From my playlists\n\
        4. From my artists\n\
        5. All available sources\n> ")) - 1

        artist_lim = 0
        if op == 3 or op == 4:
            artist_lim = int(input("\nHow many top songs per artist?\n> "))

        threshhold = float(input("\nInput song threshold (0.00 - 1.00)\n> "))

        suppress = False
        # suppress = input("\nSuppress output? (Y or N)\n> ")
        # if suppress == 'Y':
        #     suppress = True
        # else:
        #     suppress = False

        access.create_playlist(sp=sp, playlist_type=playlist_type_list[playlist_type], op=op_list[op], username=username, threshhold=threshhold,
            suppress=suppress, artist_lim=artist_lim)

    else:
        rec = sp.current_user_recently_played()
        while rec:
            for num, song in enumerate(rec['items']):
                print(num, song['track']['name'])
            if rec['next']:
                rec = sp.next(rec)
            else:
                rec = None


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
