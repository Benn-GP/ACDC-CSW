def registrar_cliente(nombre: str, telefono: str, direccion: str) -> dict[str, str]:
    nombre = nombre.strip()
    telefono = telefono.strip()
    direccion = direccion.strip()

    if not nombre:
        raise ValueError("El nombre del cliente es obligatorio")

    if not telefono:
        raise ValueError("El teléfono del cliente es obligatorio")

    if not direccion:
        raise ValueError("La dirección del cliente es obligatoria")

    return {
        "nombre": nombre,
        "telefono": telefono,
        "direccion": direccion,
    }
