import os
import uuid
import hashlib
import pandas as pds
import psycopg2
from .handlers import endpoint_truenative
from .models import Verificacion, db
from .gcp_pubsub import publisher_message, task_truenative

SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'a')

params_dic = {
    'host': os.getenv('USERS_DB_HOST', '34.135.18.78'),
    "database": os.getenv('USERS_DB_NAME', 'terminus_db'),
    'user': os.getenv('USERS_DB_USER', 'admin'),
    'password': os.getenv('USERS_DB_PASSWORD', 'admin'),
}

users_tablename = os.getenv('DB_USERS_TABLE', 'usuarios')

def express(request):
    # revisar si tiene ruv
    existe_usuario = Verificacion.query.filter(Verificacion.transactionidentifier == request.json["transactionIdentifier"]).first()
    # si no tiene ruv hace peticion si tiene solo consulta
    if existe_usuario is None:
        return {"mensaje": "Usuario con email no exista o incorrecto"}, 404

    #reviso el get para ver el proceso
    RUV = existe_usuario.ruv
    consulta = endpoint_truenative(os.getenv('SECRET_TOKEN', 'a'),
                        method='GET',
                        ruta=f'verify/{RUV}')
    if consulta[0] != 200:
        return consulta[1], consulta[0]

    # se activa la logica de jose si el proceso es PROCESSED
    if consulta[1].get('status') == 'PROCESSED':
        try:
            a, b = validate_verification(consulta[1])
            if b == 200:
                return consulta[1], consulta[0]
            return a, b
        except Exception as e:
            return consulta[1], consulta[0]

    return consulta[1], consulta[0]


def basic(request):
    respuesta = endpoint_truenative(os.getenv('SECRET_TOKEN', 'a'),
                    method='POST',
                    ruta='verify',
                    data=request.json)
    verificacion = Verificacion(ruv=respuesta[1].get('RUV'),
                                useridentifier=request.json["userIdentifier"],
                                transactionidentifier=respuesta[1].get('transactionIdentifier'))
    db.session.add(verificacion)
    db.session.commit()
    # ponerlo en una cola
    task_truenative(request.data)
    return respuesta[1], respuesta[0]


def validate_verification(trunative_resp):
    # Verify fields
    try:
        trunative_resp = trunative_resp.json
    except Exception as e:
        trunative_resp = trunative_resp
    fields_validation_ok = validate_true_resp_fields(trunative_resp)
    if not fields_validation_ok:
        print("Identity verification message error")
        return 0

    # check message token
    if 'verifyToken' in trunative_resp:
        token_validation_result = validate_true_token(trunative_resp['verifyToken'], trunative_resp['RUV'],
                                                      trunative_resp['score'])
        if (not token_validation_result):
            print("Message authenticity couldn't be confirmed")
            return 0

    # get user info
    users_db = connect_user_db()
    if (users_db is None):
        print("Users_db connection error")
        return 0
    user_info = users_db_get_info(trunative_resp['userIdentifier'])
    if user_info is None:
        print("Error getting the data")
        return 0
    if user_info.empty:
        print("user not found")
        return 0

    # validate score
    user_new_status = 'POR_VERIFICAR'
    if int(trunative_resp['score']) >= 80:
        user_new_status = 'VERIFICADO'
    else:
        user_new_status = 'NO_VERIFICADO'

    # Update database record
    user_update_resp = users_db_update_info(trunative_resp['userIdentifier'],
                                            user_new_status,
                                            int(trunative_resp['score']))

    if not user_update_resp:
        print("User status couldn't be updated")
        return 0

    user_response_msg = construir_msj(trunative_resp, user_info, user_new_status)

    # Close db connection
    users_db.close()

    a, b = publisher_message(user_response_msg)
    return a, b


def users_db_update_info(user_id, user_new_status, user_new_score):
    cursor = connect_user_db().cursor()
    try:
        cursor.execute(
            f"update {users_tablename} set status = '{user_new_status}', score='{user_new_score}' where id = {user_id};")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return False
    cursor.close()
    return True


def users_db_get_info(user_id):
    column_names = ["id",
                    "username",
                    "email",
                    "dni",
                    "fullName",
                    "phone",
                    "status",
                    "transactionIdentifier"]

    cursor = connect_user_db().cursor()
    try:
        cursor.execute(
            f'select id, username, email, dni, "fullName", phone, status, transactionIdentifier from {users_tablename} where id = {user_id};')
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return None
    result = cursor.fetchall()
    cursor.close()
    df = pds.DataFrame(result, columns=column_names)
    return df


def validate_true_resp_fields(truenative_resp):
    if ('RUV' not in truenative_resp or
            'userIdentifier' not in truenative_resp or
            'score' not in truenative_resp or
            'createdAt' not in truenative_resp or
            'status' not in truenative_resp):
        return False
    return True


def validate_true_token(verifyToken, RUV, SCORE):
    token = f"{SECRET_TOKEN}:{RUV}:{SCORE}"
    sha_token = hashlib.sha256(token.encode()).hexdigest()
    return True if sha_token == verifyToken else False


def connect_user_db():
    try:
        db = psycopg2.connect(**params_dic)
        db.autocommit = True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        db = None
    return db


def construir_msj(trunative_resp, user_info, user_new_status):
    # Write message to topic
    return {
        "transaction": {
            "RUV": trunative_resp['RUV'],
            "transactionIdentifier": user_info.get("transactionIdentifier").iloc[-1],
            "userIdentifier": trunative_resp['userIdentifier'],
            "verificationStatus": user_new_status
        },
        "user": {
            "username": user_info.get("username").iloc[-1],
            "email": user_info.get("email").iloc[-1],
            "dni": user_info.get("dni").iloc[-1],
            "fullName": user_info.get("fullName").iloc[-1],
            "phone": user_info.get("phone").iloc[-1]
        }
    }

