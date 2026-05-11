from fastapi import APIRouter,Request,Depends
from auth import requiere_autenticacion,requiere_superusuario
router=APIRouter(prefix="/api/system",tags=["system"])

@router.get("/check")
async def comprobacion_auth(
    request: Request,
    user_info: dict = Depends(requiere_autenticacion)
):
    return {
        "success": True,
        "autenticado": True,
        "usuario": {
            "id": user_info["usuario_id"],
            "username": user_info["username"],
            "is_superuser": user_info["is_superuser"],
            "is_staff": user_info["is_staff"]
        }
    }
