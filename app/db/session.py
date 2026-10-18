from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections.abc import Generator
from sqlalchemy.orm import Session

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    echo=True,
    )


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session