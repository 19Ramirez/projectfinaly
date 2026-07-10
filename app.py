from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime
import os
import psycopg2

app = Flask(__name__)
VERSION = "4.0.0"

# Configuración de conexión a PostgreSQL
DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "taller_db")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres_password")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
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
                fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✔ Base de datos inicializada correctamente con tabla de PRODUCTOS.")
    except Exception as e:
        print(f"❌ Error al conectar o inicializar Base de Datos: {e}")

TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGA - Sistema de Gestión de Almacén</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); width: 750px; margin-bottom: 20px; }
        h1 { color: #2c3e50; text-align: center; font-size: 26px; margin-bottom: 5px; }
        h2 { color: #95a5a6; text-align: center; font-size: 13px; margin-top: 0; margin-bottom: 25px; }
        .section-title { border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; color: #16a085; font-size: 16px; margin-top: 20px; font-weight: bold; margin-bottom: 15px; }
        
        /* Formularios */
        .form-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 12px; }
        input, select, button { width: 100%; padding: 10px; border: 1px solid #bdc3c7; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        
        /* Botones */
        button { background-color: #1abc9c; color: white; font-weight: bold; cursor: pointer; border: none; transition: background 0.2s; }
        button:hover { background-color: #16a085; }
        .btn-update { background-color: #f39c12; color: white; padding: 5px 10px; font-size: 12px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-right: 5px;}
        .btn-update:hover { background-color: #d35400; }
        .btn-delete { background-color: #e74c3c; color: white; padding: 5px 10px; font-size: 12px; text-decoration: none; border-radius: 4px; font-weight: bold;}
        .btn-delete:hover { background-color: #c0392b; }
        
        /* Alertas */
        .alert { padding: 12px; background: #e8f8f5; color: #117a65; border-radius: 6px; font-size: 14px; margin-bottom: 15px; text-align: center; font-weight: bold; border-left: 5px solid #1abc9c; }
        .alert.error { background: #fdf2f2; color: #922b21; border-left-color: #e74c3c; }
        
        /* Tabla CRUD */
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #fafbfc; border-radius: 6px; overflow: hidden; border: 1px solid #eaeded; }
        th, td { padding: 12px; text-align: left; font-size: 13px; border-bottom: 1px solid #eaeded; }
        th { background-color: #e8f8f5; color: #16a085; font-weight: bold; }
        tr:hover { background-color: #f2f4f4; }
        .badge-out { background-color: #f9e7e7; color: #c0392b; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
        
        footer { text-align:center; margin-top:25px; font-size:11px; color:#bdc3c7; border-top: 1px solid #ecf0f1; padding-top: 10px; width: 100%; }
    </style>
</head>
<body>

<div class="container">
    <h1>📦 Sistema de Control de Inventario (SGA)</h1>
    <h2>Panel DevOps | Base de Datos PostgreSQL</h2>

    {% if msg_db %}
        <div class="alert {% if 'Error' in msg_db or '❌' in msg_db %}error{% endif %}">{{ msg_db }}</div>
    {% endif %}

    <div class="section-title">
        {% if prod_edit %} 📝 Modificar Producto (ID: {{ prod_edit[0] }}) {% else %} ➕ Añadir Nuevo Producto al Almacén {% endif %}
    </div>
    
    <form method="POST" action="{% if prod_edit %}/actualizar/{{ prod_edit[0] }}{% else %}/registrar{% endif %}">
        <div class="form-grid">
            <input type="text" name="nombre" placeholder="Nombre del Producto" value="{{ prod_edit[1] if prod_edit else '' }}" required>
            
            <select name="categoria">
                <option value="Electrónica" {% if prod_edit and prod_edit[2] == 'Electrónica' %}selected{% endif %}>Electrónica</option>
                <option value="Lácteos" {% if prod_edit and prod_edit[2] == 'Lácteos' %}selected{% endif %}>Lácteos / Alimentos</option>
                <option value="Ropa" {% if prod_edit and prod_edit[2] == 'Ropa' %}selected{% endif %}>Ropa / Textil</option>
                <option value="Limpieza" {% if prod_edit and prod_edit[2] == 'Limpieza' %}selected{% endif %}>Limpieza</option>
                <option value="Otros" {% if prod_edit and prod_edit[2] == 'Otros' %}selected{% endif %}>Otros</option>
            </select>

            <input type="number" step="0.01" name="precio" placeholder="Precio ($)" value="{{ prod_edit[3] if prod_edit else '' }}" min="0.01" required>
            <input type="number" name="stock" placeholder="Stock Inicial" value="{{ prod_edit[4] if prod_edit else '' }}" min="0" required>
        </div>
        <button type="submit">{% if prod_edit %}Actualizar Información (UPDATE){% else %}Guardar Producto en Stock (CREATE){% endif %}</button>
        {% if prod_edit %}
            <a href="/" style="display: block; text-align: center; margin-top: 8px; font-size: 13px; color: #95a5a6; text-decoration: none;">Cancelar Modificación</a>
        {% endif %}
    </form>

    <div class="section-title">📋 Stock Actual en Almacén (READ / UPDATE / DELETE)</div>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Producto</th>
                <th>Categoría</th>
                <th>Precio Unitario</th>
                <th>Stock Disponible</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for prod in productos %}
            <tr>
                <td>{{ prod[0] }}</td>
                <td><strong>{{ prod[1] }}</strong></td>
                <td>{{ prod[2] }}</td>
                <td style="color: #27ae60; font-weight: bold;">${{ "%.2f"|format(prod[3]) }}</td>
                <td>
                    {% if prod[4] == 0 %}
                        <span class="badge-out">Agotado (0)</span>
                    {% else %}
                        {{ prod[4] }} unidades
                    {% endif %}
                </td>
                <td>
                    <a class="btn-update" href="/editar/{{ prod[0] }}">Editar</a>
                    <a class="btn-delete" href="/eliminar/{{ prod[0] }}" onclick="return confirm('¿Seguro que deseas eliminar este producto del inventario?')">Eliminar</a>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="6" style="text-align: center; color: #bdc3c7;">El almacén está vacío. Registra un producto arriba.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <footer>
        Hora del Sistema: {{ hora }}<br>
        Arquitectura de Contenedores Unificada: Local & VPS Cloud (V{{ version }})
    </footer>
</div>

</body>
</html>
"""

# READ - Listar productos
@app.route("/")
def index():
    productos = []
    msg_db = request.args.get("msg_db", None)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, precio, stock FROM productos ORDER BY id DESC;")
        productos = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al traer productos: {e}")

    return render_template_string(
        TEMPLATE_HTML,
        version=VERSION,
        hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        productos=productos,
        prod_edit=None,
        msg_db=msg_db
    )

# CREATE - Insertar producto
@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre")
    categoria = request.form.get("categoria")
    precio = request.form.get("precio")
    stock = request.form.get("stock")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO productos (nombre, categoria, precio, stock) VALUES (%s, %s, %s, %s);", 
                    (nombre, categoria, precio, stock))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index", msg_db="✔ Producto añadido exitosamente (CREATE)"))
    except Exception as e:
        return redirect(url_for("index", msg_db=f"❌ Error al insertar producto: {str(e)}"))

# Cargar datos para editar (UPDATE)
@app.route("/editar/<int:id>")
def editar(id):
    productos = []
    prod_edit = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, precio, stock FROM productos ORDER BY id DESC;")
        productos = cur.fetchall()
        
        cur.execute("SELECT id, nombre, categoria, precio, stock FROM productos WHERE id = %s;", (id,))
        prod_edit = cur.fetchone()
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al buscar para editar: {e}")

    return render_template_string(
        TEMPLATE_HTML,
        version=VERSION,
        hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        productos=productos,
        prod_edit=prod_edit,
        msg_db=f"Editando el producto ID: {id}"
    )

# UPDATE - Guardar cambios
@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    nombre = request.form.get("nombre")
    categoria = request.form.get("categoria")
    precio = request.form.get("precio")
    stock = request.form.get("stock")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE productos SET nombre = %s, categoria = %s, precio = %s, stock = %s WHERE id = %s;", 
                    (nombre, categoria, precio, stock, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index", msg_db=f"✔ Producto ID {id} actualizado con éxito (UPDATE)"))
    except Exception as e:
        return redirect(url_for("index", msg_db=f"❌ Error al actualizar el producto: {str(e)}"))

# DELETE - Eliminar producto
@app.route("/eliminar/<int:id>")
def eliminar(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM productos WHERE id = %s;", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index", msg_db=f"✔ Producto ID {id} eliminado del inventario (DELETE)"))
    except Exception as e:
        return redirect(url_for("index", msg_db=f"❌ Error al eliminar el producto: {str(e)}"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)