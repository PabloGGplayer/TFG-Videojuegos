import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
import models

# 1. Base de datos SQLite en memoria aislada para los tests (no toca PostgreSQL)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sobrescribimos la dependencia de BD de la app
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    """Crea todas las tablas antes de cada test y las borra al terminar."""
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

client = TestClient(app)


# --- TESTS DE INFRAESTRUCTURA Y SEGURIDAD ---

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensaje": "¡Hola mundo!"}


def test_registro_usuario_y_seguridad_password():
    # Creamos un superadmin sin empresa asociada
    payload = {
        "nombre": "Admin Global",
        "email": "superadmin@tfg.com",
        "rol": "superadmin",
        "empresa_id": None,
        "password": "MiPasswordSecreta123"
    }
    response = client.post("/usuarios/", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Verificamos que devuelve los datos esperados y NUNCA expone la contraseña
    assert data["email"] == "superadmin@tfg.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_registro_email_duplicado_bloqueado():
    payload = {
        "nombre": "Usuario Uno",
        "email": "duplicado@tfg.com",
        "rol": "superadmin",
        "empresa_id": None,
        "password": "password123"
    }
    res1 = client.post("/usuarios/", json=payload)
    assert res1.status_code == 200

    # Intentar registrar el mismo email debe fallar con 400
    res2 = client.post("/usuarios/", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "El email ya está registrado"


def test_login_exitoso_devuelve_jwt():
    # 1. Registramos el usuario
    client.post("/usuarios/", json={
        "nombre": "Tester Login",
        "email": "login@tfg.com",
        "rol": "superadmin",
        "empresa_id": None,
        "password": "ClaveCorrecta2026"
    })

    # 2. Hacemos login (OAuth2PasswordRequestForm usa form-data: username y password)
    response = client.post(
        "/login",
        data={"username": "login@tfg.com", "password": "ClaveCorrecta2026"}
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_credenciales_incorrectas():
    client.post("/usuarios/", json={
        "nombre": "Tester Fallo",
        "email": "fallo@tfg.com",
        "rol": "superadmin",
        "empresa_id": None,
        "password": "ClaveReal"
    })

    # Contraseña incorrecta
    res_bad_pass = client.post(
        "/login",
        data={"username": "fallo@tfg.com", "password": "ClaveEquivocada"}
    )
    assert res_bad_pass.status_code == 400
    assert res_bad_pass.json()["detail"] == "Contraseña incorrecta"

    # Usuario inexistente
    res_bad_user = client.post(
        "/login",
        data={"username": "noexiste@tfg.com", "password": "ClaveReal"}
    )
    assert res_bad_user.status_code == 400
    assert res_bad_user.json()["detail"] == "Correo incorrecto"


def test_regla_negocio_limite_licencias_b2b():
    # 1. Creamos empresa
    res_emp = client.post("/empresas/", json={"nombre": "Empresa Test S.L."})
    assert res_emp.status_code == 200
    empresa_id = res_emp.json()["id"]

    # 2. Intentar crear usuario antes de tener suscripción debe fallar
    res_sin_sub = client.post("/usuarios/", json={
        "nombre": "Empleado Sin Plan",
        "email": "sinplan@empresa.com",
        "rol": "trabajador",
        "empresa_id": empresa_id,
        "password": "123"
    })
    assert res_sin_sub.status_code == 400
    assert res_sin_sub.json()["detail"] == "La empresa no tiene una suscripción activa"

    # 3. Asignamos suscripción con límite de 1 sola licencia
    res_sub = client.post("/suscripciones/", json={
        "empresa_id": empresa_id,
        "plan": "basico",
        "limite_licencias": 1
    })
    assert res_sub.status_code == 200

    # 4. Primer usuario dentro del límite -> Debe funcionar (200)
    res_u1 = client.post("/usuarios/", json={
        "nombre": "Empleado 1",
        "email": "emp1@empresa.com",
        "rol": "trabajador",
        "empresa_id": empresa_id,
        "password": "123"
    })
    assert res_u1.status_code == 200

    # 5. Segundo usuario excediendo el límite -> Debe bloquearse (400)
    res_u2 = client.post("/usuarios/", json={
        "nombre": "Empleado 2",
        "email": "emp2@empresa.com",
        "rol": "trabajador",
        "empresa_id": empresa_id,
        "password": "123"
    })
    assert res_u2.status_code == 400
    assert "Límite de licencias alcanzado" in res_u2.json()["detail"]