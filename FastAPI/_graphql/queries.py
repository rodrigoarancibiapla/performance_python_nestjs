
from typing import List
from line_profiler import LineProfiler
from sqlalchemy import func, text
from sqlmodel import Session, select
import strawberry
from sqlalchemy.orm import joinedload
from _graphql.types import ClienteConFacturasType, ClienteType
from models.db import Cliente, Factura
import redis
import pickle
import cProfile, pstats, io
from pstats import SortKey
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def getAllClients( info: strawberry.Info):
            db: Session = info.context["db"]
            cached_clientes = redis_client.get(f"clientes")
            if cached_clientes:
                 clientes = pickle.loads(cached_clientes)
            else:
                clientes = db.exec(select(Cliente)).all()
                clientes_data = pickle.dumps(clientes)  # Serializar con Pickle
                redis_client.set(f"clientes", clientes_data)
            result = []
        
            for cliente in clientes:
                cached_facturas = redis_client.get(f"item_{cliente.id}")
          
                if cached_facturas:
                    facturas = pickle.loads(cached_facturas)
                else:
                    facturas = db.exec(
                        select(Factura).where(
                            Factura.cliente_id == cliente.id)).all()
                    facturas_data = pickle.dumps(facturas)  # Serializar con Pickle
                    redis_client.set(f"item_{cliente.id}", facturas_data)
                
                total_facturas = sum(
                    f.total for f in facturas) if facturas else 0.0
                result.append(
                    ClienteType(
                        id=cliente.id,
                        nombre=cliente.nombre,
                        email=cliente.email,
                        total_facturas=total_facturas,
                        facturas=facturas))
            
            return result
@strawberry.type
class Query:
    @strawberry.field
    def all_clientes(self, info: strawberry.Info) -> List[ClienteType]:
        return getAllClients(info)
            

    @strawberry.field
    def clientes_con_facturas_opt(
            self, info: strawberry.Info) -> List[ClienteConFacturasType]:
        db: Session = info.context["db"]

        # Realizamos una sola consulta para obtener los clientes con las
        # facturas asociadas
        query = db.exec(Cliente).options(
            joinedload(
                Cliente.facturas)) .outerjoin(Factura) .add_columns(
            Cliente.id,
            Cliente.nombre,
            Cliente.email,
            func.coalesce(
                func.sum(
                    Factura.total),
                0).label("total_facturas")) .group_by(
            Cliente.id)

        # Ejecutamos la consulta
        results = query.all()

        # Convertimos los resultados en los tipos deseados
        clientes_facturas = []
        for result in results:
            cliente = result[0]  # El primer valor es el objeto Cliente
            # El cuarto valor es total_facturas (después de los campos del
            # cliente)
            total_facturas = result[3]

            clientes_facturas.append(ClienteConFacturasType(
                id=cliente.id,
                nombre=cliente.nombre,
                email=cliente.email,
                total_facturas=total_facturas,
                facturas=cliente.facturas  # Ya puedes acceder a las facturas desde el cliente
            ))

        return clientes_facturas

    @strawberry.field
    def clientes_con_facturas(
            self,
            info: strawberry.Info) -> List[ClienteConFacturasType]:
        db: Session = info.context["db"]

        # Consulta con LEFT JOIN y GROUP BY para obtener la suma de facturas
        # por cliente
        query = text("""
            SELECT c.id, c.nombre, c.email, COALESCE(SUM(f.total), 0) as total_facturas
            FROM clientes_cliente c
            LEFT JOIN clientes_factura f ON c.id = f.cliente_id
            GROUP BY c.id
        """)
        results = db.exec(query).all()

        clientes_facturas = []
        for row in results:
            cliente_id, nombre, email, total_facturas = row
            facturas = db.exec(
                select(Factura).where(
                    Factura.cliente_id == cliente_id)).all()
            clientes_facturas.append(ClienteConFacturasType(
                id=cliente_id, nombre=nombre, email=email,
                total_facturas=total_facturas, facturas=facturas
            ))

        return clientes_facturas
