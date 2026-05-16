from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from database import SessionLocal
from models import Empresas, MovimientosGastos, MovimientosIngresos
from datetime import datetime, timezone

class EmpresasConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

empresas_manager = EmpresasConnectionManager()

async def get_empresas_con_movimientos() -> list[dict]:
    db = SessionLocal()
    try:
        ingresos_count = (
            db.query(
                MovimientosIngresos.EmpresaId.label("empresa_id"),
                func.count(MovimientosIngresos.Id).label("total_ingresos")
            )
            .group_by(MovimientosIngresos.EmpresaId)
            .subquery()
        )
        
        gastos_count = (
            db.query(
                MovimientosGastos.EmpresaId.label("empresa_id"),
                func.count(MovimientosGastos.Id).label("total_gastos")
            )
            .group_by(MovimientosGastos.EmpresaId)
            .subquery()
        )
        
        resultados = (
            db.query(
                Empresas,
                func.coalesce(ingresos_count.c.total_ingresos, 0).label("total_ingresos"),
                func.coalesce(gastos_count.c.total_gastos, 0).label("total_gastos"),
            )
            .outerjoin(ingresos_count, Empresas.Id == ingresos_count.c.empresa_id)
            .outerjoin(gastos_count, Empresas.Id == gastos_count.c.empresa_id)
            .filter(
                or_(
                    ingresos_count.c.total_ingresos > 0,
                    gastos_count.c.total_gastos > 0
                )
            )
            .order_by(Empresas.NombreEmpresa)
            .all()
        )
        
        empresas = []
        for empresa, total_ingresos, total_gastos in resultados:
            empresas.append({
                "id": empresa.Id,
                "nombre": empresa.NombreEmpresa,
                "ruc": empresa.Ruc,
                "url_img": empresa.UrlImg,
                "fecha_registro": empresa.FechaRegistro.isoformat() if empresa.FechaRegistro else None,
                "total_ingresos": int(total_ingresos),
                "total_gastos": int(total_gastos),
                "total_movimientos": int(total_ingresos) + int(total_gastos),
            })
        
        return empresas
    finally:
        db.close()

async def notificar_cambio_empresas():
    empresas = await get_empresas_con_movimientos()
    await empresas_manager.broadcast({
        "tipo": "empresas_activas",
        "cantidad": len(empresas),
        "empresas": empresas,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

async def websocket_empresas(websocket: WebSocket):
    await empresas_manager.connect(websocket)
    
    empresas = await get_empresas_con_movimientos()
    await websocket.send_json({
        "tipo": "empresas_activas",
        "cantidad": len(empresas),
        "empresas": empresas
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "refresh":
                empresas = await get_empresas_con_movimientos()
                await websocket.send_json({
                    "tipo": "empresas_activas",
                    "cantidad": len(empresas),
                    "empresas": empresas
                })
            
            elif data == "ping":
                await websocket.send_json({"tipo": "pong"})
                
    except WebSocketDisconnect:
        empresas_manager.disconnect(websocket)