from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# ⚠️ Corregido: se especifica dónde están los templates
app = Flask(__name__, template_folder="templates")



# Configuración para PostgreSQL desde Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de base de datos
class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(100))
    description = db.Column(db.String(200))
    serial_number = db.Column(db.String(100))
    entry_date = db.Column(db.Date, default=datetime.utcnow)
    location = db.Column(db.String(100))
    status = db.Column(db.String(100))
    technician = db.Column(db.String(100))
    aircraft_registration = db.Column(db.String(100))
    wo_number = db.Column(db.String(100))  # ← Número de tarea agregado
    output_location = db.Column(db.String(100))
    output_technician = db.Column(db.String(100))
    output_destination = db.Column(db.String(100))
    output_date = db.Column(db.Date)

# Crear tablas si no existen
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_in', methods=['GET', 'POST'])
def register_in():
    if request.method == 'POST':
        component = Component(
            part_number=request.form['part_number'],
            description=request.form['description'],
            serial_number=request.form['serial_number'],
            location=request.form['location'],
            status=request.form['status'],
            technician=request.form['technician'],
            aircraft_registration=request.form['aircraft_registration'],
            wo_number=request.form['wo_number']
        )
        db.session.add(component)
        db.session.commit()
        return redirect('/inventory')
    return render_template('register_in.html')

@app.route('/inventory')
def inventory():
    components = Component.query.filter_by(output_date=None)
    return render_template('inventory.html', components=components)  # ← asumimos que tenés esta plantilla
