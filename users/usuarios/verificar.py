import os
import json
import urllib3
userWebhook = os.getenv('VERIFICACION_WEBHOOK', 'https://us-central1-terminus-grupo25.cloudfunctions.net/function-terminus-http-3')


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

def create_msj(msj, id_user, transactionIdentifier):
    message = {
    "user": {
        "email": msj.json.get('email', ''),
        "dni": msj.json.get('dni', ''),
        "fullName": msj.json.get('fullName', ''),
        "phone": msj.json.get('phone', ''),
            },
    "transactionIdentifier": transactionIdentifier,
    "userIdentifier": str(id_user),
    "userWebhook": userWebhook
            }
    return json.dumps(message)

def verificacion(request, usuario_id, transactionIdentifier, modelo):
    msj = create_msj(request, usuario_id, transactionIdentifier)
    verify = endpoint_verificacion(request.headers,
                    method='POST',
                    ruta=f'verifying/{modelo}',
                    data=msj)

    return verify
