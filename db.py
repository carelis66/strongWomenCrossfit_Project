import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # tu usuario de MySQL
        password="",          # tu contraseña (si tenés)
        database="strongwomen"  # nombre de tu base de datos
    )
