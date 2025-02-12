from decimal import Decimal
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class Cliente(SQLModel, table=True):
    __tablename__ = "clientes_cliente"
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str
    facturas: List["Factura"] = Relationship(
        back_populates="cliente")  # Relación con Factura


class Factura(SQLModel, table=True):
    __tablename__ = "clientes_factura"
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="clientes_cliente.id")
    total: Decimal
    fecha: str
    cliente: Cliente = Relationship(
        back_populates="facturas")  # Relación con Cliente
