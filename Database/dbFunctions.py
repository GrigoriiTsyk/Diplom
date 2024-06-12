# coding: utf8

import sqlite3
import hashlib

def create_user(status, username, password):
    # status: 0 - admin, 1 - врач

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    conn = sqlite3.connect('Database/database.db')
    c = conn.cursor()

    c.execute('INSERT INTO users (status, username, password) VALUES (?, ?, ?)', (status, username, hashed_password))

    conn.commit()
    conn.close()

def add_foreign_key():
    conn = sqlite3.connect('Database/database.db')
    c = conn.cursor()

    c.execute('''ALTER TABLE users
                ADD CONSTRAINT fk_users_doctors
                FOREIGN KEY (users_doctors) 
                REFERENCES doctors (id)
                ON DELETE CASCADE
                ON UPDATE CASCADE;''')

    conn.commit()
    conn.close()

def add_patient(session, form):
    conn = sqlite3.connect('Database/database.db')
    c = conn.cursor()

    pasport = c.execute('''
        SELECT p.pasport_series, p.pasport_number
        FROM patients p
        WHERE p.pasport_series = ? OR p.pasport_number = ?
    ''', (str(form.get('inputPasSeries')), str(form.get('inputPasNum')))).fetchone()

    print(pasport)
    print(form)

    if pasport == None:
        name = form.get('inputLastName') + " " + form.get('inputFirstName') + " " + form.get('inputMiddleName')
        doctor = c.execute('''
            SELECT users_doctors FROM users 
            WHERE id = ?
            ''', str(session['user_id'])).fetchone()

        pasport_series = form.get('inputPasSeries')
        pasport_number = form.get('inputPasNum')
        snils = form.get('inputSnils')


        c.execute('''
            INSERT INTO patients (name, doctor, pasport_series, pasport_number, snils) 
            VALUES(?, ?, ?, ?, ?);
        ''', (name, doctor[0], pasport_series, pasport_number, snils))

        conn.commit()

        doctor = c.execute('''
            SELECT d.name, p.id, doctor_id FROM users u
            JOIN doctors d ON u.users_doctors = d.doctor_id 
            JOIN patients p ON p.doctor = d.doctor_id 
            WHERE u.id = ? and d.doctor_id = u.users_doctors
            ORDER BY p.id DESC LIMIT 1;
        ''', str(session['user_id'])).fetchone()

        c.execute('''
            INSERT INTO doctors(name, patient, doctor_id) VALUES (?, ?, ?);
        ''', (doctor[0], doctor[1], doctor[2]))

    conn.commit()
    conn.close()

def update_patient(form, id):
    conn = sqlite3.connect('Database/database.db')
    c = conn.cursor()

    patient = c.execute('''
        SELECT *
        FROM patients p
        WHERE p.id = ?
    ''', (id,)).fetchone()

    print(patient)
    print(form)

    if patient != None:
        name = form.get('inputLastName') + " " + form.get('inputFirstName') + " " + form.get('inputMiddleName')

        pasport_series = form.get('inputPasSeries')
        pasport_number = form.get('inputPasNum')
        snils = form.get('inputSnils')
        diagnostic_image = form.get('inputImage')
        diagnostic_result = form.get('inputResult')

        print(diagnostic_image)
        print(diagnostic_result)

        c.execute('''
            UPDATE patients 
            SET name = ?, pasport_series = ?, pasport_number = ?, snils = ?
            WHERE id = ?;
        ''', (name, pasport_series, pasport_number, snils, id))

        conn.commit()

        if diagnostic_image != '':
            c.execute('''
                        UPDATE patients 
                        SET diagnostic_image = ?
                        WHERE id = ?;
                    ''', (diagnostic_image, id))

            conn.commit()

        if diagnostic_result != '':
            c.execute('''
                        UPDATE patients 
                        SET diagnostic_result = ?
                        WHERE id = ?;
                    ''', (diagnostic_result, id))

            conn.commit()

    conn.commit()
    conn.close()

