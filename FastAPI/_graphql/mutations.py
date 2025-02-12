
from decimal import Decimal
from fastapi import HTTPException
from sqlmodel import Session
from _graphql.types import ClienteType, FacturaType
from models.db import Cliente, Factura
import strawberry


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_cliente(
            self,
            nombre: str,
            email: str,
            info: strawberry.Info) -> ClienteType:
        db: Session = info.context["db"]
        db_cliente = Cliente(nombre=nombre, email=email)
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return ClienteType(
            id=db_cliente.id,
            nombre=db_cliente.nombre,
            email=db_cliente.email,
            total_facturas=0.0,
            facturas=[])

    @strawberry.mutation
    def create_factura(
            self,
            cliente_id: int,
            total: Decimal,
            fecha: str,
            info: strawberry.Info) -> FacturaType:
        db: Session = info.context["db"]
        cliente = db.get(Cliente, cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=404,
                detail="Cliente no encontrado")

        db_factura = Factura(cliente_id=cliente_id, total=total, fecha=fecha)
        db.add(db_factura)
        db.commit()
        db.refresh(db_factura)
        return FacturaType(
            id=db_factura.id,
            total=db_factura.total,
            fecha=db_factura.fecha)
