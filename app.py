from flask import Flask, request, render_template, flash, url_for, redirect
import pymysql
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'secretkey'
upload_folder = 'static/uploads/'
allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = upload_folder

# conexión a la base de datos MySQL
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='adopta',
        cursorclass=pymysql.cursors.DictCursor,
        ssl_disabled=True
    )

@app.route('/')
def inicio():
    # Mostrar interfaz de bienvenida con base.html
    return render_template('base.html')


# Ruta principal que muestra las mascotas disponibles para adopción
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
    
    # Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# Ruta para adoptar una mascota
# Aquí se maneja tanto la visualización del formulario como el procesamiento del mismo
@app.route('/adoptar', methods=['GET', 'POST'])
def adoptar():
    if request.method == 'POST':
        # Tomamos datos del formulario
        nombre = request.form.get('nombre')
        especie = request.form.get('especie')
        edad = request.form.get('edad')
        ciudad = request.form.get('ciudad')
        descripcion = request.form.get('descripcion')
        imagen = request.form.get('imagen')

        file = request.files.get('imagen')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            imagen = f"uploads/{filename}"
        else:
            imagen = request.form.get('imagen_actual')  # Mantener la imagen si no se sube nueva


        # Si algún campo es vacío, lo puedes manejar aquí o permitir NULL en la base datos
        if not edad:
            edad = None  # En MySQL el valor NULL, no string vacío

        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO mascotas (nombre, especie, edad, ciudad, descripcion, imagen) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (nombre, especie, edad, ciudad, descripcion, imagen))
            connection.commit()
            flash('Mascota registrada correctamente.')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error al registrar mascota: {e}")
        finally:
            connection.close()

    return render_template('adoptar.html')

@app.route


# Editar mascota
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
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            imagen = f"uploads/{filename}"
        else:
            imagen = request.form.get('imagen_actual')  # Mantener la imagen si no se sube nueva

        cur.execute("""
            UPDATE mascotas 
            SET nombre=%s, especie=%s, edad=%s, ciudad=%s, descripcion=%s, imagen=%s
            WHERE id=%s
        """, (nombre, especie, edad, ciudad, descripcion, imagen, id))
        conn.commit()
        cur.close()
        conn.close()
        flash('Mascota actualizada correctamente', 'success')
        return redirect(url_for('index'))

    # Si es GET, obtener datos
    cur.execute("SELECT * FROM mascotas WHERE id=%s", (id,))
    mascota = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('editar.html', mascota=mascota)

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id): 
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM mascotas WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Mascota eliminada correctamente', 'success')
    except Exception as e:
        flash(f"Error al eliminar mascota: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)