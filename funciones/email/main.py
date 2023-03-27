import base64
import os
import smtplib
import json
from email.message import EmailMessage


def hello_pubsub(event, context):
    data = base64.b64decode(event['data']).decode('utf8')
    print(data)
    data = json.loads(data)
    data_transaction = data['transaction']
    data_user = data['user']
    # data_transaction = data_['transaction']
    print(data_transaction)
    print(data_user['email'])

    destinatario = data_user['email']
    usuario_name = data_user['fullName']

    remitente = os.getenv('REMITENTE', '')
    destinatario = destinatario
    mensaje = f"¡Datos validados {data_user}, transaccion {data_transaction}"
    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = f"Usuario {usuario_name} validado"
    email.set_content(mensaje)
    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login(remitente, os.getenv('REMITENTE_PASSWORK', ''))
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()
    print('email enviado')
