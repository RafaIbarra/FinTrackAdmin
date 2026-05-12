from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus
from decouple import Config, RepositoryEnv

class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent
    env_path = BASE_DIR.parent / 'BackendConfig' / '.env'
    
    try:
        config = Config(RepositoryEnv(str(env_path)))
    except Exception as e:
        raise RuntimeError(f"No se pudo cargar .env desde {env_path}: {e}")
    
    # === JWT ===
    SECRET_KEY: str = config('SECRET_KEY')
    ALGORITHM: str = config('ALGORITHM')
    
    # === Base de datos (datos separados) ===
    DB_USER: str = config('DB_USER')
    DB_PASS: str = config('DB_PASS')
    DB_HOST: str = config('DB_HOST')
    DB_NAME: str = config('DB_NAME')
    DB_PORT: str = config('DB_PORT', default='5432')
    DRF_BASE_URL: str = config('DRF_BASE_URL', default='http://127.0.0.1:8000')
    # Armar URL correcta con contraseña codificada
    DATABASE_URL: str = (
        f"postgresql://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    @classmethod
    def validate(cls):
        missing = []
        if not cls.SECRET_KEY: missing.append("SECRET_KEY")
        if not cls.ALGORITHM: missing.append("ALGORITHM")
        if not cls.DB_USER: missing.append("DB_USER")
        if not cls.DB_PASS: missing.append("DB_PASS")
        if not cls.DB_HOST: missing.append("DB_HOST")
        if not cls.DB_NAME: missing.append("DB_NAME")
        
        if missing:
            raise ValueError(f"Faltan en .env: {', '.join(missing)}")
        
        # Log seguro (oculta contraseña)
        safe = cls.DATABASE_URL.replace(quote_plus(cls.DB_PASS), '***')
        

@lru_cache()
def get_settings():
    s = Settings()
    s.validate()
    return s

settings = get_settings()