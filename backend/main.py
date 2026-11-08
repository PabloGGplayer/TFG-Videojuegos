from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import verify_password, create_access_token, get_password_hash
import models
import schemas
from database import engine, get_db

# Crea las tablas en la base de datos si aún no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola mundo!"}

@app.post("/usuarios/", response_model=schemas.Usuario)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Comprobamos si el email ya existe en la base de datos
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # 2. Encriptamos la contraseña
    contrasena_encriptada = get_password_hash(usuario.password)
    
    # 3. Creamos el usuario real y lo guardamos
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        hashed_password=contrasena_encriptada,
        rol=usuario.rol,
        empresa_id=usuario.empresa_id
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Buscamos el usuario en la BD por su email
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    
    if not db_usuario:
        raise HTTPException(status_code=400, detail="Correo incorrecto")

    # 2. Verificamos que la contraseña introducida coincide con la guardada en BD
    if not verify_password(form_data.password, db_usuario.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    # 3. Si todo es correcto, generamos el Token JWT real
    access_token = create_access_token(
        data={
            "sub": db_usuario.email,
            "rol": db_usuario.rol,
            "empresa_id": db_usuario.empresa_id
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
@app.post("/empresas/", response_model=schemas.Empresa)
def crear_empresa(empresa: schemas.EmpresaCreate, db: Session = Depends(get_db)):
    db_empresa = db.query(models.Empresa).filter(models.Empresa.nombre == empresa.nombre).first()
    if db_empresa:
        raise HTTPException(status_code=400, detail="La empresa ya está registrada")
    
    nueva_empresa = models.Empresa(
        nombre=empresa.nombre
    )
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return nueva_empresa