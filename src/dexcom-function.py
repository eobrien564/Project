import urllib.parse
#import requests  # No longer using botocore.vendored.requests as it's deprecated
import requests
import json

CLIENT_ID = 'ygHSIkgQ11P18yMZg8Y0o6tUaCsnqnDr'
CLIENT_SECRET = 'CRHqYJrAHRv6PwdE'
TOKEN_URL = 'https://sandbox-api.dexcom.com/v2/oauth2/token'

# CloudFront distribution URL (replace with your actual CloudFront distribution URL)
CLOUDFRONT_URL = 'https://d2r1l8k32qe758.cloudfront.net'
REDIRECT_URI = f'{CLOUDFRONT_URL}/callback'

def get_authorization_code():
    pass
    print("******* auth_url defined")
    auth_url = f"https://sandbox-api.dexcom.com/v2/oauth2/login?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    print("auth_url done")
    
    # You will now direct the user to this URL, which will eventually redirect back to your CloudFront distribution.
    print("Please open the following URL in your browser to authorize:")
    print(auth_url)
    # Here you'd typically ask the user to paste the authorization code they received or capture it via CloudFront.'''

def lambda_handler(event, context):
    print("lambda_handler called")
    print(event)

    # Step 1: Extract the authorization code from the event triggered by CloudFront

#    if 'queryStringParameters' in event and 'code' in event['queryStringParameters']:
#        print("auth code defined")
#        auth_code = event['queryStringParameters']['code']
#        print(f"Authorization code received: {auth_code}")

    auth_code = get_authorization_code()
    print("*** AUTH CODE RETURNED ***")

        # Step 2: Exchange the authorization code for tokens
    tokens = get_tokens(auth_code)
    access_token = tokens['access_token']

        # Step 3: Make an authorized API request
    api_response = make_api_request(access_token)
    print(api_response)
#    else:
 #       return {"statusCode": 400, "body": "Authorization code not found."}

def get_tokens(auth_code):
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, data=data)
    print("RESPONSE = "+response)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to obtain tokens: {response.text}")

def make_api_request(access_token):
    API_URL = 'https://sandbox-api.dexcom.com/v2/users/self/egvs'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed: {response.text}")
