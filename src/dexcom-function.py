import requests

import webbrowser

import urllib.parse

from http.server import BaseHTTPRequestHandler, HTTPServer

CLIENT_ID = 'ygHSIkgQ11P18yMZg8Y0o6tUaCsnqnDr'
CLIENT_SECRET = 'CRHqYJrAHRv6PwdE'
AUTH_URL = 'https://sandbox-api.dexcom.com/v2/oauth2/login?client_id={your_client_id}&redirect_uri={your_redirect_uri}&response_type=code&scope=offline_access&state={your_state_value}'
TOKEN_URL = 'https://sandbox-api.dexcom.com/v2/oauth2/token'
REDIRECT_URI = 'https://d2r1l8k32qe758.cloudfront.net/callback'
API_URL = 'https://d2r1l8k32qe758.cloudfront.net'

# Step 1: Define the handler for the HTTP server to capture the authorization code

class OAuthCallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if 'code' in query_components:

            self.server.auth_code = query_components['code'][0]

        self.send_response(200)

        self.send_header('Content-type', 'text/html')

        self.end_headers()

        self.wfile.write(b'You can close this window now.')
# Step 2: Start the HTTP server and open the authorization URL in the browser

def get_authorization_code():

    server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)

    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"

    webbrowser.open(auth_url)

    server.handle_request()

    return server.auth_code

 

# Step 3: Exchange the authorization code for an access token and refresh token

def get_tokens(auth_code):

    data = {

        'grant_type': 'authorization_code',

        'code': auth_code,

        'redirect_uri': REDIRECT_URI,

        'client_id': CLIENT_ID,

        'client_secret': CLIENT_SECRET,

    }

    response = requests.post(TOKEN_URL, data=data)

    if response.status_code == 200:

        return response.json()

    else:

        raise Exception(f"Failed to obtain tokens: {response.text}")

 

# Step 4: Use the access token to make authorized API requests

def make_api_request(access_token):

    headers = {

        'Authorization': f'Bearer {access_token}'

    }

    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:

        return response.json()

    else:

        raise Exception(f"API request failed: {response.text}")

 

if __name__ == "__main__":

    # Step 1: Get the authorization code

    auth_code = get_authorization_code()

 

    # Step 2: Exchange the authorization code for tokens

    tokens = get_tokens(auth_code)

    access_token = tokens['access_token']

    refresh_token = tokens['refresh_token']

 

    # Step 3: Make an authorized API request

    api_response = make_api_request(access_token)

    print(api_response)

'''
from datetime import timedelta
from datetime import date
today = date.today()
print(today)

yesterday = today - timedelta(days = 1)
print(yesterday)
'''