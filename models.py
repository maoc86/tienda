from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password = db.Column(db.String(255), index=True, unique=True)


class Books(db.Model):
    __tablename__ = "tblbook"
    bookid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    picture = db.Column(db.String(150), index=True, unique=True)
    isbn = db.Column(db.String(255), index=True, unique=True)
    cantidad = db.Column(db.Integer())
    talla = db.Column(db.String(40))
    precio_prov = db.Column(db.Integer())
    precio_retail = db.Column(db.Integer())
    fecha_ent = db.Column(db.DateTime, default=datetime.datetime.now)

    prov_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))


class Proveedores(db.Model):
    __tablename__ = "proveedores"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(80))


class Clientes(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(240))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(80))
