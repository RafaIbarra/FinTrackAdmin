from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import Optional
from config import settings

class EmpresaResponse(BaseModel):
    Id: int
    NombreEmpresa: Optional[str] = None
    Ruc: Optional[str] = None
    UrlImg: Optional[str] = None
    FechaRegistro: Optional[datetime] = None
    
    @computed_field
    @property
    def UrlImgCompleta(self) -> Optional[str]:
        if self.UrlImg:
            return f"{settings.DRF_BASE_URL}/Media/{self.UrlImg}"
        return None

    @computed_field
    @property
    def FechaRegistroFormateada(self) -> Optional[str]:
        if self.FechaRegistro:
            # Formato: dd/mm/aaaa hh:mm:ss
            return self.FechaRegistro.strftime("%d/%m/%Y %H:%M:%S")
        return None

    class Config:
        from_attributes = True  # Permite convertir objetos SQLAlchemy

class UsuariosResponse(BaseModel):
    Id: int
    NombreUsuario: Optional[str] = None
    ApellidoUsuario: Optional[str] = None
    UserName: Optional[str] = None
    Correo: Optional[str] = None
    FechaRegistro: Optional[datetime] = None
    LastLogin: Optional[datetime] = None

    class Config:
        from_attributes = True  # Permite convertir objetos SQLAlchemy
    