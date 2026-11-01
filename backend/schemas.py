from pydantic import BaseModel, ConfigDict, EmailStr

#EMPRESAS
class EmpresaBase(BaseModel):
    nombre: str

class EmpresaCreate(EmpresaBase):
    pass

class Empresa(EmpresaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#USUARIOS
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: str
    empresa_id: int | None = None

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#SUSCRIPCIONES 
class SuscripcionBase(BaseModel):
    plan: str
    limite_licencias: int

class SuscripcionCreate(SuscripcionBase):
    empresa_id: int

class Suscripcion(SuscripcionBase):
    id: int
    empresa_id: int
    model_config = ConfigDict(from_attributes=True)

#JUEGOS 
class JuegoBase(BaseModel):
    titulo: str
    descripcion: str | None = None
    precio_suscripcion: float

class JuegoCreate(JuegoBase):
    pass

class Juego(JuegoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)