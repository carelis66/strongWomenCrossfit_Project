from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'strongwomen_secret_key'

# === Configuración de sesión ===
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# === Debug de sesión ===
@app.before_request
def debug_session():
    print("🧩 Usuario en sesión:", session.get('usuario'), "| Rol:", session.get('rol'))


# ===== Conexión a MySQL =====
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="strongwomen"
    )


# ===== Usuarios del sistema =====
usuarios = {
    "admin": {"password": "1234", "rol": "ADMIN"},
    "recepcion": {"password": "abcd", "rol": "RECEPCION"},
    "coach": {"password": "5678", "rol": "COACH"}
}


# ===== Función auxiliar =====
def rol_permitido(*roles):
    return session.get('rol') in roles


# =========================================
#                  LOGIN
# =========================================

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/validar', methods=['POST'])
def validar():
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']

    if usuario in usuarios and usuarios[usuario]["password"] == contrasena:
        session['usuario'] = usuario
        session['rol'] = usuarios[usuario]["rol"]

        if session['rol'] == "ADMIN":
            return redirect(url_for('admin'))
        elif session['rol'] == "RECEPCION":
            return redirect(url_for('recepcion'))
        else:
            return redirect(url_for('coach'))
    else:
        return render_template('login.html', error="Credenciales inválidas")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# =========================================
#                DASHBOARDS
# =========================================

@app.route('/admin')
def admin():
    if not rol_permitido("ADMIN"):
        return redirect(url_for('login'))
    return render_template('dashboard_admin.html', rol=session.get('rol'))


@app.route('/recepcion')
def recepcion():
    if not rol_permitido("RECEPCION"):
        return redirect(url_for('login'))
    return render_template('dashboard_recepcion.html', rol=session.get('rol'))


@app.route('/coach')
def coach():
    if not rol_permitido("COACH"):
        return redirect(url_for('login'))
    return render_template('dashboard_coach.html', rol=session.get('rol'))


# =========================================
#              CRUD CLIENTAS
# =========================================

@app.route('/clientas')
def listar_clientas():
    if not rol_permitido("ADMIN", "RECEPCION", "COACH"):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientas")
    clientas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('lista_clientas.html', clientas=clientas, rol=session.get('rol'))


@app.route('/clientas/nueva', methods=['GET', 'POST'])
def nueva_clienta():
    if not rol_permitido("ADMIN", "RECEPCION"):
        return "Acceso denegado"

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']
        plan = request.form['plan']
        fecha = request.form['fecha']
        celular = request.form['celular']
        emergencia = request.form['emergencia']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientas (nombre, apellido, edad, plan, fecha_inscripcion, celular, emergencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, apellido, edad, plan, fecha, celular, emergencia))
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Clienta agregada correctamente.", "success")
        return redirect(url_for('listar_clientas'))

    return render_template('nueva_clienta.html')


