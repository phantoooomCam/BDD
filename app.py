from flask import Flask, render_template,request,redirect,url_for,session,Response, flash, make_response
import pyodbc
import random
import string
from flask_mail import Mail, Message
from config import SQL_SERVER_CONFIG
from flask_session import Session
from datetime import timedelta
from datetime import datetime
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import base64

#Configuracion de cookies---------------------------------------------------------
app = Flask(__name__,template_folder='templates')
app.secret_key = 'secret_password'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

#Configuracion de requerimiento de sesion-------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('iniciar_sesion'))
        return f(*args, **kwargs)
    return decorated_function

Session(app)

#Cerrar sesion despues de tiempo---------------------------------------
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    if 'user' in session:
        if 'last_activity' in session:
            if datetime.now() - session['last_activity'] > app.permanent_session_lifetime:
                session.pop('user', None)
        session['last_activity'] = datetime.now()
        

#Configuracion con la base de datos
conn_str = (
    f"DRIVER=ODBC Driver 17 for SQL Server;"
    f"SERVER={SQL_SERVER_CONFIG['server']};"
    f"DATABASE={SQL_SERVER_CONFIG['database']};"
    f"Trusted_Connection={SQL_SERVER_CONFIG['trusted_connection']};"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

#Direcciones Paginas web
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password'] 
        
        query = "SELECT * FROM Usuario WHERE correo = ? AND password = ?"
        cursor.execute(query, (correo, password))
        
        user = cursor.fetchone()
        
        if user:
            session['user']={
                'id':user[0],
                'opcion':user[1],
                'nombre':user[2],
                'correo':user[3],
                'password':user[4]
            }
        if user[1] == 'Profesor':
            column_names = [column[0] for column in cursor.description]
            user_data = dict(zip(column_names, user))
            session['user'] = user_data
            return redirect(url_for('profesor'))
        elif user[1] == 'Alumno':
            column_names = [column[0] for column in cursor.description]
            user_data = dict(zip(column_names, user))
            session['user'] = user_data
            return redirect(url_for('alumno'))
        elif user[1] == 'Gestión Escolar':
            column_names = [column[0] for column in cursor.description]
            user_data = dict(zip(column_names, user))
            session['user'] = user_data
            return redirect(url_for(''))
        else:
            error = 'Correo electrónico o contraseña incorrectos. Por favor, inténtelo de nuevo.'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/registro',methods=['GET','POST'])
def registro():
    
    if request.method == 'POST':
        opcion = request.form['opcion']
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        
        query="INSERT INTO Usuario (opcion, nombre, correo, password) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (opcion, nombre, correo,password))
        conn.commit() 
    
    return render_template('registrarse.html')

@app.route('/alumno',methods=['GET','POST'])
def alumno():
    return render_template('alumno.html')

@app.route('/profesor',methods=['GET','POST'])
def profesor():
    return render_template('profesor.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1433,debug=True)