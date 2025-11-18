import pytest
from app import app 

# Configuración para simular un navegador (cliente de pruebas)
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_redirect(client):
    """Verifica que el login sea la ruta principal"""
    response = client.get('/') # simulamos abrir http://127.0.0.1:5000/
    assert response.status_code == 200 #  Debe responder "OK"
    assert b'Strong Women Crossfit' in response.data # EL texto del login está en el HTML
    

def test_login_correcto_admin(client):
    """Verifica que el login redirija correctamente al panel del admin"""
    response = client.post('/validar', data={
        'usuario': 'admin',
        'contrasena': '1234'
    }, follow_redirects=True) #  sigue la redirección automática

    # Comprueba que el dashboard admin se cargue correctamente
    assert response.status_code == 200
    assert b'Panel Admin' in response.data # texto que esté en dashboard_admin.html
    
    
def test_login_incorrecto(client):
    """Verifica que el sistema muestre error al usar credenciales inválidas"""
    response = client.post('/validar', data={
        'usuario': 'admin',
        'contrasena': 'malapass'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Credenciales inválidas' in response.data.decode('utf-8')
    
def test_acceso_sin_login(client):
    """Verifica que un usuario no logueado sea redirigido al login"""
    response = client.get('/admin', follow_redirects=True)

    # El servidor debe responder con 200 porque sigue la redirección hasta el login
    assert response.status_code == 200
    # El contenido debería contener algo del login (por ejemplo, 'Iniciar sesión' o 'Credenciales inválidas')
    assert 'Strong Women Crossfit' in response.data.decode('utf-8')
    
def test_restriccion_por_rol(client):
    """Verifica que un usuario coach no pueda acceder al panel admin"""
    
    # Simulamos que el usuario coach inicia sesión
    with client.session_transaction() as session:
        session['usuario'] = 'coach'
        session['rol'] = 'COACH'

    response = client.get('/admin', follow_redirects=True)

    # Debe redirigir (porque el rol no tiene permisos)
    assert response.status_code == 200
    assert 'Strong Women Crossfit' in response.data.decode('utf-8')