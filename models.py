from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JuegoModel(Base):
    __tablename__ = "juegos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True, nullable=False)
    descripcion = Column(String)
    precio_suscripcion = Column(Float, nullable=False)