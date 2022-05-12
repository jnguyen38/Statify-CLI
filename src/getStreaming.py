import json
from math import floor

def format_time(num):
    hours = int(floor(num / 60))
    minutes = int(floor(num % 60))
    seconds = round((num % 1) * 60, 3)

    return f"{hours:02}:{minutes:02}:{seconds:02.5}"

def handle_file(openfile, track_dict):
    json_obj = json.load(openfile)

    for song in json_obj:
        tag = f"{song['trackName']} by {song['artistName']}"
        mins = song['msPlayed']/60000.0
        
        info = track_dict.get(tag, {'played':0, 'mins':0})
        info['played'] += 1
        info['mins'] += round(mins,2)
        track_dict[tag] = info


def main():
    track_dict = {}
    count_dict = {}
    total_time = 0
    total_time2 = 0
    with open("./MyData/StreamingHistory0.json", encoding='utf-8') as openfile:
         handle_file(openfile, track_dict)

    with open("./MyData/StreamingHistory1.json", encoding='utf-8') as openfile:
        handle_file(openfile, track_dict)

    with open("./MyData/StreamingHistory2.json", encoding='utf-8') as openfile:
        handle_file(openfile, track_dict)

    # for song in track_dict:
    #     print(f"{song} played for {format_time(track_dict[song])}")

    for song in track_dict:
        total_time2 += track_dict[song]['mins']
        track_dict[song]['mins'] = round(track_dict[song]['mins'], 2)

    print(round(total_time2, 2))

    json_object = json.dumps({k: v for k, v in sorted(track_dict.items(), key=lambda item: item[1]['played'], reverse=True)}, indent = 4)

    # Writing to sample.json
    with open("results.json", "w") as outfile:
        outfile.write(json_object)

if __name__ == "__main__":
    main()
