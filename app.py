from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('components.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_number TEXT,
            description TEXT,
            serial_number TEXT,
            date_in TEXT,
            location TEXT,
            status TEXT,
            technician TEXT,
            aircraft_reg TEXT,
            date_out TEXT,
            destination TEXT
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
        part_number = request.form['part_number']
        description = request.form['description']
        serial_number = request.form['serial_number']
        date_in = datetime.now().strftime('%Y-%m-%d')
        location = request.form['location']
        status = request.form['status']
        technician = request.form['technician']
        aircraft_reg = request.form['aircraft_reg']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO components (part_number, description, serial_number, date_in, location, status, technician, aircraft_reg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (part_number, description, serial_number, date_in, location, status, technician, aircraft_reg))
        conn.commit()
        conn.close()
        return redirect(url_for('inventory'))
    return render_template('register_in.html')

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    components = conn.execute('SELECT * FROM components WHERE date_out IS NULL').fetchall()
    conn.close()
    return render_template('inventory.html', components=components)

@app.route('/register_out/<int:id>', methods=['POST'])
def register_out(id):
    date_out = datetime.now().strftime('%Y-%m-%d')
    workshop = request.form['workshop']
    technician_out = request.form['technician_out']
    destination = request.form['destination']

    conn = get_db_connection()
    conn.execute('''
        UPDATE components
        SET date_out = ?, aircraft_reg = ?, technician = ?, destination = ?
        WHERE id = ?
    ''', (date_out, workshop, technician_out, destination, id))
    conn.commit()
    conn.close()
    return redirect(url_for('inventory'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
