from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
from models import SesionesActivas, AuthUser
from config import settings

security = HTTPBearer()


async def requiere_autenticacion(
    request: Request,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependencia FastAPI equivalente a @AutenticacionToken de DRF.
    Valida doble token (JWT + sesión clásica) en cada petición.
    """
    
    try:
        # ========== 1. EXTRAER X-SESSION-USER ==========
        x_session_user = request.headers.get("X-SESSION-USER")
        
        if not x_session_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token clásico requerido (X-SESSION-USER)"
            )
        
        # ========== 2. VALIDAR TOKEN CLÁSICO EN BD ==========
        data_sesion = db.query(SesionesActivas).filter(
            SesionesActivas.TokenSesion == x_session_user,
            SesionesActivas.ConexionActiva == True
        ).first()
        
        if not data_sesion:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o sesión cerrada"
            )
        
        # ========== 3. EXTRAER JWT ==========
        auth_header = credentials.credentials
        
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token JWT requerido"
            )
        
        # ========== 4. DECODIFICAR JWT (con firma) ==========
        try:
            decoded_token = jwt.decode(
                auth_header,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id_jwt = decoded_token.get("user_id")
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"JWT inválido: {str(e)}"
            )
        
        # ========== 5. CROSS-CHECK USER ID ==========
        if str(user_id_jwt) != str(data_sesion.IdDjangoUser):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID no coincide entre tokens"
            )
        
        # ========== 6. VERIFICAR EXPIRACIÓN ==========
        # ✅ CORREGIDO: usar timezone-aware datetime
        ahora = datetime.now(timezone.utc)
        
        # Si FechaExpiracion es naive, convertirla a aware
        fecha_exp = data_sesion.FechaExpiracion
        if fecha_exp.tzinfo is None:
            fecha_exp = fecha_exp.replace(tzinfo=timezone.utc)
        
        if ahora > fecha_exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Su sesión ha expirado"
            )
        
        # ========== 7. VERIFICAR SI ES SUPERUSUARIO ==========
        auth_user = db.query(AuthUser).filter(
            AuthUser.id == data_sesion.IdDjangoUser
        ).first()
        
        is_superuser = auth_user.is_superuser if auth_user else False
        is_staff = auth_user.is_staff if auth_user else False
        
        # ========== 8. INYECTAR INFO AL REQUEST ==========
        request.state.user_info = {
            "usuario_id": data_sesion.UsuarioId,
            "id_django_user": data_sesion.IdDjangoUser,
            "username": auth_user.username if auth_user else None,
            "is_superuser": is_superuser,
            "is_staff": is_staff,
            "token_sesion": x_session_user,
            "jwt_payload": decoded_token
        }
        
        return request.state.user_info
        
    except HTTPException:
        # Re-lanzar excepciones HTTP (401, 403) tal cual
        raise
        
    except Exception as e:
        # ✅ CAPTURAR CUALQUIER OTRO ERROR INESPERADO
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno de autenticación: {str(e)}"
        )


async def requiere_superusuario(
    request: Request,
    user_info: dict = Depends(requiere_autenticacion)
):
    """
    Dependencia adicional: solo permite superusuarios.
    """
    try:
        if not user_info.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requiere privilegios de superusuario"
            )
        return user_info
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando permisos: {str(e)}"
        )