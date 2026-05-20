from unittest import result
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import os
from werkzeug.utils import secure_filename
from gtts import gTTS
import mysql.connector

app = Flask(__name__)

data_antrian = [
    {
        "id": 1,
        "nama": "Loket",
        "awalan": "A",
        "tujuan": ["Loket 1", "Loket 2", "Loket 3"]
    }
]

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_antrianqu"
    )

    
def proses_login_database(username_input, password_input):
        db = get_db()
        cursor = db.cursor(dictionary=True)
    
        cursor.execute("SELECT * FROM petugas WHERE username = %s", (username_input,))
        user_data = cursor.fetchone()

        cursor.close()
        db.close()
    
    # Bagian ini sekarang sudah diluruskan dengan rapi di sisi kiri
        if user_data:
            hash_database = user_data['password'].strip()
        
        if hash_database.startswith("scrypt."):
            hash_database = hash_database.replace("scrypt.32768.8.1$", "scrypt:32768:8:1$")
            
        try:
            if check_password_hash(hash_database, password_input):
                return {"status": "sukses", "role": user_data['username']}
        except ValueError:
            pass
            
        return {"status": "gagal"}


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

        result = proses_login_database(username, password)

        if result["status"] == "sukses":
            if result["role"] == "admin":
                return redirect(url_for('admin_db1'))
            elif result["role"] == "teller":
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

@app.route('/ambil_antrian/<nama_layanan>', methods=['GET'])
def ambil_antrian(nama_layanan):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    nama_clean = nama_layanan.strip()
    cursor.execute("SELECT id_layanan FROM layanan WHERE LOWER(TRIM(nama_layanan)) = LOWER(%s)", (nama_clean,))
    data_layanan = cursor.fetchone()

    if not data_layanan:
        cursor.close()
        db.close()
        return f"Error: Layanan '{nama_layanan}' tidak ditemukan di database!", 400

    id_layanan = data_layanan['id_layanan']

    if id_layanan == 1:
        id_loket = 1
        nama_loket = 'Loket 1'
    elif id_layanan == 22:
        id_loket = 2
        nama_loket = 'Loket 2'
    elif id_layanan == 21:
        id_loket = 3
        nama_loket = 'Loket 3'
    else:
        id_loket = 1
        nama_loket = 'Loket 1'

    cursor.execute("SELECT id_loket FROM loket WHERE id_loket = %s", (id_loket,))
    loket_eksis = cursor.fetchone()

    if not loket_eksis:
        try:

            cursor.execute("""
                INSERT INTO loket (id_loket, nama_loket, id_layanan, status, awalan, tujuan)
                VALUES (%s, %s, %s, 'buka', 'A', %s)
            """, (id_loket, nama_loket, id_layanan, nama_loket))
            db.commit() 
        except Exception as e:
            db.rollback()
            cursor.close()
            db.close()
            return f"Gagal mendaftarkan loket otomatis. Error: {str(e)}", 500

    cursor.execute("""
        SELECT COALESCE(MAX(nomor_antrian), 0) as nomor_terakhir 
        FROM antrian 
        WHERE id_loket = %s
    """, (id_loket,))
    nomor_terakhir = cursor.fetchone()['nomor_terakhir']
    
    nomor_baru = nomor_terakhir + 1

    try:
        cursor.execute("""
            INSERT INTO antrian (nomor_antrian, waktu_masuk, status, id_layanan, id_loket)
            VALUES (%s, NOW(), 'menunggu', %s, %s)
        """, (nomor_baru, id_layanan, id_loket))
        db.commit()
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        return f"Gagal menyimpan antrian ke database. Error: {str(e)}", 500

    cursor.close()
    db.close()

    return redirect(url_for('success'))


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
    db = get_db()
    cursor = db.cursor(dictionary=True) 

    cursor.execute("SELECT * FROM loket")
    data_antrian_mysql = cursor.fetchall()

    for item in data_antrian_mysql:
        if item.get('tujuan'):
            item['tujuan'] = [t.strip() for t in item['tujuan'].split(',')]
        else:
            item['tujuan'] = []

    cursor.execute("SELECT * FROM layanan") 
    data_layar_mysql = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('admin_tb/admin_db1.html', data_antrian=data_antrian_mysql, data_layar=data_layar_mysql)


