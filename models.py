from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class SesionesActivas(Base):
    __tablename__ = "SesionesActivas"  # Mismo nombre que Django
    
    Id = Column(Integer, primary_key=True)
    FechaConexion = Column(DateTime)
    Dispositivo = Column(String(200))
    IpConexion = Column(String(200))
    UsuarioId = Column(Integer, ForeignKey("Usuarios.Id"))  # db_column de Django
    IdDjangoUser = Column(Integer)
    TokenSesion = Column(String(300), unique=True, index=True)
    FechaExpiracion = Column(DateTime, index=True)
    ConexionActiva = Column(Boolean, default=True)
    
    # Relación opcional (si quieres acceder a datos del usuario)
    # usuario = relationship("Usuarios", back_populates="sesiones")

class AuthUser(Base):
    """Tabla auth_user de Django - solo campos que necesitamos"""
    __tablename__ = "auth_user"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True)
    is_superuser = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

# Si necesitas la tabla Usuarios para el username:
class Usuarios(Base):
    __tablename__ = "Usuarios"
    
    Id = Column(Integer, primary_key=True)
    UserName = Column(String(100))
    # Agrega otros campos si los necesitas