import pytest

from src.dominio.cliente import registrar_cliente


def test_registrar_cliente_con_datos_completos():
    resultado = registrar_cliente(
        "Carlos Pérez",
        "987654321",
        "Jr. Las gardenias 112",
    )

    assert resultado["nombre"] == "Carlos Pérez"
    assert resultado["telefono"] == "987654321"
    assert resultado["direccion"] == "Jr. Las gardenias 112"


def test_rechazar_cliente_sin_nombre():
    with pytest.raises(ValueError):
        registrar_cliente("", "987654321", "Jr. Las gardenias 112")


def test_rechazar_cliente_sin_telefono():
    with pytest.raises(ValueError):
        registrar_cliente("Carlos Pérez", "", "Jr. Las gardenias 112")


def test_rechazar_cliente_sin_direccion():
    with pytest.raises(ValueError):
        registrar_cliente("Carlos Pérez", "987654321", "")
