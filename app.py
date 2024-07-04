from flask import Flask, render_template,request,redirect,url_for,session,Response, flash, make_response
import pyodbc
import random
from flask_sqlalchemy import SQLAlchemy
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
            return render_template('login.html')
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
        
        query = "SELECT * FROM Usuarios WHERE correo = ? AND  password = ?"
        cursor.execute(query, (correo,password))
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
            return redirect(url_for('gestion'))
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
        
        query="INSERT INTO Usuarios (opcion, nombre, correo, password) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (opcion, nombre, correo,password))
        conn.commit() 
    
    return render_template('registrarse.html')

@app.route('/alumno', methods=['GET', 'POST'])
def alumno():
    query = "SELECT TareaID, Titulo, Descripcion, Fecha FROM Tarea"
    cursor.execute(query)
    tareas = cursor.fetchall()

    query2 = "SELECT PracticaID, Titulo, Descripcion, Fecha FROM Practica"
    cursor.execute(query2)
    practicas = cursor.fetchall()

    query3 = "SELECT PublicacionID, Titulo, Descripcion, Fecha FROM Publicacion"
    cursor.execute(query3)
    publicacion = cursor.fetchall()

    return render_template('alumno.html', tareas=tareas, practicas=practicas, publicacion=publicacion)


@app.route('/gestion', methods=['GET', 'POST'])
def gestion():
    # Consulta SQL para obtener los usuarios
    query = "SELECT id, opcion, nombre, correo, password FROM Usuarios"
    cursor.execute(query)
    usuarios = cursor.fetchall()

    return render_template('gestion_escolar.html', usuarios=usuarios)

# Ruta para eliminar un usuario
@app.route('/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    query = "DELETE FROM Usuario WHERE id=?"
    cursor.execute(query, (usuario_id,))
    conn.commit()
    return redirect(url_for('gestion'))


@app.route('/profesor', methods=['GET', 'POST'])
def profesor():
    user = session.get('user')
    if user:
        query = "SELECT TareaID, Titulo, Descripcion, Fecha FROM Tarea"
        cursor.execute(query)
        tareas = cursor.fetchall()

        query2 = "SELECT PracticaID, Titulo, Descripcion, Fecha FROM Practica"
        cursor.execute(query2)
        practicas = cursor.fetchall()

        query3 = "SELECT PublicacionID, Titulo, Descripcion, Fecha FROM Publicacion"
        cursor.execute(query3)
        publicacion = cursor.fetchall()

        return render_template('profesor.html', tareas=tareas, practicas=practicas, publicacion=publicacion)
    else:
        return redirect('/')


@app.route('/gestiontarea', methods=['GET','POST'])
def gestiontarea():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        
        query = "INSERT INTO Tarea (Titulo,Descripcion,Fecha) VALUES (?,?,?)"
        cursor.execute(query,(titulo,descripcion,fecha))
        conn.commit()
    
    return render_template('gestiontarea.html')

@app.route('/gestionpractica', methods=['GET','POST'])
def gestionpractica():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        
        query = "INSERT INTO Practica (Titulo,Descripcion,Fecha) VALUES (?,?,?)"
        cursor.execute(query,(titulo,descripcion,fecha))
        conn.commit()
    
    return render_template('gestionpractica.html')

@app.route('/gestionpublicacion', methods=['GET','POST'])
def gestionpublicacion():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        
        query = "INSERT INTO Publicacion (Titulo,Descripcion,Fecha) VALUES (?,?,?)"
        cursor.execute(query,(titulo,descripcion,fecha))
        conn.commit()
    return render_template('gestionpublicacion.html')

@app.route('/eliminar_tarea', methods=['POST'])
def eliminar_tarea():
    tarea_id = request.form['id']
    query = "DELETE FROM Tarea WHERE TareaID = ?"
    cursor.execute(query, tarea_id)
    conn.commit()
    return redirect('/profesor')

@app.route('/eliminar_practica', methods=['POST'])
def eliminar_practica():
    practica_id = request.form['id']
    query = "DELETE FROM Practica WHERE PracticaID = ?"
    cursor.execute(query, practica_id)
    conn.commit()
    return redirect('/profesor')

@app.route('/eliminar_publicacion', methods=['POST'])
def eliminar_publicacion():
    publicacion_id = request.form['id']
    query = "DELETE FROM Publicacion WHERE PublicacionID = ?"
    cursor.execute(query, publicacion_id)
    conn.commit()
    return redirect('/profesor')


@app.route('/cerrarsesion', methods=['POST'])
@login_required
def cerrar_sesion():
    if 'user' in session:
        session.pop('user', None)
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # HTTP 1.1
    response.headers['Pragma'] = 'no-cache'  # HTTP 1.0
    response.headers['Expires'] = '0'  # Proxies
    
    return response

@app.route('/entregar_tarea', methods=['GET','POST'])
@login_required
def entregar_tarea():
    if request.method == 'POST':
        opcion = request.form['opcion_de_entregar']

        print(opcion)
        if opcion == 'Archivo':

            #aqui va lo del pdf
            return redirect('/alumno')
        elif opcion == 'Script':
            script = request.form['script']
            script2 = request.form['tablas']
            script3 = request.form['script2']
            script4 = request.form['input-tablas']
            script5 = request.form['script3']
            script6 = request.form['condi']
            tareaid = request.form['tarea_id']

            print(f"{script} {script2} {script3} {script4} {script5} {script6}")
            print(f"id: {tareaid}")
            user_id = session['user']['id']

            consulta = script+" "+script2+" "+script3+" "+script4+" "+script5+" "+script6
            query = "INSERT INTO Entrega_trabajo (id_tarea, id_alumno, contenido, datos) VALUES (?,?,?,NULL)"
            cursor.execute(query, (tareaid, int(user_id), consulta))
            conn.commit()
            print("Insertado en la Base de datos")

    return redirect('/alumno')

@app.route('/vertareas', methods=['GET','POST'])
@login_required
def ver_tareas():
    id_tarea = 0
    if request.method=='POST':
        id = request.form['id']
        id_tarea = id

    user = session.get('user')
    if user:
        query = """SELECT Tarea.Titulo, Usuarios.nombre, Usuarios.correo, Entrega_trabajo.datos, Entrega_trabajo.contenido 
        FROM Entrega_trabajo 
        INNER JOIN Usuarios on Entrega_trabajo.id_alumno = Usuarios.id 
        INNER JOIN Tarea on Entrega_trabajo.id_tarea = Tarea.TareaID 
        WHERE Usuarios.opcion = 'Alumno' and Tarea.TareaID = ?"""
        cursor.execute(query, (int(id_tarea)))
        tareas = cursor.fetchall()
    
        return render_template('Tareas_view.html', tareas=tareas)
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1433,debug=True)