from fastapi import FastAPI
from elastic_transport import ConnectionError as ElasticConnectionError
from elastic_transport import ConnectionTimeout
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager

from app.api.routes.documents import router as documents_router
from app.core.exceptions import elastic_connection_error_handler
from app.core.exceptions import database_error_handler
from app.db.session import async_engine
from app.search.client import es_async


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await es_async.close()
    await async_engine.dispose()
    
    
app = FastAPI(lifespan=lifespan)

app.include_router(documents_router)

app.add_exception_handler(
    ElasticConnectionError,
    elastic_connection_error_handler
)
app.add_exception_handler(
    OperationalError,
    database_error_handler
)
app.add_exception_handler(
    ConnectionTimeout,
    elastic_connection_error_handler
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Document Search API"}
