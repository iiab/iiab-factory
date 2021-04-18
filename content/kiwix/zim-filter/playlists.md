### Playlists Program Manipulates Youtube Playlists
* Google has established a complicated process for a program to get permission from the owner of a channel (A channel is the storage unit for an individual Google user identity).
* The '-a' '--authenticate' option of the ```Playlist``` program starts up a local server on port 8088 which interacts with Google-Youtube, and the owner of a channel so that the owner can grant privileges to modify the data in the owner's channel. 


```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# List, create, delete playlists, authenticate access to Youtube 
import os,sys
import json
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Operate on Youtube Playlists that belong to you.")
    parser.add_argument("-a","--authenticate", help='Start local authentication on port 8088.',action='store_true')
    parser.add_argument("-c","--create", help='Create playlist with this name.')
    parser.add_argument("-d","--delete", help='Delete listed item by number.',type=int)
    parser.add_argument("-l","--list", help='List numbers,names,itemCount in Channel.',action='store_true')
    return parser.parse_args()

def human_readable(num):
    # return 3 significant digits and unit specifier
    num = float(num)
    units = [ '','K','M','G']
    for i in range(4):
        if num<10.0:
            return "%.2f%s"%(num,units[i])
        if num<100.0:
            return "%.1f%s"%(num,units[i])
        if num < 1000.0:
            return "%.0f%s"%(num,units[i])
        num /= 1024.0
```


```python
# This cell creates an authenticated youtube object which has methods described in:
#   in https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.html

import google.oauth2.credentials
import googleapiclient.discovery

# The User validated google credentials are in my home directory
home = os.environ['HOME']
with open("%s/zim_playbook_oauth_credentials"%home,'r') as fp:
    credentials = json.loads(fp.read())
    
# Load credentials from file
credentials = google.oauth2.credentials.Credentials(**credentials)
 
youtube = googleapiclient.discovery.build(
    'youtube', 'v3', credentials=credentials)

channel = youtube.channels().list(mine=True, part='snippet').execute()

# check that the authentication worked
#print(json.dumps(channel,indent=2))
```


