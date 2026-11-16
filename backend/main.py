from typing import List
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
    
    # 2. Lógica de negocio B2B: Validar empresa, suscripción activa y límite de licencias
    if usuario.empresa_id is not None:
        empresa = db.query(models.Empresa).filter(models.Empresa.id == usuario.empresa_id).first()
        if not empresa:
            raise HTTPException(status_code=404, detail="La empresa especificada no existe")
        
        suscripcion = db.query(models.Suscripcion).filter(models.Suscripcion.empresa_id == usuario.empresa_id).first()
        if not suscripcion:
            raise HTTPException(status_code=400, detail="La empresa no tiene una suscripción activa")
        
        usuarios_actuales = db.query(models.Usuario).filter(models.Usuario.empresa_id == usuario.empresa_id).count()
        if usuarios_actuales >= suscripcion.limite_licencias:
            raise HTTPException(
                status_code=400,
                detail=f"Límite de licencias alcanzado ({suscripcion.limite_licencias} máximo para el plan {suscripcion.plan})"
            )

    # 3. Encriptamos la contraseña y guardamos el usuario
    contrasena_encriptada = get_password_hash(usuario.password)
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
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    if not db_usuario:
        raise HTTPException(status_code=400, detail="Correo incorrecto")

    if not verify_password(form_data.password, db_usuario.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    access_token = create_access_token(
        data={
            "sub": db_usuario.email,
            "rol": db_usuario.rol,
            "empresa_id": db_usuario.empresa_id
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/empresas/", response_model=schemas.Empresa)
def crear_empresa(empresa: schemas.EmpresaCreate, db: Session = Depends(get_db)):
    db_empresa = db.query(models.Empresa).filter(models.Empresa.nombre == empresa.nombre).first()
    if db_empresa:
        raise HTTPException(status_code=400, detail="La empresa ya está registrada")
    
    nueva_empresa = models.Empresa(nombre=empresa.nombre)
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return nueva_empresa

@app.get("/empresas/", response_model=List[schemas.Empresa])
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(models.Empresa).all()

@app.get("/empresas/{empresa_id}/usuarios", response_model=List[schemas.Usuario])
def listar_usuarios_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return db.query(models.Usuario).filter(models.Usuario.empresa_id == empresa_id).all()

@app.post("/suscripciones/", response_model=schemas.Suscripcion)
def crear_o_actualizar_suscripcion(suscripcion: schemas.SuscripcionCreate, db: Session = Depends(get_db)):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == suscripcion.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    db_suscripcion = db.query(models.Suscripcion).filter(models.Suscripcion.empresa_id == suscripcion.empresa_id).first()
    if db_suscripcion:
        db_suscripcion.plan = suscripcion.plan
        db_suscripcion.limite_licencias = suscripcion.limite_licencias
        db.commit()
        db.refresh(db_suscripcion)
        return db_suscripcion

    nueva_suscripcion = models.Suscripcion(
        empresa_id=suscripcion.empresa_id,
        plan=suscripcion.plan,
        limite_licencias=suscripcion.limite_licencias
    )
    db.add(nueva_suscripcion)
    db.commit()
    db.refresh(nueva_suscripcion)
    return nueva_suscripcion

@app.post("/juegos/", response_model=schemas.Juego)
def crear_juego(juego: schemas.JuegoCreate, db: Session = Depends(get_db)):
    db_juego = models.Juego(
        titulo=juego.titulo,
        descripcion=juego.descripcion,
        precio_suscripcion=juego.precio_suscripcion
    )
    db.add(db_juego)
    db.commit()
    db.refresh(db_juego)
    return db_juego

@app.get("/juegos/", response_model=List[schemas.Juego])
def listar_juegos(db: Session = Depends(get_db)):
    return db.query(models.Juego).all()