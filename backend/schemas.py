from pydantic import BaseModel, ConfigDict

class JuegoCreate(BaseModel):
    titulo: str
    descripcion: str | None = None
    precio_suscripcion: float
    
class Juego(JuegoCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)