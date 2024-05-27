from flask import Flask, session
from flask import render_template, redirect, url_for, request
import sqlite3
import hashlib

import tensorflow as tf
from keras.src.saving import load_model

from Database.dbFunctions import create_user, get_patients, add_patient

name = 'main'

app = Flask(name)
app.secret_key = 'e80141c41b762bf063e91cb7ae7ca26f3617e8aa'

def get_db_connection():
    conn = sqlite3.connect('Database/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def load_keras_model():
    global model
    model = load_model('Neuro/classify_model.h5')

@app.route('/')
def home():
  return redirect(url_for('admin_login'))

@app.route('/adm_login', methods=['GET', 'POST'])
def admin_login():
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        global gUsername
        gUsername = username
        conn.close()

        if user and user['password'] == hashed_password:
            session['user_id'] = user['id']
            if user['status'] == 0:
                return redirect(url_for('admin_panel'))
            elif user['status'] == 1:
                return redirect(url_for('doctor_main_page'))
            else:
                error = 'Что это за пользователь такой!?'
        else:
            error = 'Неправильное имя пользователя или пароль'

    return render_template('Login page.html', error=error)

@app.route('/admin_panel')
def admin_panel():
    return render_template('Admin panel.html', username=gUsername)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confPassword = request.form['confPassword']

        if username != "" and username != None:
            if password and confPassword != "":
                if password == confPassword:
                    conn = get_db_connection()
                    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                    conn.close()
                    if user:
                        error = 'Имя пользователя уже занято'
                    else:
                        create_user(1, username, password)
                        return redirect(url_for('admin_login'))
                else:
                    error = 'Пароли не совпадают'
            else:
                error = 'Поля пароля не могут быть пустыми'
        else:
            error = 'Имя пользователя не может быть пустым'

    return render_template('Registration page.html', error=error)

@app.route('/doctor_main', methods=['GET', 'POST'])
def doctor_main_page():
    if request.method =='POST':
        add_patient(session=session, form=request.form)

    list = get_patients(str(session['user_id']))

    return render_template('Doctor main page.html', patients_list=list)

if name == 'main':
    load_keras_model()

    app.run(debug=True)
