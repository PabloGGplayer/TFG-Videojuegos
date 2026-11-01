from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Empresa(Base):
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    
    usuarios = relationship("Usuario", back_populates="empresa")
    suscripcion = relationship("Suscripcion", back_populates="empresa", uselist=False)

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rol = Column(String) # 'superadmin', 'admin_empresa', 'trabajador'
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)

    empresa = relationship("Empresa", back_populates="usuarios")

class Suscripcion(Base):
    __tablename__ = "suscripciones"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), unique=True)
    plan = Column(String) # 'basico', 'premium'
    limite_licencias = Column(Integer, default=10)
    
    empresa = relationship("Empresa", back_populates="suscripcion")

class Juego(Base):
    __tablename__ = "juegos"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    precio_suscripcion = Column(Float)