from unittest import result
from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gtts import gTTS
import mysql.connector

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_antrianqu"
    )

USERS = [

    {
        "username": "admin",
        "password": "12345",
        "role": "admin"
    },

    {
        "username": "teller",
        "password": "111",
        "role": "teller"
    }

]

data_antrian = [
   {
    "id": 1,
    "nama": "Loket",
    "awalan": "A",
    "tujuan": [
        "Loket 1",
        "Loket 2",
        "Loket 3"
    ]
}
]

data_layar = [

    {
        "id": 1,
        "nama": "Setoran",
        "awalan": "B",
        "tujuan": [
            "Setoran"
        ]
    },

    {
        "id": 2,
        "nama": "Penarikan",
        "awalan": "C",
        "tujuan": [
            "Penarikan"
        ]
    },

    {
        "id": 3,
        "nama": "Penukaran Uang",
        "awalan": "D",
        "tujuan": [
            "Penukaran Uang"
        ]
    }

]

data_admin2 = [

    {
        "id": 1,
        "awalan": "A",
        "tujuan": "Loket 1"
    },

    {
        "id": 2,
        "awalan": "A",
        "tujuan": "Loket 2"
    },

    {
        "id": 3,
        "awalan": "A",
        "tujuan": "Loket 3"
    }

]

data_tujuan = [

    {
        "id": len(data_antrian) + 1,
        "tujuan": "Setoran",
        "file": "Setoran.wav"
    },

    {
        "id": len(data_antrian) +  2,
        "tujuan": "Penarikan",
        "file": "Penarikan.wav"
    },

    {
        "id": len(data_antrian) +   3,
        "tujuan": "Penukaran Uang",
        "file": "penukaran uang.wav"
    }

]

def buat_suara(pesan, filename):

    try:

        folder = "static/audio"

        if not os.path.exists(folder):
            os.makedirs(folder)

        tts = gTTS(text=pesan, lang='id')

        path = os.path.join(folder, filename)

        tts.save(path)

        return True

    except Exception as e:

        print("ERROR SUARA:", e)

        return False

    folder = "static/audio"

    if not os.path.exists(folder):
        os.makedirs(folder)

    tts = gTTS(text=pesan, lang='id')

    path = os.path.join(folder, filename)

    tts.save(path)

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        print(username)
        print(password)

        for user in USERS:

            if username == user["username"] and password == user["password"]:

                if user["role"] == "admin":
                    return redirect(url_for('admin_db1'))

                elif user["role"] == "teller":
                    return redirect(url_for('teller_db'))

        error = "Username atau Password salah!"

    return render_template('Utama/login.html', error=error)   


@app.route('/')
def index():
    return render_template('Utama/index.html')


@app.route('/pilih_layanan')
def pilih_layanan():
    return render_template('pilih_layanan/pilih_layanan.html')

@app.route('/antrian_teller')
def antrian_teller():
    return render_template('pilih_layanan/antrian_teller.html')

@app.route('/antrian_cs')
def antrian_cs():
    return render_template('pilih_layanan/antrian_cs.html')

@app.route('/antrian_pk')
def antrian_pk():
    return render_template('pilih_layanan/antrian_pk.html')

@app.route('/antrian_lainnya')
def antrian_lainnya():
    return render_template('pilih_layanan/antrian_lainnya.html')

@app.route('/success')
def success():
    return render_template('Utama/success.html')

@app.route('/masuk')
def masuk():
    return render_template('Utama/masuk.html')

@app.route('/admin')
def admin():
    return "<h2>Halaman Admin</h2>"

@app.route('/teller')
def teller():
    return "<h2>Halaman Teller</h2>"


    
@app.route('/admin_db1')
def admin_db1():
    return render_template('admin_tb/admin_db1.html', data_antrian=data_antrian, data_layar=data_layar)

@app.route('/admin_db2')
def admin_db2():
    return render_template('admin_tb/admin_db2.html', data_admin2=data_admin2)

@app.route('/admin_db3')
def admin_db3():
    return render_template('admin_tb/admin_db3.html',data_tujuan=data_tujuan)


