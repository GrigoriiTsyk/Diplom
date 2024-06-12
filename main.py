# coding: utf8
import tensorflow as tf
from flask import Flask, session
from flask import render_template, redirect, url_for, request
import sqlite3
import hashlib
import os
import numpy as np
from werkzeug.utils import secure_filename

from Database.dbFunctions import create_user, get_patients, add_patient, get_patient_info_from_db, \
    get_patient_diagnostic_result, set_patient_image_path, get_patient_image_path, get_all_doctors, get_patients_by_id, \
    del_doctor, del_patient, update_patient

name = 'main'
UPLOAD_FOLDER = 'static/images/screens'

ALLOWED_EXTENSIONS = {'png'}

app = Flask(name)
app.secret_key = 'e80141c41b762bf063e91cb7ae7ca26f3617e8aa'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('Database/database.db')
    conn.row_factory = sqlite3.Row
    return conn

# def load_keras_model():
#     global model
#     model = tf.keras.models.load_model('Neuro/saved_model_2.h5')

def predict_image(image_path):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    print(img_array)

    model = tf.keras.models.load_model('Neuro/saved_model_2.h5')

    model.summary()

    prediction = model.predict(img_array)

    print(prediction[0])

    return prediction

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        session['gUsername'] = username
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

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    doctorsList = get_all_doctors()

    print(doctorsList)
    print(doctorsList[0])

    return render_template('Admin panel.html', username=session['gUsername'], doctorsList=doctorsList)

@app.route('/del_doctor/<int:id>')
def delete_doctor(id):
    del_doctor(str(id))

    return redirect(url_for('admin_panel'))

@app.route('/edit_doctor/<int:doctor_id>/del_patient/<int:id>')
def delete_patient(id, doctor_id):
    del_patient(str(id))

    print(request.url)

    return redirect(url_for('edit_doctor', id=doctor_id))

@app.route('/doctor_main/del_patient/<int:id>')
def doctor_delete_patient(id, doctor_id):
    del_patient(str(id))

    print(request.url)

    return redirect(url_for('doctor_main'))

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

@app.route('/edit_doctor/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    if request.method =='POST':
        add_patient(session=session, form=request.form)

    list = get_patients_by_id(str(id))

    return render_template('Edit doctor page.html', patients_list=list, doctor_id=id)

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    image_path = None

    query = get_patient_image_path(str(id))

    diagnostic_result = get_patient_diagnostic_result(str(id))

    if (query[0][0] == None):
        diagnostic_image = False
    else:
        diagnostic_image = True
        image_path = '/' + UPLOAD_FOLDER + '/' + query[0][0]

    if request.method == 'POST':
        if 'file' not in request.files:
            print('Не могу прочитать файл')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            print('Нет выбранного файла')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            old_path = image_path
            image_path = '/' + UPLOAD_FOLDER + '/' + filename

            set_patient_image_path(filename, id)

    print('image_path: ')
    print(image_path)
    print('diagnostic_result: ')
    print(diagnostic_result[0][0])

    return render_template('Edit patient page.html', id=id, diagnostic_image=diagnostic_image, image_path=image_path, diagnostic_result=diagnostic_result[0][0])

@app.route('/patient_info/<int:id>', methods=['GET', 'POST'])
def get_patient_info(id):
    list = get_patient_info_from_db(str(id))

    print(list[0])

    return render_template('Patient info.html', item=list[0])

@app.route('/add_diagnostic/<int:id>', methods=['POST'])
def add_diagnostic(id):
    print('Функция диагностики')

    query = get_patient_image_path(str(id))

    if(query[0][0] != None):
        image_name = get_patient_image_path(str(id))[0][0]

        image_path = UPLOAD_FOLDER + '/' + image_name

        print( "Путь до изображения: " + image_path)

        if(os.path.exists(image_path)):
            print("файл существует")

            predict_image(image_path)
        else:
            print("Файл не существует")
    else:
        print('Нет изображения для предсказания')

    return redirect('/edit_patient/' + str(id))

@app.route('/update_pateint_info/<int:id>', methods=['POST'])
def update_patient_info(id):
    if request.method == 'POST':
        update_patient(form=request.form, id=str(id))

    return redirect('/patient_info/' + str(id))

if name == 'main':
    #load_keras_model()

    app.run(debug=True)
