# Spotify tools

Setup permanent access to spotify API using refresh tokens  
Export your spotify playlists into files with genres and features  
Create playlists from text files  


## Technologies
* [Spotify Web API]
* [Requests Library v 2.22.0]


## LocalSetup
1) Install All Dependencies   
`pip3 install -r requirements.txt`



# Steps to get access and refresh tokens

### create an app  
from: https://developer.spotify.com/dashboard/
input a redirect uri e.g : https://example.com/callback  
save client_id, client_secrect, redirect_uri


### encode the callback url

    https://example.com/callback => https%3A%2F%2Fexample.com%2Fcallback


### encode client_id:client_secret in base64

    dc68ed368b84455a9467586a4b1fceb8:82153ff2523c4308a68ec05c8e028ef2 => Zio4d.. =


### encode scope of permissions separated by spaces 

    scope='user-top-read playlist-modify-public user-modify-playback-state playlist-modify-private user-library-modify playlist-read-private user-library-read playlist-read-collaborative' => user-top-read%20playlist-modify-public%20user-modify-playback-state%20playlist-modify-private%20user-library-modify%20playlist-read-private%20user-library-read%20playlist-read-collaborative


### create a url like follow

    https://accounts.spotify.com/authorize?client_id=dc68ed368b84455a9467586a4b1fceb8&response_type=code&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&scope=user-top-read%20playlist-modify-public%20user-modify-playback-state%20playlist-modify-private%20user-library-modify%20playlist-read-private%20user-library-read%20playlist-read-collaborative


### paste the url and get the access token
    code=AQDiJpEFDX1Ge9Mi0b-pzugWCZOIIcHAWnz-0BfLI60pbd2rkcqX5VeN1moCrwXIASIZi-pnKnL9Ww8YSp_pdAnOh1VT_VbHe1hdKY3wxdBfDMVdqsY39TjCxJ3twl0kjGMlk-qOCvY0m48wUJO7rwj4brbof-VcU9_QoLbEvpRy4CaPJgY9KG5LRPPCW5I0MZJKDoHc89fKB_QHCCFz4b9yLmDTCHr70aibhdpZWy2S4bddqi_AN8uCKKqqm5umWmNcneRnDXdWMnhAe2pOiHJBTMt-79RrYUnXFXk46wKpgBUO2DkZGmyqlWbg_OWiWNPO5Fk5GhbqBIiX8zs0PNzUP2QT8-vrDeTyUU6iykDxuEUnnuLOEvnNCI4s9cTUADy6KWGaFX4reUqJVgXXf2ejBBdwmgJ6


### compose a curl request 
refer:https://developer.spotify.com/documentation/general/guides/authorization-guide/  

put the base_64 code after 'Basic'  
put the access token after code=  
mention the encoded callback  
finally put the endpoint url: https://accounts.spotify.com/api/token  

    curl -H "Authorization: Basic ZGM2OGVkMzY4Yjg0NDU1YTk0Njc1ODZhNGIxZmNlYjg6ODIxNTNmZjI1MjNjNDMwOGE2OGVjMDVjOGUwMjhlZjI=" -d grant_type=authorization_code -d code=AQDiJpEFDX1Ge9Mi0b-pzugWCZOIIcHAWnz-0BfLI60pbd2rkcqX5VeN1moCrwXIASIZi-pnKnL9Ww8YSp_pdAnOh1VT_VbHe1hdKY3wxdBfDMVdqsY39TjCxJ3twl0kjGMlk-qOCvY0m48wUJO7rwj4brbof-VcU9_QoLbEvpRy4CaPJgY9KG5LRPPCW5I0MZJKDoHc89fKB_QHCCFz4b9yLmDTCHr70aibhdpZWy2S4bddqi_AN8uCKKqqm5umWmNcneRnDXdWMnhAe2pOiHJBTMt-79RrYUnXFXk46wKpgBUO2DkZGmyqlWbg_OWiWNPO5Fk5GhbqBIiX8zs0PNzUP2QT8-vrDeTyUU6iykDxuEUnnuLOEvnNCI4s9cTUADy6KWGaFX4reUqJVgXXf2ejBBdwmgJ6 -d redirect_uri=https%3A%2F%2Fexample.com%2Fcallback https://accounts.spotify.com/api/token


### save the refresh token

preferably in a secret file ...


### use the refresh token to generate an access token every time you want to query spotify api

get an access token by using a code like follow:


    def refresh():

        import requests

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
        print(response)
        access_token = response['access_token']
        return access_token


   [Spotify Web API]: <https://developer.spotify.com/documentation/web-api/>
   [Requests Library v 2.22.0]: <https://requests.readthedocs.io/en/master/>
   [Account Overview]: <https://www.spotify.com/us/account/overview/>
   [Get Oauth]: <https://developer.spotify.com/console/post-playlists/>
