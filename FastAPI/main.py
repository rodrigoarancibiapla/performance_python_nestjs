from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, Session, create_engine
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware
from _graphql.mutations import Mutation
from _graphql.queries import Query

database_url = "mysql+pymysql://myuser:mypassword@127.0.0.1:3306/mydatabase"
engine = create_engine(database_url, echo=True)


def get_db():
    with Session(engine) as session:  # Deshabilitar el cache
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecutará al iniciar la aplicación (equivalente a
    # 'startup')
    SQLModel.metadata.create_all(engine)
    yield  # Este punto es cuando la app está en funcionamiento
    # Código que se ejecutará al cerrar la aplicación (equivalente a
    # 'shutdown')
    print("App is shutting down...")

# Crea la app con el manejador de eventos 'lifespan'
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)

# Middleware para inyectar la sesión de la BD en el contexto


async def get_context():
    with Session(engine, expire_on_commit=False) as session:  # Deshabilitar el cache
        yield {"db": session}

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphql_ide=True)

app.include_router(graphql_app, prefix="/graphql")
