import os
import json

from google.cloud import pubsub_v1
from google.cloud import tasks_v2

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
BUCKET_KEY_GCP = os.path.join(APP_ROOT)
json_key = f'{BUCKET_KEY_GCP}/terminus-grupo25-c344aae1345b.json'


def publisher_message(message):
    try:

        message = json.dumps(message)

        publisher = pubsub_v1.PublisherClient.from_service_account_json(json_key)
        topic_path = publisher.topic_path("terminus-grupo25", "terminus-25")

        # The message must be a bytestring.
        message = message.encode("utf-8")

        # When you publish a message, the client returns a future.
        future1 = publisher.publish(topic_path, message)
        print(future1.result())
        return {}, 200
    except Exception as e:
        print(e)
        return str(e), 400

def task_truenative(data):
    # Se leen las variables de entorno especificadas
    location_id = 'us-central1'
    projec_id = 'terminus-grupo25'
    queue_id = "terminus-test3-task"
    url_function = 'https://us-central1-terminus-grupo25.cloudfunctions.net/function-terminus-http-3'

    client = tasks_v2.CloudTasksClient.from_service_account_json(json_key)

    # Construye el nombre de la cola a la que se realizará la conexión
    parent = client.queue_path(projec_id, location_id, queue_id)

    # Definición de los parametros de la tarea que se creará
    task = {
        "http_request": {  # Determina el tipo de tareas, en este caso una petición HTTP.
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url_function,  # Determina la URL completa a la que se realizará el consumo del servicio.
            "headers": {
                "Content-type": "application/json"
            },
            "body": data,
        }
    }
    # Se realiza la creación de la tarea en la cola
    response = client.create_task(parent=parent, task=task)
    print( {
        'message': 'Se crea la tarea de manera exitosa',
        'name': response.name,
        'http_request': {
            'url': response.http_request.url,
            'http_method': str(response.http_request.http_method)
        }
    })

