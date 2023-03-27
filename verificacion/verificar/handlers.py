import os
import urllib3
import json


def endpoint_truenative(token,
                    method='POST',
                    ruta='verify',
                    data={}):


    url_offers = os.getenv('TRUENATIVE_URL', 'http://127.0.0.1:4000/')
    encoded_body = json.dumps(data)
    http = urllib3.PoolManager()
    response = http.request(method,
                            f'{url_offers}{ruta}',
                            body=encoded_body,
                            headers={"Authorization": f'Bearer {token}',
                                     'Content-Type': 'application/json'})
    try:
        return (response.status, json.loads(response.data.decode('utf-8')))
    except Exception as e:
        return (response.status, response.data.decode('utf-8'))
