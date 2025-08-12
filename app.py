from flask import Flask, request, render_template, flash, url_for, redirect
import pymysql

app = Flask(__name__)
app.secret_key = 'secretkey'

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


if __name__ == '__main__':
    app.run(debug=True)