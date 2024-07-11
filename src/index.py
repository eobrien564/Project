import json
import base64

print('Loading function')


def lambda_handler(event, context):
    print(event)
    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    authUser = 'user'
    authPass = 'pass'

    passString = (authUser + ':' + authPass).encode()
    b64val = base64.b64encode(passString)
    authString = f'Basic {b64val.decode()}'


    if 'authorization' not in headers.keys() or headers['authorization'][0]['value'] != authString:
        body = 'Unauthorised'
        response = {
            'status' : '401',
            'statusDescription' : 'Unauthorised',
            'body' : body,
            'headers' : {
                'www-authenticate' : [{'key' : 'WWW-Authenticate', 'value' : 'Basic'}]
                }
        }
        return response
    return request