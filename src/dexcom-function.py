from datetime import datetime, timedelta
import urllib.parse
import requests
import json

CLIENT_ID = 'ygHSIkgQ11P18yMZg8Y0o6tUaCsnqnDr'
CLIENT_SECRET = 'CRHqYJrAHRv6PwdE'
TOKEN_URL = 'https://sandbox-api.dexcom.com/v2/oauth2/token'

# CloudFront distribution URL (replace with your actual CloudFront distribution URL)
CLOUDFRONT_URL = 'https://d2r1l8k32qe758.cloudfront.net'
REDIRECT_URI = f'{CLOUDFRONT_URL}'

AUTH_URL = 'https://sandbox-api.dexcom.com/v2/oauth2/login'
REDIRECT_URI = 'https://d2r1l8k32qe758.cloudfront.net/callback'
API_URL = 'https://sandbox-api.dexcom.com/v3/users/self/egvs'
STATE = 'random_string_to_prevent_csrf'

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    print("ENTERING LAMBDA")
    print(event)
    auth_code = None
    
    request = event['Records'][0]['cf']['request']
    print(request)
    if request['querystring'] and request['querystring'] != '':
        querystring = request['querystring']
        # Extract the 'code' parameter
        auth_code = extract_code_from_querystring(querystring)
        print(auth_code)
    
    # Check if this is the callback with an authorization code
    if auth_code != None:
        print("GET AUTH CODE OFF CLOUDFRONT EVENT")
        # Exchange the authorization code for an access token
        tokens = get_access_token(auth_code)
        access_token = tokens['access_token']
        
        # Use the access token to make an API request
        api_response = make_api_request(access_token)
        print(f"******API RETURNED {api_response}")
        
        # Embedd HTML file in response
        # Define the path to the HTML file within your Lambda package
        html_file_path = 'index.html'

        # Get values in range
        values, total, all_values = get_in_range_values(api_response)
        high, low, percent_in_range = get_table_values(total, values)
        
        print(f'****VALUES = {values}')
        print(f'****COUNT = {total}')
    
        # Read the contents of the HTML file
        with open(html_file_path, 'r') as html_file:
            html_content = html_file.read()

        html_content = html_template.replace('{{ high_values }}', json.dumps(high, indent=4))
        html_content = html_template.replace('{{ all_values }}', json.dumps(all_values, indent=4))
        html_content = html_template.replace('{{ low_values }}', json.dumps(low, indent=4))
        html_content = html_template.replace('{{ in_range_percentage }}', json.dumps(percent_in_range, indent=4))
        
        response = {
            'status': '200',
            'statusDescription': 'OK',
            'headers': {
                'content-type': [{ 'key': 'Content-Type', 'value': 'text/html' }]
            },
            'body': html_content
        }
        
        return response
    else:
        # Redirect to the OAuth authorization URL
        # 'Location': auth_url
        print("Redirect to OAuth")
        auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&scope=read"
        print("Auth URL: " + auth_url)
        redirectResponse = {
            'status': '302',
            'headers': {
               'location': [{'key': 'Location', 'value': auth_url}]
            },
            'body': ''
        }
        print(redirectResponse)
        return redirectResponse

def get_access_token(auth_code):
    """
    Exchange the authorization code for an access token.
    """
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    json_str = json.dumps(data, indent=4)
    print("get_access_token data: " + json_str)

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    print(response)

    
    response.raise_for_status()
    return response.json()

def make_api_request(access_token):
    print(access_token)
    """
    Make an authenticated API request using the access token.
    """
    print("make_api_request")

    # Get the current date and time
    now = datetime.now()
    
    # Format today's date and time in the correct format
    formatted_today = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Calculate the date 3 days ago
    three_days_ago = now - timedelta(days=3)
    
    # Format the date 3 days ago in the correct format
    formatted_three_days_ago = three_days_ago.strftime("%Y-%m-%dT%H:%M:%S")
    
    print("Today's date:", formatted_today)
    print("Date 3 days ago:", formatted_three_days_ago)

    query = {
      "startDate": formatted_three_days_ago,
      "endDate": formatted_today
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(API_URL, headers=headers, params=query)

    print("response from make_api_request")
    print(f"RESPONSE {response}")
    response.raise_for_status()
    return response.json()
    
def extract_code_from_querystring(querystring):
    
    # Split the query string by '&' to get each key=value pair
    parameters = querystring.split('&')
    
    # Iterate over each parameter to find the 'code'
    for param in parameters:
        key, value = param.split('=')
        if key == 'code':
            return value

    # If 'code' not found, return None
    return None

def get_in_range_values(api_response):
    
    in_range_values = []
    all_values = []
    count = 0
    for record in api_response['records']:
        count += 1
        all_values.append(record['value'])
        # Check if value is in range
        if record['value'] >= 40 and record['value'] <= 400:
          # Append to in range list
          in_range_values.append(record['value'])
    
    return in_range_values, count, all_values
    
def get_table_values(count, in_range):
    high_bar = []
    low_bar = []
    
    for i in range(count):
        high_bar.append(400)
        low_bar.append(40)
    
    percent_in_range = (len(in_range)/count) * 100
    print(f'% IN RANGE{percent_in_range}')
    
    return high_bar, low_bar, percent_in_range
    

    
    
    
    """
    # Replace placeholders with actual API data
    html_content = html_template.replace('{{ api_data }}', json.dumps(api_data, indent=4))
"""
