import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuarios(db.Model):

    __tablename__ = 'usuarios'
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username: str = db.Column(db.String(150))
    email: str = db.Column(db.String(150))
    password: str = db.Column(db.Text)

    dni: str = db.Column(db.String(150))
    fullName: str = db.Column(db.String(150))
    phone: str = db.Column(db.String(150))
    transactionidentifier: str = db.Column(db.String(300))
    score: int = db.Column(db.Integer)

    salt: str = db.Column(db.String(150))
    token: str = db.Column(db.String(500), nullable=True)
    status: str = db.Column(db.String(150), nullable=True)
    expireAt: datetime = db.Column(db.DateTime, default=datetime.datetime.now)
    createdAt: datetime = db.Column(db.DateTime, default=datetime.datetime.now)
