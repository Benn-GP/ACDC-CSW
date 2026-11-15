"""theme.py - Tokens de diseño de ACDC Electronics Lab (dark moderno de alto contraste)."""

# ── Superficies ─────────────────────────────────────────────────────────
CANVAS = "#070b14"          # lienzo profundo
CARD = "#111827"            # tarjetas elevadas
PANEL = "#1e293b"           # sub-paneles
INPUT_BG = "#0b1220"        # campos de entrada
BORDER = "#1f2937"          # borde nítido de tarjetas
BORDER_STRONG = "#334155"   # borde de inputs / sub-paneles

# ── Acentos ─────────────────────────────────────────────────────────────
ACCENT = "#06b6d4"
ACCENT_HOVER = "#0891b2"
ACCENT_SOFT = "#083344"

SUCCESS = "#10b981"
SUCCESS_HOVER = "#059669"
SUCCESS_SOFT = "#052e26"
SUCCESS_SOFT_HOVER = "#065f46"

DANGER = "#ef4444"
DANGER_SOFT = "#450a0a"
DANGER_BORDER = "#dc2626"

WARNING = "#f59e0b"
WARNING_SOFT = "#451a03"

QUOTE = "#a5b4fc"
QUOTE_SOFT = "#1e1b4b"

TEXT = "#f8fafc"
TEXT_MUTED = "#94a3b8"
TEXT_DIM = "#64748b"

ROW_HOVER = "#162033"
ROW_SELECTED = "#0c2c38"

# Papel térmico del comprobante
PAPER = "#e5e7eb"
PAPER_TEXT = "#0b1120"

# ── Geometría y espaciado ───────────────────────────────────────────────
RADIUS = 10
RADIUS_SM = 6
RADIUS_PILL = 12
BORDER_W = 1
OUTER_PAD = 12
INNER_PADX = 16
INNER_PADY = 14
SIDEBAR_W = 245
RIGHT_W = 370

# ── Tipografía ──────────────────────────────────────────────────────────
FONT_UI = "Segoe UI"
FONT_MONO = "Consolas"


def font(size=12, weight="normal", mono=False):
    return (FONT_MONO if mono else FONT_UI, size, weight)


# ── Estilos de pills: kind -> (fondo, texto/borde) ──────────────────────
BADGE_STYLES = {
    "success": (SUCCESS_SOFT, SUCCESS),
    "danger": (DANGER_SOFT, DANGER),
    "warning": (WARNING_SOFT, WARNING),
    "info": (ACCENT_SOFT, ACCENT),
    "quote": (QUOTE_SOFT, QUOTE),
    "neutral": (INPUT_BG, TEXT_MUTED),
}

# ── Datos de negocio ────────────────────────────────────────────────────
COMPANY_NAME = "ACDC ELECTRONICS"
COMPANY_RUC = "20608491021"
COMPANY_ADDRESS = "Urb. Santa Lucila A-16"
COMPANY_TEL = "984 841 733 / 940 200 565"
COMPANY_HOURS = "10:00 - 20:00"

CLIENT_TYPES = ["Particular / Hogar", "Empresa / MYPE", "Garantía de Marca"]
CATEGORIES = [
    "Terma / Calentador", "Lavadora / Secadora", "Televisor Smart TV",
    "Computadora / Laptop", "Equipo de Sonido", "Placa Electrónica"
]
BRANDS = [
    "Sole", "Panasonic", "LG", "Samsung", "Sony", "Whirlpool", "Bosch",
    "HP / Lenovo", "Otro"
]
ACCESSORIES = [
    "Cable de Poder", "Control Remoto", "Cargador / Fuente",
    "Mangueras / Racores", "Manual / Boleta Previa", "Solo Equipo Base"
]
DESTINATIONS = ["Reparación", "Evaluación RAEE / Reciclaje"]

STATUSES = ["EN MESA", "DIAGNÓSTICO", "COTIZADO", "LISTO"]
STATUS_KIND = {
    "EN MESA": "info",
    "DIAGNÓSTICO": "warning",
    "COTIZADO": "quote",
    "LISTO": "success",
}

CHECKLIST = ["Fuente de poder", "Placa principal", "Sensores", "Prueba de carga"]

# Precios referenciales en S/ (catálogo de demostración)
PARTS = {
    "Fuente de poder": 95.0,
    "Placa principal": 180.0,
    "Sensor / Termostato": 45.0,
    "Resistencia / Elemento": 60.0,
    "Bomba / Electroválvula": 85.0,
    "Capacitores (kit)": 25.0,
    "Cable / Conector": 15.0,
    "Panel LED / Display": 220.0,
}

# Chips de autocompletado: (etiqueta, texto técnico insertado)
CONDITION_CHIPS = [
    ("Carcasa rayada", "Carcasa con rayones visibles"),
    ("Golpe / abolladura", "Golpe o abolladura visible en carcasa"),
    ("Sin perilla / botón", "Falta perilla o botón de mando"),
    ("Sin control remoto", "Se recibe sin control remoto"),
    ("Pantalla con fisura", "Panel / pantalla con fisura visible"),
    ("Oxidación / humedad", "Signos de oxidación o humedad interna"),
    ("Sin daños visibles", "Sin daños físicos visibles al ingreso"),
]
FAULT_CHIPS = [
    ("No enciende", "No enciende; sin respuesta al pulsar el botón de encendido"),
    ("Sin imagen", "Enciende pero sin imagen en pantalla"),
    ("Fuga de agua / gas", "Presenta fuga de agua / gas (cerrar suministro)"),
    ("No calienta el agua", "No calienta el agua al abrir la llave"),
    ("Chasquido intermitente", "Chasquido intermitente al intentar encender"),
    ("Se apaga solo", "Se apaga solo tras unos minutos de uso"),
    ("Ruido anormal", "Ruido anormal durante el funcionamiento"),
]
DIAG_CHIPS = [
    ("Placa principal dañada", "Placa principal con componentes dañados"),
    ("Fuente sin salida", "Fuente de poder sin salida de voltaje"),
    ("Sensor defectuoso", "Sensor / termostato defectuoso"),
    ("Capacitores hinchados", "Capacitores hinchados o con fuga"),
    ("Requiere repuesto", "Requiere reemplazo de repuesto"),
    ("Falla no reproducible", "Falla no reproducible en banco"),
]