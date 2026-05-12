# ==========================================================
# app.py
# API REST FLASK + MYSQL CLOUD (AIVEN)
# ==========================================================

from flask import Flask, request, jsonify
import pymysql
from dotenv import load_dotenv
import os

# ==========================================================
# CARGAR VARIABLES DE ENTORNO
# ==========================================================

load_dotenv()

# ==========================================================
# CONFIGURACIÓN FLASK
# ==========================================================

app = Flask(__name__)

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

        ssl_disabled=True,

        cursorclass=pymysql.cursors.DictCursor
    )

# ==========================================================
# RUTA PRINCIPAL
# ==========================================================

@app.route('/')
def inicio():

    return jsonify({
        'success': True,
        'mensaje': 'API REST de adopción funcionando correctamente'
    })

# ==========================================================
# TEST VARIABLES DE ENTORNO
# ==========================================================

@app.route('/test-env')
def test_env():

    return jsonify({

        'MYSQL_HOST': os.getenv('MYSQL_HOST'),

        'MYSQL_PORT': os.getenv('MYSQL_PORT'),

        'MYSQL_DATABASE': os.getenv('MYSQL_DATABASE')

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
# OBTENER MASCOTA POR ID
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

        data = request.json

        conn = connect_db()

        cur = conn.cursor()

        sql = """
            INSERT INTO mascotas
            (nombre, especie, edad, ciudad, descripcion, imagen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cur.execute(sql, (

            data.get('nombre'),

            data.get('especie'),

            data.get('edad'),

            data.get('ciudad'),

            data.get('descripcion'),

            data.get('imagen')

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
                descripcion=%s,
                imagen=%s

            WHERE id=%s

        """, (

            data.get('nombre'),

            data.get('especie'),

            data.get('edad'),

            data.get('ciudad'),

            data.get('descripcion'),

            data.get('imagen'),

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

    app.run(debug=True)