```python
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import json

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
HOME = os.environ['HOME']
CLIENT_SECRETS_FILE = HOME + "/.youtube_client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
# Where to write the returned google credentials
CREDENTIALS_FILE = HOME + '/.youtube_oauth_credentials'

def youtube_authorize():
    app = flask.Flask(__name__)
    # Note: A secret key is included in the sample so that it works.
    # If you use this code in your application, replace this with a truly secret
    # key. See https://flask.palletsprojects.com/quickstart/#sessions.
    #app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
    app.secret_key = 'AIzaSyBWvv2Hnhak_VufcnIV2Xs9NVLEtk-wzoo'


    @app.route('/')
    def index():
      return print_index_table()


    @app.route('/test')
    def test_api_request():
      if 'credentials' not in flask.session:
        return flask.redirect('authorize')

      # Load credentials from the session.
      credentials = google.oauth2.credentials.Credentials(
          **flask.session['credentials'])

      # Write the credentials for future use elsewhere
      with open(CREDENTIALS_FILE,'w') as fp:
          fp.write(json.dumps(flask.session['credentials'],indent=2))

      youtube = googleapiclient.discovery.build(
          API_SERVICE_NAME, API_VERSION, credentials=credentials)

      channel = youtube.channels().list(mine=True, part='snippet').execute()

      # Save credentials back to session in case access token was refreshed.
      # ACTION ITEM: In a production app, you likely want to save these
      #              credentials in a persistent database instead.
      flask.session['credentials'] = credentials_to_dict(credentials)

      return flask.jsonify(**channel)


    @app.route('/authorize')
    def authorize():
      # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
      flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
          CLIENT_SECRETS_FILE, scopes=SCOPES)

      # The URI created here must exactly match one of the authorized redirect URIs
      # for the OAuth 2.0 client, which you configured in the API Console. If this
      # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
      # error.
      flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

      authorization_url, state = flow.authorization_url(
          # Enable offline access so that you can refresh an access token without
          # re-prompting the user for permission. Recommended for web server apps.
          access_type='offline',
          # Enable incremental authorization. Recommended as a best practice.
          include_granted_scopes='true')

      # Store the state so the callback can verify the auth server response.
      flask.session['state'] = state

      return flask.redirect(authorization_url)


    @app.route('/oauth2callback')
    def oauth2callback():
      # Specify the state when creating the flow in the callback so that it can
      # verified in the authorization server response.
      state = flask.session['state']

      flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
          CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
      flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

      # Use the authorization server's response to fetch the OAuth 2.0 tokens.
      authorization_response = flask.request.url
      flow.fetch_token(authorization_response=authorization_response)

      # Store credentials in the session.
      # ACTION ITEM: In a production app, you likely want to save these
      #              credentials in a persistent database instead.
      credentials = flow.credentials
      flask.session['credentials'] = credentials_to_dict(credentials)

      return flask.redirect(flask.url_for('test_api_request'))


    @app.route('/revoke')
    def revoke():
      if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

      credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

      revoke = requests.post('https://oauth2.googleapis.com/revoke',
          params={'token': credentials.token},
          headers = {'content-type': 'application/x-www-form-urlencoded'})

      status_code = getattr(revoke, 'status_code')
      if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
      else:
        return('An error occurred.' + print_index_table())


    @app.route('/clear')
    def clear_credentials():
      if 'credentials' in flask.session:
        del flask.session['credentials']
      return ('Credentials have been cleared.<br><br>' +
              print_index_table())


    def credentials_to_dict(credentials):
      return {'token': credentials.token,
              'refresh_token': credentials.refresh_token,
              'token_uri': credentials.token_uri,
              'client_id': credentials.client_id,
              'client_secret': credentials.client_secret,
              'scopes': credentials.scopes}

    def print_index_table():
      return ('<table>' +
              '<tr><td><a href="/test">Test an API request</a></td>' +
              '<td>Submit an API request and see a formatted JSON response. ' +
              '    Go through the authorization flow if there are no stored ' +
              '    credentials for the user.</td></tr>' +
              '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
              '<td>Go directly to the authorization flow. If there are stored ' +
              '    credentials, you still might not be prompted to reauthorize ' +
              '    the application.</td></tr>' +
              '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
              '<td>Revoke the access token associated with the current user ' +
              '    session. After revoking credentials, if you go to the test ' +
              '    page, you should see an <code>invalid_grant</code> error.' +
              '</td></tr>' +
              '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
              '<td>Clear the access token currently stored in the user session. ' +
              '    After clearing the token, if you <a href="/test">test the ' +
              '    API request</a> again, you should go back to the auth flow.' +
              '</td></tr></table>')

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8088, debug=True)

```

     * Serving Flask app "__main__" (lazy loading)
     * Environment: production
    [31m   WARNING: This is a development server. Do not use it in a production deployment.[0m
    [2m   Use a production WSGI server instead.[0m
     * Debug mode: on


     * Running on http://localhost:8088/ (Press CTRL+C to quit)
     * Restarting with stat



    An exception has occurred, use %tb to see the full traceback.


    SystemExit: 1



    /home/ghunt/miniconda3/lib/python3.9/site-packages/IPython/core/interactiveshell.py:3445: UserWarning: To exit: use 'exit', 'quit', or Ctrl-D.
      warn("To exit: use 'exit', 'quit', or Ctrl-D.", stacklevel=1)



```python
def get_my_playlists():
    global my_playlists
    playlists_list_response = youtube.playlists().list(
        part='contentDetails,snippet',
        mine = True
        ).execute()
    my_playlists = []
    for item in playlists_list_response['items']:
        my_playlists.append([item['id'],item['snippet']['title'],item['contentDetails']['itemCount']])
    return my_playlists

```

    1 ['PLs2auPpToJpb0ttyGab3c5h5XUn7dXE-9', 'youtube2zim', 0]
    2 ['PLs2auPpToJpbDRe9sh5nbeXRviOI4HpAL', 'youtube2zim', 1]
    3 ['PLs2auPpToJpb6MeiaKEIpkdSWeBVgvC_p', 'top-ted', 0]



```python
def delete_playlist(list_index):
    my_playlists = get_my_playlists()
    if list_index not in range(1,len(my_playlists)+1):
        print('Please use the Playlist index from the list command')
        return
    response = input('Do you want to delete %s? y/N'%my_playlists[list_index-1][1])
    if response != 'Y' and response != 'y':
        print('Aborting Delete')
        return
    response = youtube.playlists().delete(id=my_playlists[list_index-1][0]).execute()
    print(response)
```


```python
def add_playlist(title):
  body = dict(
    snippet=dict(
      title=title,
      description="This is a temporary Playslist which is used as source for the Openzim 'youtube2zim' program."
    ),
    status=dict(
      privacyStatus='public'
    ) 
  ) 
  playlists_insert_response = youtube.playlists().insert(
    part='snippet,status',
    body=body
  ).execute()
  print('New playlist ID: %s' % playlists_insert_response['id'])
```


```python
def main():
   global args
   args = parse_args()
   if args.create:
       print('Create %s'%args.create)
       add_playlist(args.create)
       sys.exit(0)
   if args.list:
        print('list')
        my_playlists = get_my_playlists()
        num = 1
        for pl in my_playlists:
            print(num,pl)
            num += 1
        sys.exit(0)
   if args.delete:
        print('delete number %s'%args.delete)
        delete_playlist(args.delete)
        sys.exit(0)
   if args.authenticate:
        youtube_authorize()  # this will 
        print('authenticate')


    
if __name__ == "__main__":
   main()
```
