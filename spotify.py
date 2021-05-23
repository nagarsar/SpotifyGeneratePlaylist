import json
import os
import re
import sys
import requests
import pandas as pd

from exceptions import ResponseException
from secrets import *
from uri import *
from util import *



def authenticate():

    query = 'https://accounts.spotify.com/api/token'

    auth_response = requests.post(query, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    response = auth_response.json()
    #print(response)
    access_token = response['access_token']
    return access_token



def refresh():

    query = 'https://accounts.spotify.com/api/token'

    auth_response = requests.post(
        query, 
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        },
        headers={
            "Authorization":"Basic " + base_64
        }
    )

    response = auth_response.json()
    #print(response)
    access_token = response['access_token']
    return access_token



def create_playlist(name):

    request_body = json.dumps({
        "name": name,
        "description": "",
        "public": False
    })

    query = "https://api.spotify.com/v1/users/{}/playlists".format(
        spotify_user_id
    )
    response = requests.post(
        query,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )
    response_json = response.json()

    # playlist id
    return response_json["id"]



def get_spotify_uri(song_name, artist):

    query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=1".format(
        song_name,
        artist
    )
    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )
    response_json = response.json()
    songs = response_json["tracks"]["items"]

    # only use the first song
    uri = songs[0]["uri"]

    return uri



def add_songs_to_playlist(playlist_id : str, uris : list):

    index=0
    max_index=len(uris)

    while(index <= max_index):

        api_uris = uris[index:index+100]
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id
        )

        request_data = json.dumps(api_uris)
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        response_json = response.json()

        if response.status_code != 200 and response.status_code != 201:
            raise ResponseException(response.status_code)

        index+=100

    return response_json



def get_artist(artist_id):

    query = "https://api.spotify.com/v1/artists/{}".format(
        artist_id
    )
    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )

    if response.status_code != 200:
        raise ResponseException(response.status_code)

    response_json = response.json()
    return response_json



def get_audio_features_several_tracks(tracks_id):

    index=0
    max_index=len(tracks_id)
    full_request = {"audio_features":[]}
    
    while(index <= max_index):

        api_tracks_id = tracks_id[index:index+100]

        query = "https://api.spotify.com/v1/audio-features/?ids={}".format(
            ','.join(api_tracks_id)
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        if response.status_code != 200:
            raise ResponseException(response.status_code)

        response_json = response.json()
        for item in response_json['audio_features']: 
            full_request['audio_features'].append(item)

        index+=100
    
    return full_request



def get_audio_features(track_id):

    query = "https://api.spotify.com/v1/audio-features/{}".format(
        track_id
    )
    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )

    if response.status_code != 200:
        raise ResponseException(response.status_code)

    response_json = response.json()
    return response_json



def get_audio_analysis(track_id):

    query = "https://api.spotify.com/v1/audio-analysis/{}".format(
        track_id
    )
    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )

    if response.status_code != 200:
        raise ResponseException(response.status_code)

    response_json = response.json()
    return response_json



