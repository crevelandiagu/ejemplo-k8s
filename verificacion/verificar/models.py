import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Verificacion(db.Model):

    __tablename__ = 'verificar'
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ruv: str = db.Column(db.String(150))
    useridentifier: int = db.Column(db.Integer)
    transactionidentifier: str = db.Column(db.Text)

    createdAt: datetime = db.Column(db.DateTime, default=datetime.datetime.now)
