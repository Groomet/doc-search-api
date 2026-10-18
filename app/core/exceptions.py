from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from elastic_transport import ConnectionError as ElasticConnectionError
from elastic_transport import ConnectionTimeout

def elastic_connection_error_handler(
    request: Request,
    exc: ElasticConnectionError | ConnectionTimeout
):
    return JSONResponse(
        status_code=503,
        content={"detail": "Elasticsearch is unavailable"}
    )
    


def database_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database temporarily unavailable"}
    )