from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_FILE = 'components.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_number TEXT,
            description TEXT,
            serial_number TEXT,
            entry_date TEXT,
            location TEXT,
            status TEXT,
            technician TEXT,
            aircraft_registration TEXT,
            output_location TEXT,
            output_technician TEXT,
            output_destination TEXT,
            output_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_in', methods=['GET', 'POST'])
def register_in():
    if request.method == 'POST':
        data = (
            request.form['part_number'],
            request.form['description'],
            request.form['serial_number'],
            request.form['location'],
            request.form['status'],
            request.form['technician'],
            request.form['aircraft_registration']
        )

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO components (
                part_number, description, serial_number,
                entry_date, location, status, technician, aircraft_registration
            )
            VALUES (?, ?, ?, DATE('now'), ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()

        return redirect('/inventory')

    return render_template('register_in.html')

@app.route('/inventory')
def inventory():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM components WHERE output_date IS NULL')
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    components = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return render_template('inventory.html', components=components)

@app.route('/register_out/<int:id>', methods=['POST'])
def register_out(id):
    output_location = request.form['output_location']
    output_technician = request.form['output_technician']
    output_destination = request.form['output_destination']

    print(f"SALIDA REGISTRADA -> ID: {id}, Ubicación: {output_location}, Técnico: {output_technician}, Destino: {output_destination}")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE components
        SET output_location = ?, output_technician = ?, output_destination = ?, output_date = DATE('now')
        WHERE id = ?
    ''', (output_location, output_technician, output_destination, id))
    conn.commit()
    conn.close()

    return redirect(url_for('inventory'))

@app.route('/historial_salidas')
@app.route('/history')  # ruta alternativa opcional
def historial_salidas():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM components
        WHERE output_date IS NOT NULL
        ORDER BY output_date DESC
    ''')
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    salidas = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return render_template('historial_salidas.html', salidas=salidas)

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/chart_data')
def chart_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT aircraft_registration,
               COUNT(CASE WHEN output_date IS NULL THEN 1 END) AS entradas,
               COUNT(CASE WHEN output_date IS NOT NULL THEN 1 END) AS salidas
        FROM components
        GROUP BY aircraft_registration
    ''')
    rows = cursor.fetchall()
    conn.close()

    data = {
        'labels': [row[0] for row in rows],
        'entradas': [row[1] for row in rows],
        'salidas': [row[2] for row in rows]
    }
    return jsonify(data)

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # usarás variable de entorno
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Crear las tablas si no existen
with app.app_context():
    db.create_all()

# Solo para depuración
print("DATABASE_URL:", os.environ.get('DATABASE_URL'))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

