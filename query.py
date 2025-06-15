import sqlite3

def obtener_salidas():
    conn = sqlite3.connect('components.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM components
        WHERE output_date IS NOT NULL
        ORDER BY output_date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Mostrar en terminal
print(obtener_salidas())
