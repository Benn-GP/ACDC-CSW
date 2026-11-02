from sqlalchemy import select

from src.infraestructura.modelos import ClienteModel, EquipoModel


def test_guardar_cliente_con_sus_equipos(db_session):
    # Dado un cliente con dos equipos asociados
    cliente = ClienteModel(
        nombre="Ana Quispe",
        telefono="987654321",
        direccion="Jr. Los Girsoles 126"
    )

    EquipoModel(
        descripcion="Lavadora Samsung",
        tipo="Lavadora",
        cliente=cliente
    )

    EquipoModel(
        descripcion="Televisor LG",
        tipo="Televisor",
        cliente=cliente
    )

    # Cuando se persiste en la base de datos
    db_session.add(cliente)
    db_session.commit()

    # Entonces se consulta y se recupera con sus relaciones
    stmt = select(ClienteModel).where(
        ClienteModel.nombre == "Ana Quispe"
    )

    cliente_db = db_session.scalars(stmt).first()

    assert cliente_db is not None
    assert len(cliente_db.equipos) == 2
    assert cliente_db.equipos[0].cliente.nombre == "Ana Quispe"