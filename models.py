from sqlalchemy import Column, Integer, String, Float, JSON
from database import Base

class Tarjeta(Base):
    __tablename__ = "tarjetas"

    id = Column(Integer, primary_key=True, index=True)
    banco = Column(String, index=True)
    tarjeta = Column(String, index=True)
    monto_total = Column(Float)      # ✅ Usar Float
    pago_minimo = Column(Float)      # ✅ Usar Float
    pagos = Column(JSON, default=[]) # ✅ Almacenar lista de pagos decimales
