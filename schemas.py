from pydantic import BaseModel
from typing import List

class TarjetaBase(BaseModel):
    banco: str
    tarjeta: str
    monto_total: float
    pago_minimo: float

class TarjetaCreate(TarjetaBase):
    pass

class TarjetaUpdate(TarjetaBase):
    pagos: List[float] = []

class TarjetaOut(TarjetaBase):
    id: int
    pagos: List[float]

    class Config:
        from_attributes = True

class PagoInput(BaseModel):
    pago: float
