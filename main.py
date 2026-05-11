from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from config import settings
from routers import admin


app = FastAPI(
    title="Admin API - Finanzas Personales",
    description="API de administración con autenticación DRF compartida",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # tu React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(admin.router)
@app.get("/health")
async def health_check():
    return {"status": "ok", "servicio": "admin-fastapi"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,        # Puerto diferente a DRF (8000)
        reload=True       # Solo desarrollo
    )