from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

# 1. Configuración de seguridad (Variables de entorno en producción)
SECRET_KEY = "tu_clave_secreta_super_segura_para_el_tfg"  # ¡En el TFG real pon algo complejo!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # El token caducará a las 2 horas

# 2. Configuración de encriptación (passlib con bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. Funciones de ayuda
def verify_password(plain_password, hashed_password):
    """Comprueba si la contraseña introducida coincide con la encriptada de la BD"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Encripta una contraseña en texto plano"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Genera un nuevo token JWT con los datos del usuario"""
    to_encode = data.copy()
    
    # Calculamos cuándo caduca
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    
    # Firmamos el token con nuestra clave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
