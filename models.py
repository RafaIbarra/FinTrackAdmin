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


class Empresas(Base):
    __tablename__ = "Empresas"  # Mismo nombre que Django
    
    Id = Column(Integer, primary_key=True)
    NombreEmpresa= Column(String(300))
    Ruc= Column(String(50))
    UrlImg = Column(String(200))
    FechaRegistro = Column(DateTime, index=True)
    
class MovimientosGastos(Base):
    __tablename__ = "MovimientosGastos"  # Mismo nombre que Django
    
    Id = Column(Integer, primary_key=True)
    EmpresaId =Column(Integer, ForeignKey("Empresas.Id"))

class MovimientosIngresos(Base):
    __tablename__ = "MovimientosIngresos"  # Mismo nombre que Django
    
    Id = Column(Integer, primary_key=True)
    EmpresaId =Column(Integer, ForeignKey("Empresas.Id"))
    
    


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
    NombreUsuario=Column(String(100))
    ApellidoUsuario=Column(String(100))
    UserName = Column(String(100))
    Correo=Column(String(100))
    FechaRegistro=Column(DateTime, index=True)
    LastLogin=Column(DateTime, index=True)
    # Agrega otros campos si los necesitas