def get_patients(user_id):
    conn = sqlite3.connect('Database/database.db')
    #conn = sqlite3.connect('database.db')
    c = conn.cursor()

    result = c.execute('''
        SELECT p.name, p.id FROM users u
        JOIN doctors d ON u.users_doctors = d.doctor_id 
        JOIN patients p ON d.patient = p.id 
        WHERE u.id = ? and d.doctor_id = u.users_doctors;
    ''', user_id).fetchall()

    conn.commit()
    conn.close()

    return result

def get_patients_by_id(doctor_id):
    conn = sqlite3.connect('Database/database.db')
    #conn = sqlite3.connect('database.db')
    c = conn.cursor()

    result = c.execute('''
        SELECT p.name, p.id FROM doctors d
        JOIN patients p ON d.patient = p.id
        WHERE d.doctor_id = ?;
    ''', doctor_id).fetchall()

    conn.commit()
    conn.close()

    return result

def get_all_doctors():
    conn = sqlite3.connect('Database/database.db')
    #conn = sqlite3.connect('database.db')
    c = conn.cursor()

    result = c.execute('''
        SELECT DISTINCT doctor_id, name FROM doctors;
    ''').fetchall()

    conn.commit()
    conn.close()

    return result

def get_patient_info_from_db(id):
    conn = sqlite3.connect('Database/database.db')
    # conn = sqlite3.connect('database.db')
    c = conn.cursor()

    result = c.execute('''
           SELECT * FROM patients
           WHERE id = ?
       ''', (id,)).fetchall()

    conn.commit()
    conn.close()

    return result

def get_patient_image_path(id):
    conn = sqlite3.connect('Database/database.db')
    #conn = sqlite3.connect('database.db')
    c = conn.cursor()

    result = c.execute('''
               SELECT p.diagnostic_image FROM patients p 
               WHERE id = ?;
           ''', (id,)).fetchall()

    conn.commit()
    conn.close()

    return result

def get_patient_diagnostic_result(id):
    conn = sqlite3.connect('Database/database.db')
    # conn = sqlite3.connect('database.db')
    c = conn.cursor()

    result = c.execute('''
               SELECT p.diagnostic_result FROM patients p 
               WHERE id = ?
           ''', (id,)).fetchall()

    conn.commit()
    conn.close()

    return result

def set_patient_image_path(imageName, id):
    conn = sqlite3.connect('Database/database.db')
    # conn = sqlite3.connect('database.db')
    c = conn.cursor()

    result = c.execute('''
                   UPDATE patients 
                    SET diagnostic_image = ?
                    WHERE id = ?;
               ''', (imageName, id)).fetchall()

    conn.commit()
    conn.close()

    return result

def set_patient_diagnostic_result(diagnostic_result, id):
    conn = sqlite3.connect('Database/database.db')
    # conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
       UPDATE patients 
        SET diagnostic_result = ?
        WHERE id = ?;
    ''', (diagnostic_result, id)).fetchall()

    conn.commit()
    conn.close()

def del_doctor(id):
    conn = sqlite3.connect('Database/database.db')
    # conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
           DELETE FROM patients
           WHERE doctor = ?;
       ''', id)

    conn.commit()

    c.execute('''
        DELETE FROM doctors
        WHERE doctor_id = ?;
    ''', id)

    conn.commit()

    conn.close()

def del_patient(id):
    conn = sqlite3.connect('Database/database.db')
    #conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
               DELETE FROM patients
               WHERE id = ?;
           ''', id)

    conn.commit()

    c.execute('''
            DELETE FROM doctors
            WHERE patient = ?;
        ''', id)

    conn.commit()

    conn.close()

#create_user(0, 'admin', 'your_password')
# create_user(1, 'doctor', 'doctor')
#add_foreign_key()
#print(get_patients('1'))
#print(get_all_doctors()[0][1])

#del_patient(str(6))

#get_patient_image_path(str(13))
