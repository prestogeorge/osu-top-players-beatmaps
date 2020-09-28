import os
import requests

from Beatmap import Beatmap
from config import Config

if __name__ == "__main__":
    BASE_URL = 'https://osu.ppy.sh'
    API_URL = BASE_URL + '/api/v2'

    MAX_USERS = 50
    MAX_SCORES = 50

    NUM_USERS = 100
    MIN_COUNT = 10

    config = Config()

    user_songs = {}
    songs = os.listdir(config.songs_path)
    for song in songs:
        id, artist_and_title = song.split(' ', 1)
        user_songs[id] = artist_and_title

    payload = {
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'grant_type': 'client_credentials',
        'scope': 'public'
    }

    r = requests.post(BASE_URL + '/oauth/token', data=payload)
    token = r.json()['access_token']

    #authorization token, use in all requests
    headers = {'Authorization': 'Bearer ' + token}

    # get the top ranked players
    users = []
    for i in range(NUM_USERS // (MAX_USERS + 1) + 1):
        r = requests.get(API_URL + '/rankings/osu/performance?page=' + str(i + 1) + '#scores', headers=headers)
        rankings = r.json()['ranking']
        users = users + [ranking['user']['id'] for ranking in rankings]
    users = users[:NUM_USERS]

    def get_time(total_length):
        seconds = total_length % 60
        minutes = total_length // 60
        return f'{minutes:d}:{seconds:02d}'

    beatmaps = {}
    # get the top 100 scores for each user
    for user in users:
        for i in range(2):
            r = requests.get(API_URL + '/users/' + str(user) + '/scores/best?limit=50&offset=' + str(i * MAX_SCORES), headers=headers)
            scores = r.json()
            for score in scores:
                beatmapset_id = str(score['beatmap']['beatmapset_id'])
                if beatmapset_id in beatmaps:
                    beatmaps[beatmapset_id].count += 1
                else:
                    beatmaps[beatmapset_id] = Beatmap(
                        count=1, 
                        title=score['beatmapset']['title'],
                        length=get_time(score['beatmap']['total_length']),
                        url='https://osu.ppy.sh/beatmapsets/' + beatmapset_id
                    )

    beatmaps = { k: v for (k, v) in beatmaps.items() if v.count >= MIN_COUNT }

    print('songs not in best performances list:')
    for (k, v) in user_songs.items():
        if k in beatmaps:
            continue
        print(v)

    beatmaps = { k: v for (k, v) in beatmaps.items() if k not in user_songs }

    print('\nsongs from best performances:')

    for beatmap in sorted(beatmaps.values(), key=lambda bm: bm.count, reverse=True):
        print(beatmap)