@app.route('/admin_db2')
def admin_db2():
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True) 

    cursor.execute("SELECT * FROM layanan")
    data_mentah = cursor.fetchall()

    data_admin2_mysql = []
    for item in data_mentah:
        if isinstance(item, dict) and 'id_layanan' in item:
            if item.get('tujuan') and isinstance(item['tujuan'], str):
                if ',' in item['tujuan']:
                    item['tujuan'] = [t.strip() for t in item['tujuan'].split(',')]
                else:
                    item['tujuan'] = [item['tujuan'].strip()]
            else:
                item['tujuan'] = []
            
            data_admin2_mysql.append(item)

    cursor.close()
    db.close()
    return render_template('admin_tb/admin_db2.html', data_admin2=data_admin2_mysql)

@app.route('/admin_db3')
def admin_db3():
    return render_template('admin_tb/admin_db3.html',data_tujuan=data_tujuan)


@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        nama = request.form.get('nama')
        awalan = request.form.get('awalan')
        tujuan = request.form.get('tujuan') 

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO loket (nama_loket, awalan, status, tujuan, id_layanan) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nama, awalan, 'buka', tujuan, 1))

        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin_db1'))

    return render_template('E_T_V/tambah.html')




@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        nama_baru = request.form.get('nama')
        awalan_baru = request.form.get('awalan')
        tujuan_baru = request.form.get('tujuan')


        cursor.execute("""
            UPDATE loket
            SET nama_loket = %s, awalan = %s, tujuan = %s
            WHERE id_loket = %s
        """, (nama_baru, awalan_baru, tujuan_baru, id))
        db.commit()
        
        cursor.close()
        db.close()
        return redirect(url_for('admin_db1'))

    cursor.execute("SELECT * FROM loket WHERE id_loket = %s", (id,))
    data = cursor.fetchone()
    
    if data and data.get('tujuan'):
        data['tujuan'] = [t.strip() for t in data['tujuan'].split(',')]
    else:
        if data: 
            data['tujuan'] = []

    cursor.close()
    db.close()
    return render_template('E_T_V/edit.html', data=data)


@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM loket WHERE id_loket = %s", (id,))
    
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('admin_db1'))

