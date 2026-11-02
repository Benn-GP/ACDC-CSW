import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infraestructura.modelos import Base


@pytest.fixture(scope="function")
def db_session():
    """Sesion limpia de SQLite en memoria para cada prueba."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    yield session

    session.close()
    engine.dispose()