def get_playlist_items(playlist_id, limit=100):

    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
        playlist_id
    )

    nb_items = 1
    offset = 0
    full_request = {"items":[]}
    response_json = {}
    
    while (nb_items > 0):

        response = requests.get(
            query,
            params={
                "market":"FR",
                "fields":"items(track(name%2Cartists))",
                "limit": limit,
                "offset":offset
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        if response.status_code != 200:
            raise ResponseException(response.status_code)
        
        response_json = response.json()

        for item in response_json['items']:
            full_request['items'].append(item)

        nb_items = len(response_json['items'])
        offset += 100

    return full_request



def export_playlist(playlist_id, output_file=""):

    playlist=[]
    tracks_id = []
    response = get_playlist_items(playlist_id)


    for item in response['items']:

        now = str(datetime.now()).split()[0]
        delta_days = get_time_delta(now, item['track']['album']['release_date'])[0]
        
        owner = multi_replace(uri_map, "spotify:playlist:"+playlist_id)

        try:
            effervescence = "{:.8f}".format(item['track']['popularity']/delta_days)
        except:
            effervescence = 0.0

        track_id = item['track']['uri'].split(':',1)[1].split(':')[1]
        tracks_id.append(track_id)

        genres = []
        for artist in item['track']['artists']:
            artist = get_artist(artist['id'])
            genres.extend(artist['genres'])

        playlist.append({
            "name": item['track']['name'],
            "artists": ', '.join(str(v['name']) for v in item['track']['artists']),
            "genres": ','.join(genres),
            "uri": item['track']['uri'],
            "popularity" : item['track']['popularity'],
            "release_date": item['track']['album']['release_date'],
            "added_at" : item['added_at'],
            "added_by" :  item['added_by']['id'],
            "delta_days": delta_days,
            "effervescence": effervescence,
            "owner": owner,
            "now": now,
        })

    features = get_audio_features_several_tracks(tracks_id)

    for track in playlist:
        for feature in features['audio_features']:
            if track['uri'] == feature['uri']:
                track.update({
                    "danceability":feature['danceability'],
                    "energy":feature['energy'],
                    "key":feature['key'],
                    "loudness":feature['loudness'],
                    "mode":feature['mode'],
                    "speechiness":feature['speechiness'],
                    "acousticness":feature['acousticness'],
                    "instrumentalness":feature['instrumentalness'],
                    "liveness":feature['liveness'],
                    "valence":feature['valence'],
                    "tempo":feature['tempo'],
                })

    df = pd.DataFrame(playlist)
    if output_file!="":
        df.to_csv(output_file, sep='|', index=False)
        print("generated playlist %s with %d tracks in %s" % (playlist_id, len(playlist), output_file))
    
    return playlist




def textfile_to_playlist(input_file, playlist_name):
    
    # input_file : single column file
    
    bad_characters={'feat':'', '.':'', '&':'', '.ft':'','Pt.':'', '(':'', 
                    ')':'', '-':'', '\u200e':'', ',':'', '\n':'', '\r':'', 
                    '–':'—'}

    log_file='textfile_to_playlist.log'
    uris=[]
    
    if 1==1:
        os.system("printf '\n\nlogging "+input_file+" at "+str(datetime.now())+"\n------------------------------\n' >> "+log_file)    
        with open(input_file, 'r', newline="\n") as f:
            for l in f:
                l = multi_replace(bad_characters,l)
                print(l)
                try:
                    artist_name, song_name = l.split(' — ')
                    try:
                        uri = get_spotify_uri(song_name=song_name ,artist=artist_name)
                        uris.append(uri)
                    except:
                        uri = ''
                    os.system("printf '"+artist_name+" - "+song_name+" : "+uri+"\n' >> "+log_file)
                except:
                    os.system("printf '"+l+" not splitable... \n' >> "+log_file)

    if 1==0:
        # Assuming the previous step failed in between
        os.system("grep -E 'spotify:track:' "+log_file+" > gh0stfile")
        with open('gh0stfile','r',newline="\n") as f:
            for l in f:
                uri = 'spotify:track:'+l.split('spotify:track:')[1].replace('\n','')
                uris.append(uri)
        os.system("rm -f gh0stfile")


    playlist_id = create_playlist(name=playlist_name)
    add_songs_to_playlist(playlist_id=playlist_id, uris=uris)



def multi_replace(replacement_dict, text):
    regex = re.compile("|".join(map(re.escape, replacement_dict.keys(  ))))
    return regex.sub(lambda match: replacement_dict[match.group(0)], text)



def project_1(
    output_file, 
    uris:list, 
    genres=[], 
    top=None):

    df_main = pd.DataFrame()
    for uri in uris:
        sys.stdout.write("\rprocessing: %d/%d\n" % (uris.index(uri)+1,len(uris)))
        p_id = uri.split(':',1)[1].split(':')[1]
        playlist = export_playlist(p_id)
        df = pd.DataFrame(playlist)
        df_main = df_main.append(df)
        df_main.to_csv(output_file, sep='|', index=False)

    # sort by column effervescence
    df_main["effervescence"] = pd.to_numeric(df_main["effervescence"])
    df_main = df_main.sort_values(by=["effervescence"], ascending=False)
    
    # keep rows containing the genres mentionned
    if len(genres) > 0:
        df_main = df_main[df_main['genres'].str.contains('|'.join(genres), na=False)]
    
    df_main = df_main.drop_duplicates()

    if top != None:
        df_main = df_main.head(top)

    print("generating %s" % output_file)
    df_main.to_csv(output_file, sep='|', index=False)


if __name__ == '__main__':
    

    if 1==1:
        spotify_token = refresh() # /!\ refer readme or replace by a temporary one generated from spotify developper console


    if 1==0:
        playlist_id = create_playlist(name="zoubida42")


    if 1==1:
        uris = []
        uris.append(get_spotify_uri(song_name="1992", artist="No_4mat"))
        uris.append(get_spotify_uri(song_name="maputo jam", artist="cuthead"))
        uris.append(get_spotify_uri(song_name="a tribe called quest", artist="jazz we've got"))
        add_songs_to_playlist(playlist_id=playlist_id, uris=uris)
    

    if 1==0:
        #os.system("awk -F'|' '{print $2}' tracklist2_columns > tracklist1_column")
        textfile_to_playlist(input_file="tracklist1_column", playlist_name="tracklist")


    if 1==0:
        export_playlist(playlist_id="1kpSDuSKe3gIWtdY8XQ7a1", output_file=".001.csv")


    if 1==0:
        # merge all playlists from uris list
        # sort by indicators e.g: effervesence (home made indicator)
        # sort by genres
        # keep the top 10
        uris=['spotify:playlist:1kpSDuSKe3gIWtdY8XQ7a1']
        genres=['chillhop','canadian']
        project_1(
            output_file="project_1.csv", 
            uris=uris, 
            genres=genres, 
            top=10) 
