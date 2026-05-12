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

    class Config:
        from_attributes = True  # Permite convertir objetos SQLAlchemy