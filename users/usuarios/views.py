from flask import Blueprint
from flask import request

from .core import (creacion_usuario,
                   autenticar_usuario,
                   self_information,
                   manual_verification)


usearios = Blueprint('usearios', __name__)


@usearios.route("/users", methods=['POST'])
def register_users():
    response, status = creacion_usuario(request)
    return response, status


@usearios.route("/users/auth", methods=['POST'])
def token_user():
    response, status = autenticar_usuario(request)
    return response, status


@usearios.route("/users/me", methods=['GET'])
def information_user():
    response, status = self_information(request)
    return response, status

@usearios.route("/users/manual-verification", methods=['POST'])
def verify_manual_user():
    response, status = manual_verification(request)
    return response, status

@usearios.route('/users/ping', methods=['GET'])
def root():
    return 'pong'

