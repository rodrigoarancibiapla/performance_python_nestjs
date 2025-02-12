
from decimal import Decimal
from typing import List
import strawberry


@strawberry.type
class FacturaType:
    id: int
    total: Decimal
    fecha: str


@strawberry.type
class ClienteType:
    id: int
    nombre: str
    email: str
    total_facturas: Decimal
    facturas: List[FacturaType]


@strawberry.type
class ClienteConFacturasType:
    id: int
    nombre: str
    email: str
    total_facturas: Decimal
    facturas: List[FacturaType]
