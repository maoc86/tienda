from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import re

import pymysql

from models import db, Users, Books, Proveedores, Clientes

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
# Databse configuration mysql                             Username:password@hostname/databasename
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/datos'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

bcrypt = Bcrypt(app)

db.init_app(app)

with app.app_context():
    db.create_all()


app.config['UPLOAD_FOLDER'] = 'static/images'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['name']
        password = request.form['password']
        email = request.form['email']

        user_exist = Users.query.filter_by(email=email).first() is not None

        if user_exist:
            mesage = 'Email already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not fullname or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = Users(name=fullname, email=email,
                             password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            mesage = 'You have successfully registered !'

    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage=mesage)


@app.route('/login', methods=['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # print(email)
        # print(password)
        if email == '' or password == '':
            mesage = 'Please enter email and password !'
        else:
            user = Users.query.filter_by(email=email).first()
            print(user)

            if user is None:
                mesage = 'Please enter correct email / password !'
            else:
                if not bcrypt.check_password_hash(user.password, password):
                    mesage = 'Please enter correct email and password !'
                else:
                    session['loggedin'] = True
                    session['userid'] = user.id
                    session['name'] = user.name
                    session['email'] = user.email
                    mesage = 'Logged in successfully !'
                    return redirect(url_for('dashboard'))

    return render_template('login.html', mesage=mesage)


@app.route("/prueba", methods=['GET', 'POST'])
def prueba():
    if 'loggedin' in session:
        books = Books.query.all()
        proveedores = Proveedores.query.all()

        m = '1'

        return render_template("prueba.html", proveedores=proveedores, m=m, books=books)
    return redirect(url_for('login'))


@app.route("/ventas", methods=['GET', 'POST'])
def ventas():
    if 'loggedin' in session:
        return render_template("ventas.html")
    return redirect(url_for('login'))


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        return render_template("dashboard.html")
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

# Manage Proveedores


@app.route("/proveedores", methods=['GET', 'POST'])
def proveedores():
    if 'loggedin' in session:
        proveedores = Proveedores.query.all()

        return render_template("proveedores.html", proveedores=proveedores)
    return redirect(url_for('login'))


@app.route('/save_proveedor', methods=['POST'])
def save_proveedor():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            telefono = request.form['telefono']
            action = request.form['action']

            if action == 'updateProveedor':
                proveedorid = request.form['proveedorid']
                proveedor = Proveedores.query.get(proveedorid)

                proveedor.name = name
                proveedor.email = email
                proveedor.telefono = telefono

                db.session.commit()
                print("UPDATE proveedor")
            else:
                proveedor = Proveedores(
                    name=name, email=email, telefono=telefono)
                db.session.add(proveedor)
                db.session.commit()
                print("INSERT INTO proveedor")
            return redirect(url_for('proveedores'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("proveedores.html", msg=msg)
    return redirect(url_for('login'))


@app.route("/edit_proveedor", methods=['GET', 'POST'])
def edit_proveedor():
    msg = ''
    if 'loggedin' in session:
        proveedorid = request.args.get('proveedorid')
        print(proveedorid)
        proveedores = Proveedores.query.get(proveedorid)

        return render_template("edit_proveedor.html", proveedores=proveedores)
    return redirect(url_for('login'))


@app.route("/delete_proveedor", methods=['GET'])
def delete_proveedor():
    if 'loggedin' in session:
        proveedorid = request.args.get('proveedorid')
        proveedor = Proveedores.query.get(proveedorid)

        db.session.delete(proveedor)
        db.session.commit()

        return redirect(url_for('proveedores'))
    return redirect(url_for('login'))

# Manage Clientes


@app.route("/clientes", methods=['GET', 'POST'])
def clientes():
    if 'loggedin' in session:
        clientes = Clientes.query.all()

        return render_template("clientes.html", clientes=clientes)
    return redirect(url_for('login'))


@app.route('/save_cliente', methods=['POST'])
def save_cliente():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            direccion = request.form['direccion']
            email = request.form['email']
            telefono = request.form['telefono']
            action = request.form['action']

            if action == 'updateClientes':
                clienteid = request.form['clienteid']
                cliente = Clientes.query.get(clienteid)

                cliente.nombre = nombre
                cliente.apellido = apellido
                cliente.direccion = direccion
                cliente.email = email
                cliente.telefono = telefono

                db.session.commit()
                print("UPDATE cliente")
            else:
                cliente = Clientes(
                    nombre=nombre, apellido=apellido, direccion=direccion, email=email, telefono=telefono)
                db.session.add(cliente)
                db.session.commit()
                print("INSERT INTO cliente")
            return redirect(url_for('clientes'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("clientes.html", msg=msg)
    return redirect(url_for('login'))


@app.route("/edit_cliente", methods=['GET', 'POST'])
def edit_cliente():
    msg = ''
    if 'loggedin' in session:
        clienteid = request.args.get('clienteid')
        print(clienteid)
        clientes = Clientes.query.get(clienteid)

        return render_template("edit_clientes.html", clientes=clientes)
    return redirect(url_for('login'))


@app.route("/delete_cliente", methods=['GET'])
def delete_cliente():
    if 'loggedin' in session:
        clienteid = request.args.get('clienteid')
        cliente = Clientes.query.get(clienteid)

        db.session.delete(cliente)
        db.session.commit()

        return redirect(url_for('clientes'))
    return redirect(url_for('login'))


# Manage Productos


@app.route("/books", methods=['GET', 'POST'])
def books():
    if 'loggedin' in session:
        books = Books.query.all()
        proveedores = Proveedores.query.all()

        return render_template("books.html", books=books, proveedores=proveedores)
    return redirect(url_for('login'))


@app.route('/save_book', methods=['POST'])
def save_book():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            isbn = request.form['isbn']
            cantidad = request.form['cantidad']
            talla = request.form['talla']
            precio_prov = request.form['precio_prov']
            precio_retail = request.form['precio_retail']
            fecha_ent = request.form['fecha_ent']
            prov_id = request.form['prov_id']
            action = request.form['action']

            if action == 'updateBook':
                bookid = request.form['bookid']
                book = Books.query.get(bookid)

                book.name = name
                book.isbn = isbn
                book.cantidad = cantidad
                book.talla = talla
                book.precio_prov = precio_prov
                book.precio_retail = precio_retail
                book.fecha_ent = fecha_ent
                book.prov_id = prov_id

                db.session.commit()
                print("UPDATE book")
            else:
                file = request.files['uploadFile']
                filename = secure_filename(file.filename)
                print(filename)
                if file and allowed_file(file.filename):
                    file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], filename))
                    filenameimage = file.filename

                    book = Books(name=name, picture=filenameimage,
                                 isbn=isbn, cantidad=cantidad, talla=talla, precio_prov=precio_prov, precio_retail=precio_retail, fecha_ent=fecha_ent, prov_id=prov_id)
                    db.session.add(book)
                    db.session.commit()
                    print("INSERT INTO book")
                else:
                    msg = 'Invalid Uplaod only png, jpg, jpeg, gif'
            return redirect(url_for('books'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("books.html", msg=msg)
    return redirect(url_for('login'))


@app.route("/edit_book", methods=['GET', 'POST'])
def edit_book():
    msg = ''
    if 'loggedin' in session:
        bookid = request.args.get('bookid')
        print(bookid)
        books = Books.query.get(bookid)
        proveedores = Proveedores.query.all()

        return render_template("edit_books.html", books=books, proveedores=proveedores)
    return redirect(url_for('login'))


@app.route("/delete_book", methods=['GET'])
def delete_book():
    if 'loggedin' in session:
        bookid = request.args.get('bookid')
        book = Books.query.get(bookid)
        print(book.picture)
        db.session.delete(book)
        db.session.commit()
        os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], book.picture))
        return redirect(url_for('books'))
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
