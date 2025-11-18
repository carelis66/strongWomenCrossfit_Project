from db import get_connection

def obtener_todas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientas ORDER BY nombre ASC")
    clientas = cursor.fetchall()
    conn.close()
    return clientas

def agregar_clienta(nombre, apellido, edad, plan, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO clientas (nombre, apellido, edad, plan, fecha) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (nombre, apellido, edad, plan, fecha))
    conn.commit()
    conn.close()

def eliminar_clienta(id_clienta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientas WHERE id = %s", (id_clienta,))
    conn.commit()
    conn.close()

