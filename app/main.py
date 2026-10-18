from fastapi import FastAPI
from elastic_transport import ConnectionError as ElasticConnectionError
from elastic_transport import ConnectionTimeout
from sqlalchemy.exc import OperationalError

from app.api.routes.documents import router as documents_router
from app.core.exceptions import elastic_connection_error_handler
from app.core.exceptions import database_error_handler


app = FastAPI()

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