@app.route('/view/<int:id>')
def view(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM loket WHERE id_loket = %s", (id,))
    data = cursor.fetchone()

    cursor.close()
    db.close()
    return render_template('E_T_V/view.html', data=data)

@app.route('/edit_layar/<int:id>', methods=['GET', 'POST'])
def edit_layar(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        nama_baru = request.form.get('nama')
        awalan_baru = request.form.get('awalan')
        tujuan_baru = request.form.get('tujuan') 

        cursor.execute("""
            UPDATE layanan
            SET nama_layanan = %s, awalan = %s, tujuan = %s
            WHERE id_layanan = %s
        """, (nama_baru, awalan_baru, tujuan_baru, id))
        db.commit()
        
        cursor.close()
        db.close()
        return redirect(url_for('admin_db1'))

    cursor.execute("SELECT * FROM layanan WHERE id_layanan = %s", (id,))
    data = cursor.fetchone()
    
    if data and data.get('tujuan'):
        data['tujuan'] = [t.strip() for t in data['tujuan'].split(',')]
    else:
        if data:
            data['tujuan'] = []

    cursor.close()
    db.close()
    return render_template('E_T_V/edit.html', data=data)



@app.route('/delete_layar/<int:id>')
def delete_layar(id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM layanan WHERE id_layanan = %s", (id,))
    db.commit()
    
    cursor.close()
    db.close()
    return redirect(url_for('admin_db1'))

@app.route('/view_layar/<int:id>')
def view_layar(id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM layanan WHERE id_layanan = %s", (id,))
    data = cursor.fetchone()

    cursor.close()
    db.close()
    return render_template('E_T_V/view.html', data=data)

@app.route('/tambah_layar', methods=['GET', 'POST'])
def tambah_layar():
    if request.method == 'POST':

        nama = request.form.get('nama')
        awalan = request.form.get('awalan')
        tujuan = request.form.get('tujuan') 

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO layanan (nama_layanan, status_aktif_non_aktif, awalan, tujuan) 
            VALUES (%s, %s, %s, %s)
        """, (nama, 'aktif', awalan, tujuan))
        
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin_db1'))

    return render_template('E_T_V/tambah.html')




@app.route('/tambah_admin2', methods=['GET', 'POST'])
def tambah_admin2():

    if request.method == 'POST':

        nama = request.form.get('nama', '').strip()
        awalan = request.form.get('awalan', '').strip()
        tujuan = request.form.get('tujuan', '').strip()

        db = get_db()
        cursor = db.cursor()

        query = """
            INSERT INTO layanan (nama_layanan, awalan, status_aktif_non_aktif, tujuan)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (nama, awalan, 'aktif', tujuan))

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_db2'))

    return render_template('tambah_admin2.html')

@app.route('/delete_admin2/<int:id>')
def delete_admin2(id):

    db = get_db()
    cursor = db.cursor()

    query = "DELETE FROM layanan WHERE id_layanan = %s"

    cursor.execute(query, (id,))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for('admin_db2'))

@app.route('/edit_admin2/<int:id>', methods=['GET', 'POST'])
def edit_admin2(id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        awalan_baru = request.form.get('awalan')
        tujuan_baru = request.form.get('tujuan')

        cursor.execute("""
            UPDATE layanan
            SET awalan = %s, tujuan = %s
            WHERE id_layanan = %s
        """, ( awalan_baru, tujuan_baru, id))
        db.commit()
        
        cursor.close()
        db.close()
        return redirect(url_for('admin_db2'))
    
    cursor.execute("SELECT * FROM layanan WHERE id_layanan = %s", (id,))
    data = cursor.fetchone() 

    cursor.close()
    db.close()
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

import os

@app.route('/edit_tujuan/<int:id>', methods=['GET', 'POST'])
def edit_tujuan(id):
    
    data = next(
        (item for item in data_tujuan if item["id"] == id),
        None
    )

    if not data:
        return "Data tidak ditemukan!", 404

    if request.method == 'POST':
        data["tujuan"] = request.form.get('tujuan')

        file_audio = request.files.get('file')
        
        if file_audio and file_audio.filename != '':
            folder_simpan = os.path.join('static', 'audio')

            if not os.path.exists(folder_simpan):
                os.makedirs(folder_simpan)

            file_audio.save(os.path.join(folder_simpan, file_audio.filename))

            data["file"] = file_audio.filename
        else:
            data["file"] = request.form.get('file_lama', data.get('file'))

        return redirect(url_for('admin_db3'))

    return render_template('edit_tujuan.html', data=data)


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
    cursor = db.cursor(dictionary=True)

    query_hitung = """
        SELECT 
            l.id_loket AS id_baris,
            l.nama_loket,
            (SELECT COUNT(*) FROM antrian WHERE id_loket = l.id_loket) AS jml_antrian,
            (SELECT COALESCE(MAX(nomor_antrian), 0) FROM antrian WHERE id_loket = l.id_loket AND status = 'dilayani') AS no_antrian,
            (SELECT COUNT(*) FROM antrian WHERE id_loket = l.id_loket AND status = 'menunggu') AS sisa
        FROM loket l
        WHERE l.id_loket IN (1, 2, 3)
    """
    
    cursor.execute(query_hitung)
    data_tabel_teller = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('teller_db.html', daftar_antrian=data_tabel_teller)


@app.route('/panggil-antrian-api/<int:id_loket>', methods=['POST'])
def panggil_api(id_loket):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # 1. Cari antrean terdepan berdasarkan id_loket (bukan id_layanan!)
        cursor.execute("""
            SELECT a.*, l.nama_layanan 
            FROM antrian a
            JOIN layanan l ON a.id_layanan = l.id_layanan
            WHERE a.status='menunggu' AND a.id_loket=%s 
            ORDER BY a.id_antrian ASC LIMIT 1
        """, (id_loket,))
        antrian = cursor.fetchone()

        if antrian is None:
            cursor.close()
            db.close()
            return jsonify({'status': 'error', 'message': 'Antrean untuk loket ini sudah habis!'}), 400

        # 2. Ganti status antrean menjadi 'dilayani'
        cursor.execute("UPDATE antrian SET status='dilayani' WHERE id_antrian=%s", (antrian['id_antrian'],))
        db.commit()

        # 3. Hitung sisa antrean terbaru di loket tersebut
        cursor.execute("SELECT COUNT(*) as sisa FROM antrian WHERE id_loket=%s AND status='menunggu'", (id_loket,))
        sisa_baru = cursor.fetchone()['sisa']

        nomor_dipanggil = antrian['nomor_antrian']
        nama_layanan = antrian['nama_layanan']

        cursor.close()
        db.close()

        # 4. Kirim data lengkap ke JavaScript termasuk nama layanan & nomor loket
        return jsonify({
            'status': 'success',
            'no_antrian': nomor_dipanggil,
            'nama_layanan': nama_layanan,
            'id_loket': id_loket,
            'sisa': sisa_baru
        })

    except Exception as e:
        if db.is_connected():
            cursor.close()
            db.close()
        print("ERROR INTERNAL PYTHON:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/panggil/<int:id_loket>')
def panggil(id_loket):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""SELECT * FROM antrian WHERE status='menunggu' AND id_loket=%s ORDER BY id_antrian ASC LIMIT 1""", (id_loket,))

    antrian = cursor.fetchone()
    if antrian is None:
        return "Antrian kosong"

    nomor = antrian['nomor_antrian']

    cursor.execute("""UPDATE antrian SET status='dilayani' WHERE id_antrian=%s""", (antrian['id_antrian'],))

    db.commit()

    cursor.close()
    db.close()

    return send_from_directory("static/audio","panggil.mp3")

@app.route('/toggle_loket/<int:id_loket>', methods=['POST'])
def toggle_loket(id_loket):
    data = request.get_json()
    # True = buka, False = tutup (sesuai kolom status di phpMyAdmin loket kamu)
    status_baru = 'buka' if data.get('aktif') else 'tutup'
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            UPDATE loket 
            SET status = %s 
            WHERE id_loket = %s
        """, (status_baru, id_loket))
        
        db.commit() # WAJIB ADA AGAR PERMANEN
        cursor.close()
        db.close()
        return jsonify({'status': 'success', 'message': f'Status loket berhasil diubah menjadi {status_baru}'})
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/toggle_layanan/<int:id_layanan>', methods=['POST'])
def toggle_layanan(id_layanan):
    data = request.get_json()
    
    # 2. Tentukan status baru berdasarkan kondisi sakelar (True = aktif, False = nonaktif)
    status_baru = 'aktif' if data.get('aktif') else 'nonaktif'
    
    print(f"Mencoba mengubah id_layanan {id_layanan} menjadi {status_baru}") # Untuk cek di terminal
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # 3. Jalankan query UPDATE langsung ke kolom database phpMyAdmin kamu
        cursor.execute("""
            UPDATE layanan 
            SET status_aktif_non_aktif = %s 
            WHERE id_layanan = %s
        """, (status_baru, id_layanan))
        
        # 4. WAJIB COMMIT agar MySQL benar-benar menyimpan perubahannya!
        db.commit()
        
        cursor.close()
        db.close()
        return jsonify({'status': 'success', 'message': f'Status berhasil diubah menjadi {status_baru}'})
        
    except Exception as e:
        print("Gagal update database:", e)
        db.rollback() # Batalkan jika ada error
        cursor.close()
        db.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/play/<filename>')
def play_wav(filename):
    return send_from_directory('static/audio', filename)

if __name__ == '__main__':
    app.run(debug=True)