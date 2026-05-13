from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import SessionLocal
from models import SesionesActivas,Usuarios
import json
import asyncio
from datetime import datetime, timezone

class ConnectionManager:
    """Gestiona conexiones WebSocket activas"""
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Envía datos a TODOS los clientes conectados"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Limpiar conexiones rotas
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()


async def get_usuarios_activos() -> list[dict]:
    """Consulta SesionesActivas y devuelve usuarios logueados"""
    db = SessionLocal()
    try:
        ahora = datetime.now(timezone.utc)
        
        sesiones = db.query(
            SesionesActivas, 
            Usuarios.UserName
        ).join(
            Usuarios, 
            SesionesActivas.UsuarioId == Usuarios.Id
        ).filter(
            SesionesActivas.ConexionActiva == True,
            SesionesActivas.FechaExpiracion > ahora
        ).all()
        
        usuarios = []
        for sesion_obj, username in sesiones:
            usuarios.append({
                "id": sesion_obj.Id,
                "usuario_id": sesion_obj.UsuarioId,
                "django_user_id": sesion_obj.IdDjangoUser,
                "dispositivo": sesion_obj.Dispositivo,
                "ip": sesion_obj.IpConexion,
                "username": username,
                "conectado_desde": sesion_obj.FechaConexion.isoformat() if sesion_obj.FechaConexion else None,
                "expira": sesion_obj.FechaExpiracion.isoformat() if sesion_obj.FechaExpiracion else None,
            })
        print(usuarios)
        return usuarios
        
    finally:
        db.close()


async def notificar_cambio():
    """Envía lista actualizada a todos los clientes"""
    usuarios = await get_usuarios_activos()
    await manager.broadcast({
        "tipo": "usuarios_activos",
        "cantidad": len(usuarios),
        "usuarios": usuarios,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# WebSocket endpoint
async def websocket_usuarios(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Enviar lista inicial
    usuarios = await get_usuarios_activos()
    await websocket.send_json({
        "tipo": "usuarios_activos",
        "cantidad": len(usuarios),
        "usuarios": usuarios
    })
    
    try:
        while True:
            # Escuchar mensajes del cliente (ping, filtros, etc)
            data = await websocket.receive_text()
            
            # Responder con datos actualizados si el cliente pide refresh
            if data == "refresh":
                usuarios = await get_usuarios_activos()
                await websocket.send_json({
                    "tipo": "usuarios_activos",
                    "cantidad": len(usuarios),
                    "usuarios": usuarios
                })
            
            # Heartbeat cada 30 segundos (opcional, el cliente puede enviar "ping")
            elif data == "ping":
                await websocket.send_json({"tipo": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)