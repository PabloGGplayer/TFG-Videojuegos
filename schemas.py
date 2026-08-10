from pydantic import BaseModel

class JuegoCreate(BaseModel):
    titulo: str
    descripcion: str | None = None
    precio_suscripcion: float
    
class Juego(JuegoCreate):
    id: int

    class Config:
        from_attributes = True