@app.route('/tambah', methods=['GET', 'POST'])
def tambah():

    if request.method == 'POST':

        nama = request.form['nama']
        awalan = request.form['awalan']

        tujuan = request.form['tujuan'].split(',')

        data_baru = {
            "id": len(data_antrian) + 1,
            "nama": nama,
            "awalan": awalan,
            "tujuan": tujuan
        }

        data_antrian.append(data_baru)

        return redirect(url_for('admin_db1'))

    return render_template('E_T_V/tambah.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    data = next((item for item in data_antrian if item["id"] == id), None)

    if request.method == 'POST':

        data["nama"] = request.form['nama']
        data["awalan"] = request.form['awalan']
        data["tujuan"] = request.form['tujuan'].split(',')

        return redirect(url_for('admin_db1'))

    return render_template('E_T_V/edit.html', data=data)


@app.route('/view/<int:id>')
def view(id):

    data = next(
        (item for item in data_antrian if item["id"] == id),
        None
    )

    return render_template('E_T_V/view.html', data=data)

@app.route('/delete/<int:id>')
def delete(id):

    global data_antrian

    data_antrian = [
        item for item in data_antrian
        if item["id"] != id
    ]

    return redirect(url_for('admin_tb/admin_db1'))

@app.route('/edit_layar/<int:id>', methods=['GET', 'POST'])
def edit_layar(id):

    data = next(
        (item for item in data_layar if item["id"] == id),
        None
    )

    if request.method == 'POST':

        data["nama"] = request.form['nama']
        data["awalan"] = request.form['awalan']
        data["tujuan"] = request.form['tujuan'].split(',')

        return redirect(url_for('admin_db1'))

    return render_template('E_T_V/edit.html', data=data)

@app.route('/delete_layar/<int:id>')
def delete_layar(id):

    global data_layar

    data_layar = [
        item for item in data_layar
        if item["id"] != id
    ]

    return redirect(url_for('admin_db1'))

@app.route('/view_layar/<int:id>')
def view_layar(id):

    data = next(
        (item for item in data_layar if item["id"] == id),
        None
    )

    return render_template('E_T_V/view.html', data=data)

@app.route('/tambah_layar', methods=['GET', 'POST'])
def tambah_layar():

    if request.method == 'POST':

        nama = request.form['nama']
        awalan = request.form['awalan']

        tujuan = request.form['tujuan'].split(',')

        data_baru = {
            "id": len(data_layar) + 1,
            "nama": nama,
            "awalan": awalan,
            "tujuan": tujuan
        }

        data_layar.append(data_baru)

        return redirect(url_for('admin_db1'))

    return render_template('E_T_V/tambah.html')

@app.route('/tambah_admin2', methods=['GET', 'POST'])
def tambah_admin2():

    if request.method == 'POST':

        awalan = request.form['awalan']
        tujuan = request.form['tujuan']

        data_baru = {
            "id": len(data_admin2) + 1,
            "awalan": awalan,
            "tujuan": tujuan
        }

        data_admin2.append(data_baru)

        return redirect(url_for('admin_db2'))

    return render_template('tambah_admin2.html')

@app.route('/delete_admin2/<int:id>')
def delete_admin2(id):

    global data_admin2

    data_admin2 = [
        item for item in data_admin2
        if item["id"] != id
    ]

    return redirect(url_for('admin_db2'))

@app.route('/edit_admin2/<int:id>', methods=['GET', 'POST'])
def edit_admin2(id):

    data = next(
        (item for item in data_admin2 if item["id"] == id),
        None
    )

    if request.method == 'POST':

        data["awalan"] = request.form['awalan']
        data["tujuan"] = request.form['tujuan']

        return redirect(url_for('admin_db2'))

    return render_template('edit_admin2.html', data=data)

@app.route('/tambah_tujuan', methods=['GET', 'POST'])
def tambah_tujuan():
    if request.method == 'POST':

        tujuan = request.form.get('tujuan')
        file = request.files.get('file')

        if not file or file.filename == '':
            return "File audio belum dipilih!"

        filename = secure_filename(file.filename)

        upload_path = os.path.join('static', 'audio', filename)
        file.save(upload_path)

        new_data = {
            "id": max([i["id"] for i in data_tujuan], default=0) + 1,
            "tujuan": tujuan,
            "file": filename
        }

        data_tujuan.append(new_data)

        return redirect(url_for('admin_db3'))

    return render_template('tambah_tujuan.html')

@app.route('/edit_tujuan/<int:id>', methods=['GET', 'POST'])
def edit_tujuan(id):

    data = next(
        (item for item in data_tujuan if item["id"] == id),
        None
    )

    if request.method == 'POST':

        data["tujuan"] = request.form['tujuan']
        data["file"] = request.form['file']

        return redirect(url_for('admin_db3'))

    return render_template('edit_tujuan.html',data=data)

@app.route('/delete_tujuan/<int:id>')
def delete_tujuan(id):

    global data_tujuan

    data_tujuan = [

        item for item in data_tujuan
        if item["id"] != id

    ]

    return redirect(url_for('admin_db3'))

@app.route('/teller_db')
def teller_db():

    db = get_db()

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM Antrian")

    total = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return render_template(
        'teller_db.html',
        total=total
    )

@app.route('/panggil/<int:id_loket>')
def panggil(id_loket):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM antrian
        WHERE status='menunggu'
        AND id_loket=%s
        ORDER BY id_antrian ASC
        LIMIT 1
    """, (id_loket,))

    antrian = cursor.fetchone()

    # cek apakah ada antrian
    if antrian is None:
        return "Antrian kosong"

    nomor = antrian['nomor_antrian']

    cursor.execute("""
        UPDATE antrian
        SET status='dilayani'
        WHERE id_antrian=%s
    """, (antrian['id_antrian'],))

    db.commit()

    cursor.close()
    db.close()

    # kirim audio
    return send_from_directory(
        "static/audio",
        "panggil.mp3"
    )

@app.route('/play/<filename>')
def play_wav(filename):
    return send_from_directory('static/audio', filename)

if __name__ == '__main__':
    app.run(debug=False)