from fastapi import APIRouter, Depends,HTTPException  
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Empresas
from schemas import EmpresaResponse
from auth import requiere_autenticacion,requiere_superusuario

router = APIRouter(prefix="/fast/empresas", tags=["empresas"])

@router.get("/", response_model=List[EmpresaResponse])
async def listar_empresas(db: Session = Depends(get_db),
                          user_info: dict = Depends(requiere_autenticacion)
                          ):
    """
    Lista todas las empresas registradas.
    Solo lectura, no requiere autenticación (o sí, según prefieras).
    """
    empresas = db.query(Empresas).order_by(Empresas.NombreEmpresa).all()
    return empresas


@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def obtener_empresa(empresa_id: int, db: Session = Depends(get_db), 
                          user_info: dict = Depends(requiere_autenticacion)):
    """
    Obtiene una empresa por su ID.
    """
    empresa = db.query(Empresas).filter(Empresas.Id == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=404,
            detail=f"Empresa con ID {empresa_id} no encontrada"
        )
    
    return empresa