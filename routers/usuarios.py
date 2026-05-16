from fastapi import APIRouter, Depends,HTTPException  
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Usuarios
from schemas import UsuariosResponse
from auth import requiere_autenticacion,requiere_superusuario
router = APIRouter(prefix="/fast/usuarios", tags=["usuarios"])

@router.get("/", response_model=List[UsuariosResponse])
async def listar_usuarios(db: Session = Depends(get_db),
                          user_info: dict = Depends(requiere_autenticacion)
                          ):
    """
    Lista todas las empresas registradas.
    Solo lectura, no requiere autenticación (o sí, según prefieras).
    """
    usuarios = db.query(Usuarios).order_by(Usuarios.Id).all()
    return usuarios
