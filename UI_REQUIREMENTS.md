# Especificación de Requerimientos UX/UI y Wireframes - ACDC Electronics

## PBI-01: Registro de Cliente
- **Campos en Interfaz:** Nombre Completo, Teléfono de Contacto, Dirección Domiciliaria.
- **Mapeo ORM:** `ClienteModel.nombre`, `ClienteModel.telefono`, `ClienteModel.direccion`.
- **Validaciones UI:** Alertas de error en rojo cuando faltan campos obligatorios.

## PBI-02: Registro de Equipo asociado a Cliente
- **Campos en Interfaz:** Selector de Cliente Registrado, Tipo de Equipo, Marca/Modelo, Falla Reportada.
- **Mapeo ORM:** `EquipoModel.cliente_id`, `EquipoModel.descripcion`, `EquipoModel.tipo`.
- **Validaciones UI:** Restricción de registro si no existe un cliente válido seleccionado.