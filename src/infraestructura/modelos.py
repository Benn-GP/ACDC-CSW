from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Clase base declarativa para todas las entidades ORM."""


class ClienteModel(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=True)
    direccion: Mapped[str] = mapped_column(String(200), nullable=True)

    pedidos: Mapped[list["PedidoModel"]] = relationship(
        "PedidoModel", back_populates="cliente"
    )
    equipos: Mapped[list["EquipoModel"]] = relationship(
        "EquipoModel", back_populates="cliente"
    )


class PedidoModel(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id"), nullable=False
    )

    cliente: Mapped["ClienteModel"] = relationship(
        "ClienteModel", back_populates="pedidos"
    )


class EquipoModel(Base):
    __tablename__ = "equipos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id"), nullable=False
    )

    cliente: Mapped["ClienteModel"] = relationship(
        "ClienteModel", back_populates="equipos"
    )