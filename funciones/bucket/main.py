import base64
import os
import uuid
import json
from google.cloud import storage
def hello_pubsub_bucket(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    client = storage.Client()
    bucket = client.get_bucket(os.environ.get('BUCKETNAME', ''))

    data = base64.b64decode(event['data']).decode('utf8')
    print(data)
    data = json.loads(data)
    data_transaction = data['transaction']

    data = json.dumps(data)
    ## Guarda la nueva entidad en una archivo
    blob = bucket.blob(data_transaction["transactionIdentifier"])
    blob.upload_from_string(data, content_type='application/json')
    print('envia bucket')
