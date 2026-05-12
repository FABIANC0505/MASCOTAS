# ==========================================================
# app.py
# PROYECTO COMPLETO FLASK + MYSQL + KAFKA + .ENV
# ==========================================================

from flask import Flask, request, render_template, flash, url_for, redirect
import pymysql
from werkzeug.utils import secure_filename
from confluent_kafka import Producer
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
app.secret_key = 'secretkey'

upload_folder = 'static/uploads/'
allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = upload_folder

# ==========================================================
# CONFIGURACIÓN KAFKA
# ==========================================================

kafka_conf = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),

    'security.protocol': os.getenv('KAFKA_SECURITY_PROTOCOL'),

    'ssl.ca.location': os.getenv('KAFKA_CA_LOCATION'),

    'ssl.certificate.location': os.getenv('KAFKA_CERT_LOCATION'),

    'ssl.key.location': os.getenv('KAFKA_KEY_LOCATION'),

    'client.id': 'adopta-app'
}

producer = Producer(kafka_conf)

# ==========================================================
# CONEXIÓN MYSQL
# ==========================================================

def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='adopta',
        cursorclass=pymysql.cursors.DictCursor,
        ssl_disabled=True
    )

# ==========================================================
# VALIDAR EXTENSIONES DE IMÁGENES
# ==========================================================

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# ==========================================================
# RUTA PRINCIPAL
# ==========================================================

@app.route('/')
def inicio():
    return render_template('base.html')

# ==========================================================
# MOSTRAR MASCOTAS
# ==========================================================

@app.route('/mascotas')
def index():
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM mascotas")

        data = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('index.html', mascotas=data)

    except Exception as e:
        flash(f"Error al conectar a la base de datos: {e}")

        return render_template('index.html', mascotas=[])

# ==========================================================
# REGISTRAR MASCOTA
# ==========================================================

@app.route('/adoptar', methods=['GET', 'POST'])
def adoptar():

    if request.method == 'POST':

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
        # VALIDAR EDAD
        # ==================================================

        if not edad:
            edad = None

        # ==================================================
        # INSERTAR EN MYSQL
        # ==================================================

        connection = connect_db()

        try:

            with connection.cursor() as cursor:

                sql = """
                    INSERT INTO mascotas
                    (nombre, especie, edad, ciudad, descripcion, imagen)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                cursor.execute(sql, (
                    nombre,
                    especie,
                    edad,
                    ciudad,
                    descripcion,
                    imagen
                ))

            connection.commit()

            # ==============================================
            # ENVIAR EVENTO A KAFKA
            # ==============================================

            mensaje = f"""
            Nueva mascota registrada:
            Nombre: {nombre}
            Especie: {especie}
            Ciudad: {ciudad}
            """

            producer.produce(
                'mascotas',
                value=mensaje
            )

            producer.flush()

            flash('Mascota registrada correctamente.')

            return redirect(url_for('index'))

        except Exception as e:

            flash(f"Error al registrar mascota: {e}")

        finally:

            connection.close()

    return render_template('adoptar.html')

# ==========================================================
# EDITAR MASCOTA
# ==========================================================

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'POST':

        nombre = request.form['nombre']
        especie = request.form['especie']
        edad = request.form['edad']
        ciudad = request.form['ciudad']
        descripcion = request.form['descripcion']

        file = request.files.get('imagen')

        # ==================================================
        # ACTUALIZAR IMAGEN
        # ==================================================

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            file.save(filepath)

            imagen = f"uploads/{filename}"

        else:

            imagen = request.form.get('imagen_actual')

        # ==================================================
        # UPDATE MYSQL
        # ==================================================

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
            nombre,
            especie,
            edad,
            ciudad,
            descripcion,
            imagen,
            id
        ))

        conn.commit()

        # ==================================================
        # EVENTO KAFKA
        # ==================================================

        mensaje = f"""
        Mascota actualizada:
        ID: {id}
        Nombre: {nombre}
        """

        producer.produce(
            'mascotas',
            value=mensaje
        )

        producer.flush()

        cur.close()
        conn.close()

        flash('Mascota actualizada correctamente')

        return redirect(url_for('index'))

    # ======================================================
    # OBTENER DATOS
    # ======================================================

    cur.execute("SELECT * FROM mascotas WHERE id=%s", (id,))

    mascota = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('editar.html', mascota=mascota)

# ==========================================================
# ELIMINAR MASCOTA
# ==========================================================

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):

    try:

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM mascotas WHERE id=%s",
            (id,)
        )

        conn.commit()

        # ==================================================
        # EVENTO KAFKA
        # ==================================================

        mensaje = f"Mascota eliminada con ID: {id}"

        producer.produce(
            'mascotas',
            value=mensaje
        )

        producer.flush()

        cur.close()
        conn.close()

        flash('Mascota eliminada correctamente', 'success')

    except Exception as e:

        flash(f"Error al eliminar mascota: {e}")

    return redirect(url_for('index'))

# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    # Crear carpeta uploads si no existe
    os.makedirs(upload_folder, exist_ok=True)

    app.run(debug=True)