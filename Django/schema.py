import graphene
from graphene_django.types import DjangoObjectType
from clientes.models import Cliente, Factura
from decimal import Decimal
from django.db.models import Sum
from django.db import connection
from django.core.cache import cache


# Tipo de entrada para el cliente
class ClienteInput(graphene.InputObjectType):
    nombre = graphene.String(required=True)
    email = graphene.String(required=True)

# Tipo de entrada para la factura
class FacturaInput(graphene.InputObjectType):
    
    cliente_id = graphene.Int(required=True)
    total = graphene.String(required=True)  # Se usa String para convertirlo después a Decimal

# Tipo de DjangoObjectType para la Factura
class FacturaType(DjangoObjectType):
    id = graphene.Int() 
    class Meta:
        model = Factura
        fields = ("id", "total", "fecha")
    def resolve_id(self, info):
        return self.id  # Garantiza que se devuelva como entero

# Tipo de DjangoObjectType para el Cliente
class ClienteType(DjangoObjectType):
    id = graphene.Int()
    total_facturas = graphene.Float()
    facturas = graphene.List(FacturaType)

    class Meta:
        model = Cliente
        fields = ("id", "nombre", "email")

    def resolve_total_facturas(self, info):
        return self.factura_set.aggregate(Sum("total"))["total__sum"] or 0.0
    
    def resolve_id(self, info):
        return self.id  # Garantiza que se devuelva como entero

    def resolve_facturas(self, info):
        return self.factura_set.all()

# Definir la mutación para crear un cliente
class CrearCliente(graphene.Mutation):
    class Arguments:
        cliente_data = ClienteInput(required=True)

    cliente = graphene.Field(lambda: ClienteType)

    def mutate(self, info, cliente_data):
        cliente = Cliente.objects.create(
            nombre=cliente_data.nombre,
            email=cliente_data.email
        )
        return CrearCliente(cliente=cliente)

# Definir la mutación para crear una factura
class CrearFactura(graphene.Mutation):
    class Arguments:
        factura_data = FacturaInput(required=True)

    factura = graphene.Field(lambda: FacturaType)

    def mutate(self, info, factura_data):
        cliente = Cliente.objects.get(id=factura_data.cliente_id)
        total = Decimal(factura_data.total)  # Convertir el string a Decimal
        factura = Factura.objects.create(
            cliente=cliente,
            total=total
        )
        return CrearFactura(factura=factura)

class ClienteConFacturas(graphene.ObjectType):
    id = graphene.Int()
    nombre = graphene.String()
    email = graphene.String()
    total_facturas = graphene.Float()
    facturas = graphene.List(FacturaType)

# Definir la consulta principal
class Query(graphene.ObjectType):
    all_clientes = graphene.List(ClienteType)
    all_facturas = graphene.List(FacturaType)
    total_facturas = graphene.Float()

    def resolve_all_clientes(self, info):
        
        cache_key = "all_clientes"
        clientes = cache.get(cache_key)

        if not clientes:
           
            clientes = list(Cliente.objects.prefetch_related("factura_set").all())
            cache.set(cache_key, clientes, timeout=60 * 15)  # Caché de 15 minutos
        

        return clientes

    clientes_con_facturas = graphene.List(ClienteConFacturas)

    def resolve_clientes_con_facturas(self, info):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, c.nombre, c.email, COALESCE(SUM(f.total), 0) as total_facturas
                FROM clientes_cliente c
                LEFT JOIN clientes_factura f ON c.id = f.cliente_id
                GROUP BY c.id
            """)

            columnas = [col[0] for col in cursor.description]
            resultados = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        
        return [ClienteConFacturas(**cliente, facturas=Factura.objects.filter(cliente_id=cliente["id"])) for cliente in resultados]

# Mejorado con select_related y prefetch_related:
  
    def resolve_total_facturas(self, info):
        return Factura.objects.aggregate(Sum("total"))["total__sum"] or 0.0

# Definir el esquema de mutaciones
class Mutation(graphene.ObjectType):
    crear_cliente = CrearCliente.Field()
    crear_factura = CrearFactura.Field()

# Crear el esquema
schema = graphene.Schema(query=Query, mutation=Mutation)
