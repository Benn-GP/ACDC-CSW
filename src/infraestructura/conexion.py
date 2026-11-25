import os
from sqlalchemy import create_engine
from src.infraestructura.modelos import Base

RUTA_DB = os.environ.get("RUTA_DB", "data/taller.db")


def obtener_motor():
    os.makedirs(os.path.dirname(RUTA_DB), exist_ok=True)
    motor = create_engine(f"sqlite:///{RUTA_DB}")
    Base.metadata.create_all(bind=motor)
    return motor
