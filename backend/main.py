from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import verify_password, create_access_token
import models
import schemas
from database import engine, get_db

# Crea las tablas en la base de datos si aún no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola mundo!"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO: Más adelante conectaremos esto con la Base de Datos real
    # Por ahora simulamos un usuario de prueba para validar que el JWT funciona
    usuario_prueba = {
        "email": "admin@empresa.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # Contraseña: "password123" encriptada
        "rol": "admin_empresa",
        "empresa_id": 1
    }

    # 1. Verificamos que el email existe (simulado)
    if form_data.username != usuario_prueba["email"]:
        raise HTTPException(status_code=400, detail="Correo incorrecto")

    # 2. Verificamos que la contraseña coincide
    if not verify_password(form_data.password, usuario_prueba["hashed_password"]):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    # 3. Si todo es correcto, generamos el Token JWT
    access_token = create_access_token(
        data={
            "sub": usuario_prueba["email"],
            "rol": usuario_prueba["rol"],
            "empresa_id": usuario_prueba["empresa_id"]
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/juegos/", response_model=schemas.Juego)
def crear_juego(juego: schemas.JuegoCreate, db: Session = Depends(get_db)):
    # Crear instancia del modelo de SQLAlchemy con los datos validados por Pydantic
    db_juego = models.Juego(
        titulo=juego.titulo,
        descripcion=juego.descripcion,
        precio_suscripcion=juego.precio_suscripcion
    )
    
    db.add(db_juego)
    db.commit()
    db.refresh(db_juego)
    
    return db_juego