from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.post("/tarjetas/", response_model=schemas.TarjetaOut)
def crear_tarjeta(tarjeta: schemas.TarjetaCreate, db: Session = Depends(get_db)):
    db_tarjeta = models.Tarjeta(**tarjeta.dict(), pagos=[])
    db.add(db_tarjeta)
    db.commit()
    db.refresh(db_tarjeta)
    return db_tarjeta

@app.get("/tarjetas/", response_model=List[schemas.TarjetaOut])
def listar_tarjetas(db: Session = Depends(get_db)):
    return db.query(models.Tarjeta).all()

@app.put("/tarjetas/{tarjeta_id}", response_model=schemas.TarjetaOut)
def actualizar_tarjeta(tarjeta_id: int, tarjeta: schemas.TarjetaUpdate, db: Session = Depends(get_db)):
    db_tarjeta = db.query(models.Tarjeta).filter(models.Tarjeta.id == tarjeta_id).first()
    if not db_tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    for key, value in tarjeta.dict().items():
        setattr(db_tarjeta, key, value)
    db.commit()
    db.refresh(db_tarjeta)
    return db_tarjeta

@app.post("/tarjetas/{tarjeta_id}/pagos", response_model=schemas.TarjetaOut)
def agregar_pago(tarjeta_id: int, pago_input: schemas.PagoInput, db: Session = Depends(get_db)):
    db_tarjeta = db.query(models.Tarjeta).filter(models.Tarjeta.id == tarjeta_id).first()
    if not db_tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

    # ✅ Asegura que pagos sea una lista
    if not isinstance(db_tarjeta.pagos, list):
        db_tarjeta.pagos = []

    db_tarjeta.pagos = db_tarjeta.pagos + [pago_input.pago]  # Reemplaza la lista entera
    db.add(db_tarjeta)  # 🔥 Vuelve a añadir la tarjeta a la sesión
    db.commit()
    db.refresh(db_tarjeta)

    return db_tarjeta

@app.delete("/tarjetas/{tarjeta_id}")
def borrar_tarjeta(tarjeta_id: int, db: Session = Depends(get_db)):
    db_tarjeta = db.query(models.Tarjeta).filter(models.Tarjeta.id == tarjeta_id).first()
    if not db_tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    db.delete(db_tarjeta)
    db.commit()
    return {"ok": True}

@app.delete("/tarjetas/{tarjeta_id}/pagos/{pago_index}", response_model=schemas.TarjetaOut)
def eliminar_pago(tarjeta_id: int, pago_index: int, db: Session = Depends(get_db)):
    db_tarjeta = db.query(models.Tarjeta).filter(models.Tarjeta.id == tarjeta_id).first()
    if not db_tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    if pago_index < 0 or pago_index >= len(db_tarjeta.pagos):
        raise HTTPException(status_code=400, detail="Índice de pago no válido")

    # ✅ Creamos una nueva lista SIN el pago eliminado
    pagos_actualizados = db_tarjeta.pagos[:pago_index] + db_tarjeta.pagos[pago_index + 1:]
    db_tarjeta.pagos = pagos_actualizados  # ⚡ Nueva lista asignada

    db.add(db_tarjeta)  # Aseguramos que SQLAlchemy detecte el cambio
    db.commit()
    db.refresh(db_tarjeta)

    return db_tarjeta

