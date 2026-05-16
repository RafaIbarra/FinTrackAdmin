from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from config import settings
from routers import admin,empresas,usuarios
from ws_manager import websocket_usuarios, notificar_cambio, manager
from ws_empresas import websocket_empresas, notificar_cambio_empresas, empresas_manager
import asyncio


app = FastAPI(
    title="Admin API - Finanzas Personales",
    description="API de administración con autenticación DRF compartida",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",'http://localhost:5173'],  # tu React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(admin.router)
app.include_router(empresas.router)
app.include_router(usuarios.router)
@app.get("/health")
async def health_check():
    return {"status": "ok", "servicio": "admin-fastapi"}


@app.websocket("/ws/usuarios")
async def ws_usuarios(websocket: WebSocket):
    await websocket_usuarios(websocket)



# Opcional: Endpoint HTTP para forzar broadcast (útil para testing)
@app.post("/api/admin/notificar-usuarios")
async def trigger_notificacion():
    """Fuerza envío de actualización a todos los WebSocket conectados"""
    await notificar_cambio()
    return {"enviado": True, "clientes_conectados": len(manager.active_connections)}



@app.websocket("/ws/empresas")
async def ws_empresas(websocket: WebSocket):
    await websocket_empresas(websocket)

@app.post("/api/admin/notificar-empresas")
async def trigger_notificacion_empresas():
    """Fuerza envío de actualización de empresas a todos los WebSocket conectados"""
    await notificar_cambio_empresas()
    return {
        "enviado": True, 
        "clientes_conectados": len(empresas_manager.active_connections)
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,        # Puerto diferente a DRF (8000)
        reload=True       # Solo desarrollo
    )