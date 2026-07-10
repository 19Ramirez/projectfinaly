from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime
import os
import psycopg2

app = Flask(__name__)
VERSION = "2.0.0"

# Variables de entorno para conectar de manera segura a la Base de Datos
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
        # Crear la tabla de usuarios requerida por la rúbrica si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✔ Base de datos inicializada de forma correcta.")
    except Exception as e:
        print(f"❌ Error al conectar o inicializar Base de Datos: {e}")

TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proyecto Final DevOps</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f0f4f8; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); width: 420px; margin-bottom: 20px; }
        h1 { color: #1a365d; text-align: center; font-size: 24px; margin-bottom: 5px; }
        h2 { color: #718096; text-align: center; font-size: 13px; margin-top: 0; margin-bottom: 25px; }
        .section-title { border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; color: #2b6cb0; font-size: 16px; margin-top: 20px; font-weight: bold; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #cbd5e0; border-radius: 6px; box-sizing: border-box; font-size: 15px; }
        button { background-color: #2b6cb0; color: white; font-weight: bold; cursor: pointer; border: none; transition: background 0.2s; }
        button:hover { background-color: #2c5282; }
        .alert { padding: 10px; background: #c6f6d5; color: #22543d; border-radius: 6px; font-size: 14px; margin-bottom: 10px; text-align: center; font-weight: bold; }
        .user-box { background: #f7fafc; padding: 10px; border-radius: 6px; font-size: 13px; max-height: 120px; overflow-y: auto; margin-top: 10px; border: 1px solid #edf2f7; }
    </style>
</head>
<body>

<div class="container">
    <h1>🚀 Proyecto Final DevOps</h1>
    <h2>Servidor Contabo Personal | Versión {{ version }}</h2>

    <div class="section-title">👤 Registro de Usuarios (Persistencia PostgreSQL)</div>
    {% if msg_db %}
        <div class="alert">{{ msg_db }}</div>
    {% endif %}
    <form method="POST" action="/registrar">
        <input type="text" name="nombre" placeholder="Nombre Completo" required>
        <input type="email" name="email" placeholder="Correo Electrónico" required>
        <button type="submit">Guardar en Base de Datos</button>
    </form>

    <div class="user-box">
        <strong>Usuarios en el sistema:</strong><br>
        {% for user in usuarios %}
            • {{ user[1] }} — <span style="color:#718096;">{{ user[2] }}</span><br>
        {% else %}
            <span style="color:#a0aec0;">No hay registros en la base de datos.</span>
        {% endfor %}
    </div>

    <div class="section-title">💱 DevOps FX Converter</div>
    <form method="POST" action="/">
        <input type="number" step="any" name="monto" placeholder="Monto en USD" value="{{ monto }}" min="0" required>
        <select name="divisa_destino">
            <option value="EUR" {% if divisa_destino == 'EUR' %}selected{% endif %}>🇪🇺 EUR - Euro</option>
            <option value="MXN" {% if divisa_destino == 'MXN' %}selected{% endif %}>🇲🇽 MXN - Peso Mexicano</option>
            <option value="JPY" {% if divisa_destino == 'JPY' %}selected{% endif %}>🇯🇵 JPY - Yen Japonés</option>
        </select>
        <button type="submit">Calcular Conversión</button>
    </form>

    {% if resultado %}
        <div style="background:#ebf8ff; padding:12px; border-left:4px solid #3182ce; margin-top:10px; color:#2b6cb0; font-weight:bold; border-radius: 4px;">
            Equivale a: {{ resultado }} {{ divisa_destino }}
        </div>
    {% endif %}

    <footer style="text-align:center; margin-top:25px; font-size:11px; color:#a0aec0; border-top: 1px solid #e2e8f0; padding-top: 10px;">
        Hora del Servidor: {{ hora }}<br>
        Infraestructura: Docker Swarm & Traefik Habilitado
    </footer>
</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    monto = ""
    divisa_destino = "EUR"
    msg_db = request.args.get("msg_db", None)
    
    if request.method == "POST":
        try:
            monto_input = request.form.get("monto")
            divisa_destino = request.form.get("divisa_destino")
            tasas = {"EUR": 0.92, "MXN": 17.05, "JPY": 150.00}
            if monto_input:
                monto = float(monto_input)
                resultado = f"{monto * tasas.get(divisa_destino, 1.0):,.2f}"
        except Exception as e:
            resultado = f"Error: {str(e)}"

    usuarios = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, email FROM usuarios ORDER BY id DESC;")
        usuarios = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al traer usuarios: {e}")

    return render_template_string(
        TEMPLATE_HTML,
        version=VERSION,
        hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        resultado=resultado,
        monto=monto,
        divisa_destino=divisa_destino,
        usuarios=usuarios,
        msg_db=msg_db
    )

@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nombre, email) VALUES (%s, %s);", (nombre, email))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index", msg_db="✔ ¡Usuario registrado exitosamente!"))
    except Exception as e:
        return redirect(url_for("index", msg_db=f"❌ Error en la base de datos: {str(e)}"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)