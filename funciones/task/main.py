import os
import urllib3
import json


def endpoint_verificacion(headers,
                          method='GET',
                          ruta='verifying/ping',
                          data={}):
    token = ''
    url_offers = os.getenv('VERIFICACION_URL', 'http://127.0.0.1:3011/')
    encoded_body = data
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


def verifying_task(request):
    RUV = request
    print(request.data)
    try:
        verify = endpoint_verificacion(request.headers,
                                       method='POST',
                                       ruta=f'verifying/express',
                                       data=json.dumps(json.loads(request.data))
                                       )
    except Exception as e:
        print("error")
        return {"msj": e}, 400

    try:
        print(verify[0])
        print(verify[1])
        print(verify[1].get('status'))
        if verify[0] != 200:
            return verify[1], verify[0]
        if verify[1].get('status') == 'ACCEPTED':
            return {}, 400
        return {}, 200
    except Exception as e:
        print(verify)
        return {}, 200
    # if verify[0] != 200:
    #     return verify[1], verify[0]

    # if verify[1].get('status') == 'ACCEPTED':
    #     return {}, 400

