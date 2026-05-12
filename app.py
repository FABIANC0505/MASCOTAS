# ==========================================================
# app.py
# API REST FLASK + MYSQL CLOUD (AIVEN)
# ==========================================================

from flask import Flask, request, jsonify
import pymysql
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

# ==========================================================
# CARGAR VARIABLES DE ENTORNO
# ==========================================================

load_dotenv()

# ==========================================================
# CONFIGURACIÓN FLASK
# ==========================================================

app = Flask(__name__)

upload_folder = 'static/uploads/'
allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = upload_folder

# ==========================================================
# CONEXIÓN MYSQL CLOUD
# ==========================================================

def connect_db():

    return pymysql.connect(

        host=os.getenv('MYSQL_HOST'),

        user=os.getenv('MYSQL_USER'),

        password=os.getenv('MYSQL_PASSWORD'),

        database=os.getenv('MYSQL_DATABASE'),

        port=int(os.getenv('MYSQL_PORT')),

        ssl={
            'ca': os.getenv('MYSQL_SSL_CA')
        },

        cursorclass=pymysql.cursors.DictCursor
    )

# ==========================================================
# VALIDAR IMÁGENES
# ==========================================================

def allowed_file(filename):

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# ==========================================================
# RUTA PRINCIPAL
# ==========================================================

@app.route('/')
def inicio():

    return jsonify({
        'mensaje': 'API REST de adopción funcionando correctamente'
    })

# ==========================================================
# OBTENER TODAS LAS MASCOTAS
# ==========================================================

@app.route('/mascotas', methods=['GET'])
def obtener_mascotas():

    try:

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM mascotas")

        mascotas = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'total': len(mascotas),
            'data': mascotas
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        })

# ==========================================================
# OBTENER UNA MASCOTA POR ID
# ==========================================================

@app.route('/mascotas/<int:id>', methods=['GET'])
def obtener_mascota(id):

    try:

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM mascotas WHERE id=%s",
            (id,)
        )

        mascota = cur.fetchone()

        cur.close()
        conn.close()

        if mascota:

            return jsonify({
                'success': True,
                'data': mascota
            })

        return jsonify({
            'success': False,
            'mensaje': 'Mascota no encontrada'
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        })

# ==========================================================
# REGISTRAR MASCOTA
# ==========================================================

@app.route('/mascotas', methods=['POST'])
def registrar_mascota():

    try:

        nombre = request.form.get('nombre')
        especie = request.form.get('especie')
        edad = request.form.get('edad')
        ciudad = request.form.get('ciudad')
        descripcion = request.form.get('descripcion')

        imagen = None

        # ==================================================
        # SUBIR IMAGEN
        # ==================================================

        file = request.files.get('imagen')

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            file.save(filepath)

            imagen = f"uploads/{filename}"

        # ==================================================
        # INSERT MYSQL
        # ==================================================

        conn = connect_db()
        cur = conn.cursor()

        sql = """
            INSERT INTO mascotas
            (nombre, especie, edad, ciudad, descripcion, imagen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cur.execute(sql, (
            nombre,
            especie,
            edad,
            ciudad,
            descripcion,
            imagen
        ))

        conn.commit()

        nuevo_id = cur.lastrowid

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'mensaje': 'Mascota registrada correctamente',
            'id': nuevo_id
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        })

# ==========================================================
# ACTUALIZAR MASCOTA
# ==========================================================

@app.route('/mascotas/<int:id>', methods=['PUT'])
def actualizar_mascota(id):

    try:

        data = request.json

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE mascotas
            SET nombre=%s,
                especie=%s,
                edad=%s,
                ciudad=%s,
                descripcion=%s
            WHERE id=%s
        """, (
            data['nombre'],
            data['especie'],
            data['edad'],
            data['ciudad'],
            data['descripcion'],
            id
        ))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'mensaje': 'Mascota actualizada correctamente'
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        })

# ==========================================================
# ELIMINAR MASCOTA
# ==========================================================

@app.route('/mascotas/<int:id>', methods=['DELETE'])
def eliminar_mascota(id):

    try:

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM mascotas WHERE id=%s",
            (id,)
        )

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'mensaje': 'Mascota eliminada correctamente'
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        })

# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    os.makedirs(upload_folder, exist_ok=True)

    app.run(debug=True)