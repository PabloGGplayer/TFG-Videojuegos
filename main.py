from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

# Crea las tablas en la base de datos si aún no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola mundo!"}

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