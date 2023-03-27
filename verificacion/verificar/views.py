from flask import Blueprint
from flask import request

from .core import (express,
                   basic,
                   validate_verification)

verifying = Blueprint('verifying', __name__)


@verifying.route("/verifying/express", methods=['POST'])
def verificar_express():
    response, status = express(request)
    return response, status


@verifying.route("/verifying/basic", methods=['POST'])
def verificar_basic():
    response, status = basic(request)
    return response, status

@verifying.route("/verifying/webhook", methods=['POST'])
def verificar_webhook():
    validar_token = request.json.get('verifyToken', False)
    if validar_token == False:
        return 'No viene verifyToken', 400

    a, b = validate_verification(request)
    return a, b

@verifying.route('/verifying/ping', methods=['GET'])
def root():
    return 'pong'

