from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import psycopg2
import time

app = Flask(__name__)
VERSION = "5.1.0"

# Configuración de carpetas y formatos permitidos para imágenes
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que la carpeta de imágenes exista localmente al arrancar
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración de conexión a PostgreSQL
DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "taller_db")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres_password")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    retries = 5
    while retries > 0:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Creamos la tabla de productos si no existe
            cur.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    categoria VARCHAR(50) NOT NULL,
                    precio NUMERIC(10, 2) NOT NULL,
                    stock INT NOT NULL DEFAULT 0,
                    imagen VARCHAR(255) DEFAULT 'default.png',
                    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("✔ Base de datos inicializada correctamente con soporte para IMÁGENES.")
            return
        except Exception as e:
            retries -= 1
            print(f"⏳ Esperando a que la base de datos esté lista... Reintentos restantes: {retries}")
            time.sleep(3)
            
    print("❌ Error definitivo: No se pudo conectar a la Base de Datos tras varios intentos.")

TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGA - Gestión de Almacén con Multimedia</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); width: 850px; margin-bottom: 20px; }
        h1 { color: #2c3e50; text-align: center; font-size: 26px; margin-bottom: 5px; }
        h2 { color: #95a5a6; text-align: center; font-size: 13px; margin-top: 0; margin-bottom: 25px; }
        .section-title { border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; color: #2980b9; font-size: 16px; margin-top: 20px; font-weight: bold; margin-bottom: 15px; }
        
        .form-grid { display: grid; grid-template-columns: 2fr 1.2fr 1fr 1fr; gap: 10px; margin-bottom: 12px; }
        .file-input-container { margin-bottom: 12px; }
        input, select, button { width: 100%; padding: 10px; border: 1px solid #bdc3c7; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        input[type="file"] { padding: 5px; background: #fafbfc; }
        
        button { background-color: #3498db; color: white; font-weight: bold; cursor: pointer; border: none; transition: background 0.2s; }
        button:hover { background-color: #2980b9; }
        .btn-update { background-color: #f39c12; color: white; padding: 5px 10px; font-size: 12px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-right: 5px;}
        .btn-update:hover { background-color: #d35400; }
        .btn-delete { background-color: #e74c3c; color: white; padding: 5px 10px; font-size: 12px; text-decoration: none; border-radius: 4px; font-weight: bold;}
        .btn-delete:hover { background-color: #c0392b; }
        
        .alert { padding: 12px; background: #ebf5fb; color: #21618c; border-radius: 6px; font-size: 14px; margin-bottom: 15px; text-align: center; font-weight: bold; border-left: 5px solid #3498db; }
        .alert.error { background: #fdf2f2; color: #922b21; border-left-color: #e74c3c; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #fafbfc; border-radius: 6px; overflow: hidden; border: 1px solid #eaeded; }
        th, td { padding: 12px; text-align: left; font-size: 13px; border-bottom: 1px solid #eaeded; vertical-align: middle; }
        th { background-color: #ebf5fb; color: #2980b9; font-weight: bold; }
        tr:hover { background-color: #f2f4f4; }
        
        .prod-img { width: 50px; height: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #d5dbdb; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .badge-out { background-color: #f9e7e7; color: #c0392b; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
        
        footer { text-align:center; margin-top:25px; font-size:11px; color:#bdc3c7; border-top: 1px solid #ecf0f1; padding-top: 10px; width: 100%; }
    </style>
</head>
<body>

<div class="container">
    <h1>📦 Catálogo de Productos Multimedia</h1>
    <h2>Panel de Control DevOps | URL Activa: fd.byronrm.com</h2>

    {% if msg_db %}
        <div class="alert {% if 'Error' in msg_db or '❌' in msg_db %}error{% endif %}">{{ msg_db }}</div>
    {% endif %}

    <div class="section-title">
        {% if prod_edit %} 📝 Modificar Producto (ID: {{ prod_edit[0] }}) {% else %} ➕ Registrar Producto con Imagen {% endif %}
    </div>
    
    <form method="POST" action="{% if prod_edit %}/actualizar/{{ prod_edit[0] }}{% else %}/registrar{% endif %}" enctype="multipart/form-data">
        <div class="form-grid">
            <input type="text" name="nombre" placeholder="Nombre del Producto" value="{{ prod_edit[1] if prod_edit else '' }}" required>
            
            <select name="categoria">
                <option value="Electrónica" {% if prod_edit and prod_edit[2] == 'Electrónica' %}selected{% endif %}>Electrónica</option>
                <option value="Alimentos" {% if prod_edit and prod_edit[2] == 'Alimentos' %}selected{% endif %}>Alimentos / Lácteos</option>
                <option value="Textil" {% if prod_edit and prod_edit[2] == 'Textil' %}selected{% endif %}>Textil / Ropa</option>
                <option value="Otros" {% if prod_edit and prod_edit[2] == 'Otros' %}selected{% endif %}>Otros</option>
            </select>

            <input type="number" step="0.01" name="precio" placeholder="Precio ($)" value="{{ prod_edit[3] if prod_edit else '' }}" min="0.01" required>
            <input type="number" name="stock" placeholder="Stock" value="{{ prod_edit[4] if prod_edit else '' }}" min="0" required>
        </div>
        
        <div class="file-input-container">
            <label style="font-size: 12px; color: #7f8c8d; display:block; margin-bottom:4px;">Imagen del producto:</label>
            <input type="file" name="imagen" accept="image/*">
        </div>

        <button type="submit">{% if prod_edit %}Actualizar Producto (UPDATE){% else %}Insertar en Inventario (CREATE){% endif %}</button>
        {% if prod_edit %}
            <a href="/" style="display: block; text-align: center; margin-top: 8px; font-size: 13px; color: #95a5a6; text-decoration: none;">Cancelar Edición</a>
        {% endif %}
    </form>

    <div class="section-title">📋 Inventario Activo (Visualización en la Nube)</div>
    <table>
        <thead>
            <tr>
                <th>Foto</th>
                <th>ID</th>
                <th>Producto</th>
                <th>Categoría</th>
                <th>Precio</th>
                <th>Stock</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for prod in productos %}
            <tr>
                <td>
                    <img class="prod-img" src="/static/uploads/{{ prod[5] }}" onerror="this.onerror=null; this.src='https://placehold.co/100x100?text=Sin+Foto';">
                </td>
                <td>{{ prod[0] }}</td>
                <td><strong>{{ prod[1] }}</strong></td>
                <td>{{ prod[2] }}</td>
                <td style="color: #27ae60; font-weight: bold;">${{ "%.2f"|format(prod[3]) }}</td>
                <td>
                    {% if prod[4] == 0 %}
                        <span class="badge-out">Agotado</span>
                    {% else %}
                        {{ prod[4] }} uds
                    {% endif %}
                </td>
                <td>
                    <a class="btn-update" href="/editar/{{ prod[0] }}">Editar</a>
                    <a class="btn-delete" href="/eliminar/{{ prod[0] }}" onclick="return confirm('¿Eliminar producto?')">Eliminar</a>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="7" style="text-align: center; color: #bdc3c7;">El almacén está vacío.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <footer>
        Hora del Sistema: {{ hora }}<br>
        Docker Volumes Activos | Entorno Producción Enlazado
    </footer>
</div>

</body>
</html>
"""

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/")
def index():
    productos = []
    msg_db = request.args.get("msg_db", None)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, precio, stock, imagen FROM productos ORDER BY id DESC;")
        productos = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al traer productos: {e}")

    return render_template_string(
        TEMPLATE_HTML, version=VERSION, hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        productos=productos, prod_edit=None, msg_db=msg_db
    )

@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre")
    categoria = request.form.get("categoria")
    precio = request.form.get("precio")
    stock = request.form.get("stock")
    
    filename = 'default.png'
    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"prod_{int(datetime.now().timestamp())}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO productos (nombre, categoria, precio, stock, imagen) VALUES (%s, %s, %s, %s, %s);", 
                    (nombre, categoria, precio, stock, filename))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index", msg_db="✔ Producto creado con éxito."))
    except Exception as e:
        return redirect(url_for("index", msg_db=f"❌ Error al insertar: {str(e)}"))

@app.route("/editar/<int:id>")
def editar(id):
    productos = []
    prod_edit = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, precio, stock, imagen FROM productos ORDER BY id DESC;")
        productos = cur.fetchall()
        cur.execute("SELECT id, nombre, categoria, precio, stock, imagen FROM productos WHERE id = %s;", (id,))
        prod_edit = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al editar: {e}")

    return render_template_string(
        TEMPLATE_HTML, version=VERSION, hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        productos=productos, prod_edit=prod_edit, msg_db=f"Modificando producto ID: {id}"
    )

@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    nombre = request.form.get("nombre")
    categoria = request.form.get("categoria")
    precio = request.form.get("precio")
    stock = request.form.get("stock")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if 'imagen' in request.files and request.files['imagen'].filename != '':
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"prod_{int(datetime.now().timestamp())}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cur.execute("UPDATE productos SET nombre=%s, categoria=%s, precio=%s, stock=%s, imagen=%s WHERE id=%s;", 
                            (nombre, categoria, precio, stock, filename, id))
        else:
            cur.execute("UPDATE productos SET nombre=%s, categoria=%s, precio=%s, stock=%s WHERE id=%s;", 
                        (nombre, categoria, precio, stock, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index", msg_db=f"✔ Producto ID {id} actualizado con éxito."))
    except Exception as e:
        return redirect(url_for("index", msg_db=f"❌ Error al actualizar: {str(e)}"))

@app.route("/eliminar/<int:id>")
def eliminar(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM productos WHERE id = %s;", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index", msg_db=f"✔ Producto ID {id} eliminado."))
    except Exception as e:
        return redirect(url_for("index", msg_db=f"❌ Error al eliminar: {str(e)}"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)