@app.route('/clientas/editar/<int:id_clienta>', methods=['GET', 'POST'])
def editar_clienta(id_clienta):
    if not rol_permitido("ADMIN", "RECEPCION"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clientas WHERE id = %s", (id_clienta,))
    clienta = cursor.fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']
        plan = request.form['plan']
        fecha = request.form['fecha']
        celular = request.form['celular']
        emergencia = request.form['emergencia']

        cursor.execute("""
            UPDATE clientas
            SET nombre=%s, apellido=%s, edad=%s, plan=%s, fecha_inscripcion=%s,
                celular=%s, emergencia=%s
            WHERE id=%s
        """, (nombre, apellido, edad, plan, fecha, celular, emergencia, id_clienta))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Clienta actualizada correctamente.", "success")
        return redirect(url_for('listar_clientas'))

    cursor.close()
    conn.close()
    return render_template('editar_clienta.html', clienta=clienta)


@app.route('/clientas/eliminar/<int:id_clienta>')
def eliminar_clienta(id_clienta):
    if not rol_permitido("ADMIN"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientas WHERE id = %s", (id_clienta,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("🗑️ Clienta eliminada correctamente.", "info")
    return redirect(url_for('listar_clientas'))


@app.route('/clientas/ver/<int:id_clienta>')
def ver_clienta(id_clienta):
    if not rol_permitido("ADMIN", "RECEPCION", "COACH"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientas WHERE id = %s", (id_clienta,))
    clienta = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('ver_clienta.html', clienta=clienta, rol=session.get('rol'))


# =========================================
#                CRUD PLANES
# =========================================

@app.route('/planes')
def listar_planes():
    if not rol_permitido("ADMIN", "RECEPCION", "COACH"):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM planes")
    planes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('lista_planes.html', planes=planes, rol=session.get('rol'))


@app.route('/planes/nuevo', methods=['GET', 'POST'])
def nuevo_plan():
    if not rol_permitido("ADMIN", "RECEPCION"):
        return "Acceso denegado"

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        nivel = request.form['nivel']
        duracion = request.form['duracion']
        descripcion = request.form['descripcion']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO planes (nombre, precio, nivel, duracion, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, precio, nivel, duracion, descripcion))
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Plan agregado correctamente.", "success")
        return redirect(url_for('listar_planes'))

    return render_template('nuevo_plan.html')


@app.route('/planes/editar/<int:id_plan>', methods=['GET', 'POST'])
def editar_plan(id_plan):
    if not rol_permitido("ADMIN", "RECEPCION"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM planes WHERE id = %s", (id_plan,))
    plan = cursor.fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        nivel = request.form['nivel']
        duracion = request.form['duracion']
        descripcion = request.form['descripcion']

        cursor.execute("""
            UPDATE planes
            SET nombre=%s, precio=%s, nivel=%s, duracion=%s, descripcion=%s
            WHERE id=%s
        """, (nombre, precio, nivel, duracion, descripcion, id_plan))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Plan actualizado correctamente.", "success")
        return redirect(url_for('listar_planes'))

    cursor.close()
    conn.close()
    return render_template('editar_plan.html', plan=plan)


@app.route('/planes/eliminar/<int:id_plan>')
def eliminar_plan(id_plan):
    if not rol_permitido("ADMIN"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM planes WHERE id = %s", (id_plan,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("🗑️ Plan eliminado correctamente.", "info")
    return redirect(url_for('listar_planes'))


# =========================================
#                CRUD RUTINAS
# =========================================

@app.route('/rutinas')
def listar_rutinas():
    if not rol_permitido("COACH", "ADMIN"):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rutinas ORDER BY dia")
    rutinas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('lista_rutinas.html', rutinas=rutinas, rol=session.get('rol'))


@app.route('/rutinas/nueva', methods=['GET', 'POST'])
def nueva_rutina():
    if not rol_permitido("COACH", "ADMIN"):
        return "Acceso denegado"

    if request.method == 'POST':
        nombre = request.form['nombre']
        dia = request.form['dia']
        nivel = request.form['nivel']
        descripcion = request.form['descripcion']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rutinas (nombre, dia, nivel, descripcion)
            VALUES (%s, %s, %s, %s)
        """, (nombre, dia, nivel, descripcion))
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Rutina creada correctamente.", "success")
        return redirect(url_for('listar_rutinas'))

    return render_template('nueva_rutina.html')


@app.route('/rutinas/editar/<int:id_rutina>', methods=['GET', 'POST'])
def editar_rutina(id_rutina):
    if not rol_permitido("COACH", "ADMIN"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM rutinas WHERE id = %s", (id_rutina,))
    rutina = cursor.fetchone()

    if not rutina:
        cursor.close()
        conn.close()
        return "❌ Rutina no encontrada"

    if request.method == 'POST':
        nombre = request.form['nombre']
        dia = request.form['dia']
        nivel = request.form['nivel']
        descripcion = request.form['descripcion']

        cursor.execute("""
            UPDATE rutinas
            SET nombre=%s, dia=%s, nivel=%s, descripcion=%s
            WHERE id=%s
        """, (nombre, dia, nivel, descripcion, id_rutina))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Rutina actualizada correctamente.", "success")
        return redirect(url_for('listar_rutinas'))

    cursor.close()
    conn.close()

    return render_template('editar_rutina.html', rutina=rutina, rol=session.get('rol'))


@app.route('/rutinas/eliminar/<int:id_rutina>')
def eliminar_rutina(id_rutina):
    if not rol_permitido("COACH", "ADMIN"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rutinas WHERE id = %s", (id_rutina,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("🗑️ Rutina eliminada correctamente.", "info")
    return redirect(url_for('listar_rutinas'))


# =========================================
#                CRUD TURNOS
# =========================================

@app.route('/turnos')
def listar_turnos():
    if not rol_permitido("RECEPCION"):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM turnos ORDER BY fecha, hora")
    turnos = cursor.fetchall()
    cursor.close()
    conn.close()

    turnos_por_fecha = defaultdict(list)
    for t in turnos:
        turnos_por_fecha[t['fecha']].append(t)

    return render_template('lista_turnos.html', turnos_por_fecha=turnos_por_fecha,
                           ahora=datetime.now(), rol=session.get('rol'))


@app.route('/turnos/nuevo', methods=['GET', 'POST'])
def nuevo_turno():
    if not rol_permitido("RECEPCION"):
        return "Acceso denegado"

    if request.method == 'POST':
        nombre_clienta = request.form['nombre_clienta']
        fecha = request.form['fecha']
        hora = request.form['hora']

        if hora < "07:00" or hora >= "21:00":
            return render_template('nuevo_turno.html',
                                   error="El horario debe estar entre 07:00 y 21:00.")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM turnos WHERE fecha=%s AND hora=%s",
                       (fecha, hora))
        existe = cursor.fetchone()

        if existe:
            cursor.close()
            conn.close()
            return render_template('nuevo_turno.html',
                                   error="Ya existe un turno agendado en ese horario.")

        cursor.execute("""
            INSERT INTO turnos (nombre_clienta, fecha, hora, estado)
            VALUES (%s, %s, %s, %s)
        """, (nombre_clienta, fecha, hora, "Pendiente"))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Turno agregado correctamente.", "success")
        return redirect(url_for('listar_turnos'))

    return render_template('nuevo_turno.html')


@app.route('/turnos/cambiar_estado/<int:id_turno>/<string:nuevo_estado>')
def cambiar_estado_turno(id_turno, nuevo_estado):
    if not rol_permitido("RECEPCION"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE turnos SET estado=%s WHERE id=%s",
                   (nuevo_estado, id_turno))
    conn.commit()
    cursor.close()
    conn.close()

    flash("🔄 Estado actualizado correctamente.", "info")
    return redirect(url_for('listar_turnos'))


# =========================================
#                CRUD USUARIOS
# =========================================

@app.route('/usuarios')
def listar_usuarios():
    if not rol_permitido("ADMIN"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('lista_usuarios.html', usuarios=usuarios,
                           rol=session.get('rol'))


@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
def nuevo_usuario():
    if not rol_permitido("ADMIN"):
        return "Acceso denegado"

    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        password = request.form['password']
        rol = request.form['rol']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, usuario, password, rol)
            VALUES (%s, %s, %s, %s)
        """, (nombre, usuario, password, rol))
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Usuario agregado correctamente.", "success")
        return redirect(url_for('listar_usuarios'))

    return render_template('nuevo_usuario.html')


@app.route('/usuarios/editar/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    if not rol_permitido("ADMIN"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id_usuario,))
    usuario = cursor.fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario_input = request.form['usuario']
        password = request.form['password']
        rol = request.form['rol']

        cursor.execute("""
            UPDATE usuarios
            SET nombre=%s, usuario=%s, password=%s, rol=%s
            WHERE id=%s
        """, (nombre, usuario_input, password, rol, id_usuario))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Usuario actualizado correctamente.", "success")
        return redirect(url_for('listar_usuarios'))

    cursor.close()
    conn.close()

    return render_template('editar_usuario.html', usuario=usuario)


@app.route('/usuarios/eliminar/<int:id_usuario>')
def eliminar_usuario(id_usuario):
    if not rol_permitido("ADMIN"):
        return "Acceso denegado"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("🗑️ Usuario eliminado correctamente.", "info")
    return redirect(url_for('listar_usuarios'))


# =========================================
#                 RUN APP
# =========================================

if __name__ == '__main__':
    app.run(debug=True)







