"""forms.py - Vistas PBI-01 (Cliente), PBI-02 (Equipos) y CU13 (Diagnóstico Técnico)."""
import re

import customtkinter as ctk
import theme as T
from widgets import (
    Chip,
    DataRow,
    InputField,
    ModernCard,
    QuickChipBar,
    StatusPill,
    TextAreaField,
    ValidationBanner,
)

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
NO_SERIAL = {"SIN SERIE", "N/A", "S/N", "NO TIENE"}

# Clientes frecuentes en memoria para autocompletado discreto (sin bloquear escritura)
FREQUENT_CLIENTS = {
    "72849102": {
        "name": "Carlos Mendoza Quispe",
        "phone": "984 512 309",
        "email": "cmendoza.cusco@gmail.com",
        "address": "Urb. Santa Lucila B-12, Wanchaq",
        "client_type": T.CLIENT_TYPES[0],
    },
    "45871236": {
        "name": "Rosa Huamán Condori",
        "phone": "974 201 884",
        "email": "rosa.huaman@outlook.com",
        "address": "Av. Tullumayo 418, Cusco",
        "client_type": T.CLIENT_TYPES[0],
    },
    "20512345678": {
        "name": "Constructora Andina S.A.C.",
        "phone": "984 900 112",
        "email": "logistica@constructoraandina.pe",
        "address": "Parque Industrial E-4, Wanchaq",
        "client_type": T.CLIENT_TYPES[1],
    },
}


def _switch(master, text, command, default=False):
    sw = ctk.CTkSwitch(
        master, text=text, command=command, font=T.font(12),
        text_color=T.TEXT, progress_color=T.ACCENT,
        fg_color=T.BORDER_STRONG, button_color=T.TEXT, button_hover_color=T.ACCENT
    )
    if default:
        sw.select()
    return sw


def _checkbox(master, text, command=None):
    return ctk.CTkCheckBox(
        master, text=text, command=command, font=T.font(12),
        text_color=T.TEXT, fg_color=T.ACCENT,
        hover_color=T.ACCENT_HOVER, border_color=T.BORDER_STRONG,
        checkmark_color=T.TEXT, border_width=2, corner_radius=4
    )


def _insert_snippet(current, snippet):
    current = (current or "").strip()
    if snippet.lower() in current.lower():
        return current
    return f"{current}; {snippet}" if current else snippet


class _MiniMetric(ModernCard):
    def __init__(self, master, caption, value, color=T.ACCENT):
        super().__init__(master)
        self.value_label = ctk.CTkLabel(
            self.body, text=value, anchor="w", font=T.font(24, "bold"), text_color=color
        )
        self.value_label.pack(anchor="w")
        ctk.CTkLabel(
            self.body, text=caption.upper(), anchor="w",
            font=T.font(9, "bold"), text_color=T.TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

    def set_value(self, value):
        self.value_label.configure(text=value)


# ════════════════════════════════════════════════════════════════════════
# PBI-01: REGISTRO CLIENTE (Sin botón RENIEC/SUNAT + Autocompletado)
# ════════════════════════════════════════════════════════════════════════
class ClientForm(ctk.CTkScrollableFrame):
    """PBI-01 (CU01) - Registro de cliente con autocompletado inteligente."""

    def __init__(self, master, on_register=None):
        super().__init__(
            master, fg_color=T.CANVAS, corner_radius=0,
            scrollbar_button_color=T.BORDER_STRONG,
            scrollbar_button_hover_color=T.TEXT_MUTED
        )
        self.columnconfigure(0, weight=1)
        self.on_register = on_register
        self._registered_today = 18
        self._matched_doc = None

        # Header
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=T.OUTER_PAD, pady=T.OUTER_PAD)
        head.columnconfigure(0, weight=1)
        ctk.CTkLabel(
            head, text="PBI-01 • REGISTRO Y FILIACIÓN DE CLIENTE", anchor="w",
            font=T.font(18, "bold"), text_color=T.TEXT
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            head, text="CU01 · Filiación directa del titular y consentimientos de servicio",
            anchor="w", font=T.font(11), text_color=T.TEXT_MUTED
        ).grid(row=1, column=0, sticky="w")
        self.badge = StatusPill(head, "VALIDADOR: EN ESPERA DE DATOS", "warning", size=10)
        self.badge.grid(row=0, column=1, rowspan=2, sticky="e")

        # Tarjeta Datos de Filiación
        card = ModernCard(
            self, "Datos de Filiación",
            "Identificación del titular del servicio (DNI: 8 dígitos | RUC: 11 dígitos)"
        )
        card.grid(row=1, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        b = card.body
        b.columnconfigure((0, 1), weight=1, uniform="cols")

        self.fields = {
            "doc": InputField(b, "DNI / RUC", "8 dígitos (DNI) u 11 dígitos (RUC)", mono=True),
            "type": InputField(b, "Tipo de Cliente", values=T.CLIENT_TYPES),
            "name": InputField(b, "Nombres y Apellidos / Razón Social", "Ej. Carlos Mendoza Quispe"),
            "phone": InputField(b, "Teléfono Móvil (WhatsApp)", "9XX XXX XXX", mono=True),
            "email": InputField(b, "Correo Electrónico", "cliente@correo.com"),
            "address": InputField(b, "Dirección / Distrito (Cusco)", "Ej. Urb. Santa Lucila, Wanchaq"),
        }

        layout = [
            ("doc", 0, 0), ("type", 0, 1),
            ("name", 1, 0), ("phone", 1, 1),
            ("email", 2, 0), ("address", 2, 1),
        ]
        for key, r, c in layout:
            self.fields[key].grid(
                row=r, column=c, sticky="ew",
                padx=(0, 8) if c == 0 else (8, 0), pady=(0, 6)
            )
            self.fields[key].bind_change(self.refresh)

        # Píldora discreta de autocompletado debajo de DNI/RUC
        self.suggest_chip = Chip(
            self.fields["doc"].extra,
            "Cliente frecuente encontrado — Autocompletar",
            self._apply_autocomplete,
            kind="suggest"
        )

        # Preferencias y consentimientos
        prefs = ModernCard(
            self, "Preferencias de Notificación y Consentimiento",
            "CU31 · Canales automáticos de avance y políticas del taller"
        )
        prefs.grid(row=2, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        pb = prefs.body
        pb.columnconfigure((0, 1), weight=1, uniform="p")

        self.sw_whatsapp = _switch(pb, "Notificaciones de avance por WhatsApp (Tiempo real)", self.refresh, True)
        self.sw_sms = _switch(pb, "Alertas SMS de cotización y entrega", self.refresh, False)
        self.chk_terms = _checkbox(pb, "Acepta política de custodia, diagnóstico y disposición RAEE", self.refresh)

        self.sw_whatsapp.grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.sw_sms.grid(row=0, column=1, sticky="w", pady=(0, 10))
        self.chk_terms.grid(row=1, column=0, columnspan=2, sticky="w")

        # Banner de validación
        self.banner = ValidationBanner(self)
        self.banner.grid(row=3, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        self.banner.actions.columnconfigure(0, weight=1)
        self.submit_btn = ctk.CTkButton(
            self.banner.actions,
            text="Registrar y Vincular a Recepción (PBI-02)  →",
            height=42, font=T.font(13, "bold"), corner_radius=T.RADIUS_SM,
            command=self._submit, fg_color=T.BORDER_STRONG, hover_color=T.ACCENT_HOVER,
            text_color=T.TEXT, text_color_disabled=T.TEXT_DIM, state="disabled"
        )
        self.submit_btn.grid(row=0, column=0, sticky="e")

        # Métricas rápidas
        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=4, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        metrics.columnconfigure((0, 1, 2), weight=1, uniform="m")
        self.m_new = _MiniMetric(metrics, "Clientes Registrados Hoy", str(self._registered_today), T.ACCENT)
        self.m_time = _MiniMetric(metrics, "Tiempo Prom. Atención", "01m 35s", T.SUCCESS)
        self.m_notif = _MiniMetric(metrics, "Notificaciones Activas", "96%", T.QUOTE)
        for i, m in enumerate((self.m_new, self.m_time, self.m_notif)):
            m.grid(row=0, column=i, sticky="nsew", padx=(0, 5) if i == 0 else (5, 0) if i == 2 else 5)

        self.refresh()

    def get_data(self):
        return {
            "doc": self.fields["doc"].get().strip(),
            "client_type": self.fields["type"].get(),
            "name": self.fields["name"].get().strip(),
            "phone": self.fields["phone"].get().strip(),
            "email": self.fields["email"].get().strip(),
            "address": self.fields["address"].get().strip(),
            "whatsapp": bool(self.sw_whatsapp.get()),
            "sms": bool(self.sw_sms.get()),
            "terms": bool(self.chk_terms.get()),
        }

    @staticmethod
    def _doc_error(doc):
        doc = doc.replace(" ", "")
        if not doc:
            return "Ingrese un DNI (8 dígitos) o RUC (11 dígitos) válido"
        if not doc.isdigit():
            return "El DNI/RUC solo admite dígitos numéricos"
        if len(doc) < 8:
            return f"DNI incompleto ({len(doc)}/8 dígitos)"
        if len(doc) in (9, 10):
            return f"Documento incompleto ({len(doc)} dígitos; DNI=8, RUC=11)"
        if len(doc) > 11:
            return "El documento excede los 11 dígitos"
        if len(doc) == 11 and doc[:2] not in ("10", "15", "17", "20"):
            return "RUC inválido (debe iniciar con 10, 15, 17 o 20)"
        return None

    def _validate(self, d):
        errs = {}
        e = self._doc_error(d["doc"])
        if e:
            errs["doc"] = e
        if len(d["name"]) < 3 or not re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", d["name"]):
            errs["name"] = "Ingrese nombres y apellidos o razón social"
        phone = re.sub(r"[\s-]", "", d["phone"])
        if not phone.isdigit() or len(phone) != 9 or not phone.startswith("9"):
            errs["phone"] = "Móvil peruano: 9 dígitos iniciando en 9"
        if not EMAIL_RE.match(d["email"]):
            errs["email"] = "Correo electrónico con formato inválido"
        if len(d["address"]) < 5:
            errs["address"] = "Ingrese dirección / distrito en Cusco"
        return errs

    def _check_autocomplete(self, clean_doc):
        if clean_doc in FREQUENT_CLIENTS:
            self._matched_doc = clean_doc
            profile = FREQUENT_CLIENTS[clean_doc]
            label = f"Cliente frecuente encontrado ({profile['name']}) — Autocompletar"
            self.suggest_chip.configure(text=label, width=int(len(label) * 6.6 + 28))
            self.suggest_chip.pack(anchor="w", pady=(2, 0))
        else:
            self._matched_doc = None
            self.suggest_chip.pack_forget()

    def _apply_autocomplete(self):
        if not self._matched_doc or self._matched_doc not in FREQUENT_CLIENTS:
            return
        profile = FREQUENT_CLIENTS[self._matched_doc]
        self.fields["name"].set(profile["name"])
        self.fields["phone"].set(profile["phone"])
        self.fields["email"].set(profile["email"])
        self.fields["address"].set(profile["address"])
        self.fields["type"].set(profile["client_type"])
        self.chk_terms.select()
        self.refresh()

    def refresh(self, *_):
        d = self.get_data()
        clean_doc = d["doc"].replace(" ", "")
        self._check_autocomplete(clean_doc)

        errs = self._validate(d)
        messages = list(errs.values())
        if not d["terms"]:
            messages.append("Acepte la política de custodia, diagnóstico y disposición RAEE")

        for key in ("doc", "name", "phone", "email", "address"):
            field = self.fields[key]
            if not d[key]:
                field.set_state("neutral")
            elif key in errs:
                field.set_state("error", errs[key])
            else:
                ok_msg = (
                    "✓ DNI válido (8 dígitos)" if key == "doc" and len(clean_doc) == 8
                    else "✓ RUC válido (11 dígitos)" if key == "doc" and len(clean_doc) == 11
                    else ""
                )
                field.set_state("ok", ok_msg)

        empty = not any(d[k] for k in ("doc", "name", "phone", "email", "address"))
        valid = not messages

        if empty:
            self.badge.set("VALIDADOR: EN ESPERA DE DATOS", "warning")
            self.banner.show_waiting(
                "Ingrese DNI (8 dígitos) o RUC (11 dígitos) y complete los datos del titular. "
                "Pruebe con 72849102 o 45871236 para autocompletado frecuente."
            )
        elif valid:
            self.badge.set("CLIENTE VERIFICADO", "success")
            self.banner.show_ok(
                "Datos válidos y política aceptada. Pulse el botón para vincular al titular en recepción.",
                "✔  LISTO PARA REGISTRAR"
            )
        else:
            self.badge.set("ERROR DE VALIDACIÓN", "danger")
            self.banner.show_errors(messages)

        self.submit_btn.configure(
            state="normal" if valid else "disabled",
            fg_color=T.ACCENT if valid else T.BORDER_STRONG
        )
        return valid

    def reset(self):
        for key in ("doc", "name", "phone", "email", "address"):
            self.fields[key].clear()
        self._matched_doc = None
        self.suggest_chip.pack_forget()
        self.fields["type"].set(T.CLIENT_TYPES[0])
        self.sw_whatsapp.select()
        self.sw_sms.deselect()
        self.chk_terms.deselect()
        self.refresh()

    def _submit(self):
        if not self.refresh():
            return
        data = self.get_data()
        FREQUENT_CLIENTS[data["doc"].replace(" ", "")] = {
            "name": data["name"],
            "phone": data["phone"],
            "email": data["email"],
            "address": data["address"],
            "client_type": data["client_type"],
        }
        self._registered_today += 1
        self.m_new.set_value(str(self._registered_today))
        self.reset()
        if self.on_register:
            self.on_register(data)


# ════════════════════════════════════════════════════════════════════════
# PBI-02: INGRESO EQUIPOS (Titular fijo arriba + QuickChipBar dinámico)
# ════════════════════════════════════════════════════════════════════════
class EquipmentForm(ctk.CTkFrame):
    """PBI-02 (CU12/CU20) - Ingreso de equipo con titular siempre visible."""

    FAULT_LIMIT = 400

    def __init__(
        self, master, on_change=None, on_generate=None, on_new_equipment=None,
        on_change_client=None, serial_lookup=None
    ):
        super().__init__(master, fg_color=T.CANVAS, corner_radius=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.on_change = on_change
        self.on_generate = on_generate
        self.on_new_equipment = on_new_equipment
        self.on_change_client = on_change_client
        self.serial_lookup = serial_lookup
        self.client = {}

        # Encabezado fijo
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(T.OUTER_PAD, 8))
        head.columnconfigure(0, weight=1)
        ctk.CTkLabel(
            head, text="PBI-02 • INGRESO DE EQUIPO Y ORDEN DE SERVICIO", anchor="w",
            font=T.font(18, "bold"), text_color=T.TEXT
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            head, text="CU12 / CU20 · Recepción técnica, custodia y destino del equipo",
            anchor="w", font=T.font(11), text_color=T.TEXT_MUTED
        ).grid(row=1, column=0, sticky="w")
        StatusPill(head, "RECEPCIÓN ACTIVA", "info", size=10).grid(row=0, column=1, rowspan=2, sticky="e")

        # Tarjeta Cliente Titular Vinculado (SIEMPRE visible arriba)
        self.client_card = ModernCard(self, "Cliente Titular Vinculado", accent=True)
        self.client_card.grid(row=1, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, 8))
        cb = self.client_card.body
        cb.columnconfigure(1, weight=1)

        avatar = ctk.CTkFrame(
            cb, width=46, height=46, corner_radius=23,
            fg_color=T.ACCENT_SOFT, border_color=T.ACCENT, border_width=1
        )
        avatar.grid(row=0, column=0, rowspan=2, padx=(0, 12))
        avatar.grid_propagate(False)
        self.initials = ctk.CTkLabel(avatar, text="", font=T.font(15, "bold"), text_color=T.ACCENT)
        self.initials.place(relx=0.5, rely=0.5, anchor="center")

        self.client_name = ctk.CTkLabel(cb, text="", anchor="w", font=T.font(14, "bold"), text_color=T.TEXT)
        self.client_name.grid(row=0, column=1, sticky="w")
        self.client_meta = ctk.CTkLabel(cb, text="", anchor="w", font=T.font(11), text_color=T.TEXT_MUTED)
        self.client_meta.grid(row=1, column=1, sticky="w")

        StatusPill(cb, "TITULAR VERIFICADO", "success").grid(row=0, column=2, rowspan=2, padx=(8, 8))
        ctk.CTkButton(
            cb, text="Cambiar Cliente", width=130, height=34, corner_radius=T.RADIUS_SM,
            font=T.font(11, "bold"), fg_color="transparent", border_width=1,
            border_color=T.BORDER_STRONG, text_color=T.TEXT_MUTED, hover_color=T.PANEL,
            command=lambda: self.on_change_client and self.on_change_client()
        ).grid(row=0, column=3, rowspan=2)

        # Área desplazable con todos los campos
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=T.CANVAS, corner_radius=0,
            scrollbar_button_color=T.BORDER_STRONG, scrollbar_button_hover_color=T.TEXT_MUTED
        )
        scroll.grid(row=2, column=0, sticky="nsew")
        scroll.columnconfigure(0, weight=1)

        # Hardware
        hw = ModernCard(
            scroll, "Detalles del Hardware en Mesón",
            "Identificación técnica y estado físico al ingreso (edición libre o chips)"
        )
        hw.grid(row=0, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        hb = hw.body
        hb.columnconfigure((0, 1), weight=1, uniform="h")

        self.category = InputField(hb, "Categoría de Equipo", values=T.CATEGORIES)
        self.brand = InputField(hb, "Marca", values=T.BRANDS, editable=True, initial="")
        self.model = InputField(hb, "Modelo Exacto", "Ej. SOLE-SOL10L / GN", mono=True)
        self.serial = InputField(hb, "Número de Serie (S/N)", "S/N del fabricante o 'SIN SERIE'", mono=True)
        self.condition = InputField(
            hb, "Estado Físico / Specs y Daños Previos",
            "Ej. Carcasa con rayones leves en lateral derecho, sin perilla inferior"
        )

        self.category.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 6))
        self.brand.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        self.model.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 6))
        self.serial.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        self.condition.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.cond_chips = QuickChipBar(
            self.condition.extra, T.CONDITION_CHIPS, self._pick_condition,
            caption="AUTOCOMPLETAR ESTADO FÍSICO"
        )
        self.cond_chips.pack(fill="x", pady=(2, 0))

        for f in (self.category, self.brand, self.model, self.serial, self.condition):
            f.bind_change(self._changed)

        # Falla declarada
        fault = ModernCard(
            scroll, "Falla Declarada por Cliente",
            "Describa el síntoma reportado o pulse los chips para insertar observaciones"
        )
        fault.grid(row=1, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        fault.body.columnconfigure(0, weight=1)

        self.fault_field = TextAreaField(
            fault.body, "Síntomas y Observaciones de Ingreso", height=90, limit=self.FAULT_LIMIT
        )
        self.fault_field.grid(row=0, column=0, sticky="ew")
        self.fault_field.bind_change(self._changed)

        self.fault_chips = QuickChipBar(
            fault.body, T.FAULT_CHIPS, self._pick_fault,
            caption="AUTOCOMPLETAR FALLA DECLARADA"
        )
        self.fault_chips.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        # Accesorios
        acc = ModernCard(
            scroll, "Accesorios en Custodia",
            "Marque todo lo que el cliente deja junto al equipo"
        )
        acc.grid(row=2, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        acc.body.columnconfigure((0, 1, 2), weight=1, uniform="a")
        self.acc_checks = {}
        for i, name in enumerate(T.ACCESSORIES):
            c = _checkbox(acc.body, name, lambda n=name: self._accessory_toggled(n))
            c.grid(row=i // 3, column=i % 3, sticky="w", pady=5, padx=(0, 8))
            self.acc_checks[name] = c

        # Destino sostenible
        dest = ModernCard(
            scroll, "Destino del Equipo (Gestión Sostenible)",
            "Reparación o evaluación para disposición RAEE / reciclaje"
        )
        dest.grid(row=3, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        dest.body.columnconfigure(0, weight=1)
        self.destination = ctk.CTkSegmentedButton(
            dest.body, values=T.DESTINATIONS, command=lambda _v: self._changed(),
            fg_color=T.INPUT_BG, selected_color=T.ACCENT, selected_hover_color=T.ACCENT_HOVER,
            unselected_color=T.INPUT_BG, unselected_hover_color=T.PANEL,
            text_color=T.TEXT, font=T.font(12, "bold"), corner_radius=T.RADIUS_SM, height=36
        )
        self.destination.set(T.DESTINATIONS[0])
        self.destination.grid(row=0, column=0, sticky="ew")

        # Barra de acciones fija al pie
        action = ctk.CTkFrame(
            self, fg_color=T.CARD, border_color=T.BORDER, border_width=1, corner_radius=0
        )
        action.grid(row=3, column=0, sticky="ew")
        action.columnconfigure(0, weight=1)

        self.hint = ctk.CTkLabel(
            action, text="", anchor="w", font=T.font(11),
            text_color=T.TEXT_MUTED, justify="left", wraplength=430
        )
        self.hint.grid(row=0, column=0, sticky="w", padx=T.OUTER_PAD, pady=10)

        ctk.CTkButton(
            action, text="Nuevo Equipo (mismo cliente)", height=40, width=195,
            font=T.font(11, "bold"), corner_radius=T.RADIUS_SM, fg_color="transparent",
            border_width=1, border_color=T.BORDER_STRONG, text_color=T.TEXT_MUTED,
            hover_color=T.PANEL, command=self._new_equipment
        ).grid(row=0, column=1, padx=6, pady=10)

        self.generate_btn = ctk.CTkButton(
            action, text="", height=40, font=T.font(12, "bold"), corner_radius=T.RADIUS_SM,
            fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER, text_color=T.TEXT,
            command=self._generate
        )
        self.generate_btn.grid(row=0, column=2, padx=(0, T.OUTER_PAD), pady=10)

        self.set_order_code("#TALLER-2026-089")
        self.set_client({
            "name": "Carlos Mendoza Quispe",
            "doc": "72849102",
            "phone": "984 512 309",
            "client_type": T.CLIENT_TYPES[0],
        })
        self._update_serial()
        self._update_hint()

    def _pick_condition(self, snippet):
        self.condition.set(_insert_snippet(self.condition.get(), snippet))
        self._changed()

    def _pick_fault(self, snippet):
        self.fault_field.set(_insert_snippet(self.fault_field.get(), snippet))
        self._changed()

    def set_order_code(self, code):
        self.generate_btn.configure(text=f"Confirmar Ingreso y Emitir Orden {code}")

    def set_client(self, client):
        self.client = dict(client)
        name = client.get("name", "") or "—"
        doc = client.get("doc", "")
        doc_type = "RUC" if len(doc) == 11 else "DNI"
        words = [w for w in name.split() if w]
        self.initials.configure(text=("".join(w[0] for w in words[:2]) or "?").upper())
        self.client_name.configure(text=f"{name}  —  {doc_type}: {doc}  —  Tel: {client.get('phone', '')}")
        self.client_meta.configure(text=f"Tipo de cliente: {client.get('client_type', T.CLIENT_TYPES[0])}")

    def get_data(self):
        return {
            "category": self.category.get(),
            "brand": self.brand.get().strip(),
            "model": self.model.get().strip(),
            "serial": self.serial.get().strip().upper(),
            "condition": self.condition.get().strip(),
            "fault": self.fault_field.get(),
            "accessories": [n for n, c in self.acc_checks.items() if c.get()],
            "destination": self.destination.get(),
        }

    def _serial_owner(self):
        s = self.serial.get().strip().upper()
        if not s or s in NO_SERIAL or not self.serial_lookup:
            return None
        return self.serial_lookup(s)

    def _update_serial(self):
        s = self.serial.get().strip().upper()
        if not s:
            self.serial.set_state("neutral")
        elif s in NO_SERIAL:
            self.serial.set_state("warn", "⚠ Equipo sin serie: se registra como 'SIN SERIE'")
        else:
            owner = self._serial_owner()
            if owner:
                self.serial.set_state("error", f"✗ S/N duplicado: ya ingresó en {owner}")
            else:
                self.serial.set_state("ok", "✓ S/N Único en Taller")

    def _missing(self):
        d = self.get_data()
        out = []
        if not self.client.get("doc"):
            out.append("Cliente vinculado")
        if not d["brand"]:
            out.append("Marca")
        if not d["model"]:
            out.append("Modelo")
        if not d["serial"]:
            out.append("S/N")
        if not d["condition"]:
            out.append("Estado físico")
        if not d["fault"]:
            out.append("Falla declarada")
        if not d["accessories"]:
            out.append("Accesorios")
        if self._serial_owner():
            out.append("S/N no duplicado")
        return out

    def _update_hint(self, emitted=False):
        if emitted:
            self.hint.configure(
                text="✔ Orden emitida y disponible en Diagnóstico Técnico (CU13).",
                text_color=T.SUCCESS
            )
            return
        missing = self._missing()
        if missing:
            self.hint.configure(text="Pendiente: " + ", ".join(missing), text_color=T.WARNING)
        else:
            self.hint.configure(text="✔ Datos completos. Listo para emitir la orden.", text_color=T.SUCCESS)

    def _changed(self, *_):
        self._update_serial()
        self._update_hint()
        self.cond_chips.sync(self.condition.get())
        self.fault_chips.sync(self.fault_field.get())
        if self.on_change:
            self.on_change()

    def _accessory_toggled(self, name):
        base = "Solo Equipo Base"
        if name == base and self.acc_checks[base].get():
            for n, c in self.acc_checks.items():
                if n != base:
                    c.deselect()
        elif name != base and self.acc_checks[name].get():
            self.acc_checks[base].deselect()
        self._changed()

    def _generate(self):
        missing = self._missing()
        if missing:
            self.hint.configure(text="No se puede emitir. Falta: " + ", ".join(missing), text_color=T.DANGER)
            return
        if self.on_generate:
            self.on_generate(self.get_data())
        self._update_hint(emitted=True)

    def _new_equipment(self):
        if self.on_new_equipment:
            self.on_new_equipment()

    def reset_equipment(self):
        self.category.set(T.CATEGORIES[0])
        self.brand.set("")
        for e in (self.model, self.serial, self.condition):
            e.clear()
        self.fault_field.set("")
        for c in self.acc_checks.values():
            c.deselect()
        self.destination.set(T.DESTINATIONS[0])
        self.cond_chips.sync("")
        self.fault_chips.sync("")
        self._update_serial()
        self._update_hint()


# ════════════════════════════════════════════════════════════════════════
# CU13: DIAGNÓSTICO TÉCNICO INTERACTIVO (Con catálogos T.PARTS / T.CHECKLIST)
# ════════════════════════════════════════════════════════════════════════
class DiagnosticView(ctk.CTkScrollableFrame):
    """CU13 - Banco de pruebas, checklist, repuestos, cotización y estado en vivo."""

    def __init__(self, master, get_orders, on_update_order):
        super().__init__(
            master, fg_color=T.CANVAS, corner_radius=0,
            scrollbar_button_color=T.BORDER_STRONG, scrollbar_button_hover_color=T.TEXT_MUTED
        )
        self.columnconfigure(0, weight=1)
        self.get_orders = get_orders
        self.on_update_order = on_update_order
        self._selected_code = None
        self._row_widgets = {}

        # Header
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=T.OUTER_PAD, pady=T.OUTER_PAD)
        head.columnconfigure(0, weight=1)
        ctk.CTkLabel(
            head, text="CU13 • DIAGNÓSTICO TÉCNICO Y COTIZACIÓN EN BANCO", anchor="w",
            font=T.font(18, "bold"), text_color=T.TEXT
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            head, text="Banco de pruebas, checklist técnico, repuestos y cambio de estado en tiempo real",
            anchor="w", font=T.font(11), text_color=T.TEXT_MUTED
        ).grid(row=1, column=0, sticky="w")
        StatusPill(head, "BANCO TÉCNICO 01", "warning", size=10).grid(row=0, column=1, rowspan=2, sticky="e")

        # KPIs en vivo
        kpis = ctk.CTkFrame(self, fg_color="transparent")
        kpis.grid(row=1, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        kpis.columnconfigure((0, 1, 2), weight=1, uniform="dk")
        self.k_total = _MiniMetric(kpis, "Equipos en Banco", "0", T.ACCENT)
        self.k_pending = _MiniMetric(kpis, "Pendientes de Cotizar", "0", T.WARNING)
        self.k_done = _MiniMetric(kpis, "Cotizados / Reparados", "0", T.SUCCESS)
        for i, k in enumerate((self.k_total, self.k_pending, self.k_done)):
            k.grid(row=0, column=i, sticky="nsew", padx=(0, 5) if i == 0 else (5, 0) if i == 2 else 5)

        # Lista interactiva de órdenes en banco
        list_card = ModernCard(
            self, "Órdenes en Banco Técnico",
            "Seleccione una orden para inspeccionar su falla, ejecutar pruebas y cotizar"
        )
        list_card.grid(row=2, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        self.list_body = list_card.body
        self.list_body.columnconfigure(0, weight=1)

        # Panel de Evaluación Técnica (CU13)
        eval_card = ModernCard(
            self, "Panel de Evaluación Técnica (CU13)",
            "Diagnóstico del especialista, checklist de pruebas y cálculo automático en S/",
            accent=True
        )
        eval_card.grid(row=3, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))
        eb = eval_card.body
        eb.columnconfigure((0, 1), weight=1, uniform="ev")

        self.sel_pill = StatusPill(eval_card.header_right, "SIN SELECCIÓN", "neutral", size=10)
        self.sel_pill.pack()

        # Comparativa Falla Reportada vs Orden
        info_panel = ModernCard(eb, level="panel")
        info_panel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        info_panel.body.columnconfigure(0, weight=1)
        self.lbl_order_head = ctk.CTkLabel(
            info_panel.body, text="", anchor="w", font=T.font(13, "bold"), text_color=T.TEXT
        )
        self.lbl_order_head.grid(row=0, column=0, sticky="w")
        self.lbl_reported_fault = ctk.CTkLabel(
            info_panel.body, text="", anchor="w", justify="left", wraplength=640,
            font=T.font(11), text_color=T.TEXT_MUTED
        )
        self.lbl_reported_fault.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # Checklist de pruebas realizadas (T.CHECKLIST)
        chk_panel = ModernCard(eb, "Checklist de Pruebas Realizadas", level="panel")
        chk_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        self.bench_checks = []
        for i, label in enumerate(T.CHECKLIST):
            cb = _checkbox(chk_panel.body, label, self._recalc_quote)
            cb.grid(row=i, column=0, sticky="w", pady=5)
            self.bench_checks.append(cb)

        # Selector de repuestos y cotización (T.PARTS)
        quote_panel = ModernCard(eb, "Repuestos y Cotización Automática", level="panel")
        quote_panel.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))
        quote_panel.body.columnconfigure(0, weight=1)

        part_options = ["Ninguno (S/ 0.00)"] + [f"{k} (S/ {v:.2f})" for k, v in T.PARTS.items()]
        self.part_combo = InputField(quote_panel.body, "Repuesto Necesario", values=part_options)
        self.part_combo.grid(row=0, column=0, sticky="ew")
        self.part_combo.bind_change(self._recalc_quote)

        self.labor_field = InputField(quote_panel.body, "Mano de Obra (S/)", "60.00", mono=True)
        self.labor_field.set("60.00")
        self.labor_field.grid(row=1, column=0, sticky="ew")
        self.labor_field.bind_change(self._recalc_quote)

        self.lbl_total = ctk.CTkLabel(
            quote_panel.body, text="TOTAL COTIZACIÓN: S/ 60.00", anchor="w",
            font=T.font(14, "bold", mono=True), text_color=T.SUCCESS
        )
        self.lbl_total.grid(row=2, column=0, sticky="w", pady=(4, 0))

        # Diagnóstico técnico + chips (T.DIAG_CHIPS)
        self.diag_notes = TextAreaField(
            eb, "Diagnóstico Técnico del Especialista", height=84, limit=350
        )
        self.diag_notes.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.diag_notes.bind_change(lambda: self.diag_chips.sync(self.diag_notes.get()))

        self.diag_chips = QuickChipBar(
            eb, T.DIAG_CHIPS, self._pick_diag, caption="AUTOCOMPLETAR HALLAZGO TÉCNICO"
        )
        self.diag_chips.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 12))

        # Botones de cambio de estado en vivo
        btns = ctk.CTkFrame(eb, fg_color="transparent")
        btns.grid(row=4, column=0, columnspan=2, sticky="ew")
        btns.columnconfigure(0, weight=1)

        self.feedback_lbl = ctk.CTkLabel(
            btns, text="", anchor="w", font=T.font(11, "bold"), text_color=T.SUCCESS
        )
        self.feedback_lbl.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            btns, text="En Diagnóstico", height=38, corner_radius=T.RADIUS_SM,
            fg_color=T.WARNING_SOFT, border_width=1, border_color=T.WARNING,
            text_color=T.WARNING, hover_color=T.PANEL, font=T.font(11, "bold"),
            command=lambda: self._save_status("DIAGNÓSTICO")
        ).grid(row=0, column=1, padx=6)

        ctk.CTkButton(
            btns, text="Pasar a Cotizado", height=38, corner_radius=T.RADIUS_SM,
            fg_color=T.QUOTE_SOFT, border_width=1, border_color=T.QUOTE,
            text_color=T.QUOTE, hover_color=T.PANEL, font=T.font(11, "bold"),
            command=lambda: self._save_status("COTIZADO")
        ).grid(row=0, column=2, padx=6)

        ctk.CTkButton(
            btns, text="✔ Marcar Reparado", height=38, corner_radius=T.RADIUS_SM,
            fg_color=T.SUCCESS, hover_color=T.SUCCESS_HOVER,
            text_color=T.TEXT, font=T.font(11, "bold"),
            command=lambda: self._save_status("LISTO")
        ).grid(row=0, column=3)

    def _pick_diag(self, snippet):
        self.diag_notes.set(_insert_snippet(self.diag_notes.get(), snippet))
        self.diag_chips.sync(self.diag_notes.get())

    def refresh_orders(self, select_code=None):
        orders = self.get_orders()
        self.k_total.set_value(str(len(orders)))
        self.k_pending.set_value(str(sum(1 for o in orders if o["status"] in ("EN MESA", "DIAGNÓSTICO"))))
        self.k_done.set_value(str(sum(1 for o in orders if o["status"] in ("COTIZADO", "LISTO"))))

        for w in self.list_body.winfo_children():
            w.destroy()
        self._row_widgets.clear()

        if select_code:
            self._selected_code = select_code
        elif not self._selected_code and orders:
            self._selected_code = orders[0]["code"]

        for i, order in enumerate(orders):
            code = order["code"]
            row = DataRow(self.list_body, on_click=lambda c=code: self._select_order(c), edge=T.BORDER)
            row.grid(row=i, column=0, sticky="ew", pady=3)
            row.columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=code, font=T.font(11, "bold", mono=True), text_color=T.ACCENT
            ).grid(row=0, column=0, rowspan=2, padx=(12, 12), pady=8)

            ctk.CTkLabel(
                row, text=f"{order['equipment']}  —  {order['client']}",
                anchor="w", font=T.font(12, "bold"), text_color=T.TEXT
            ).grid(row=0, column=1, sticky="w", pady=(6, 0))

            ctk.CTkLabel(
                row, text=f"Ingreso: {order['time']}  ·  Diagnóstico: {order.get('diagnosis') or 'Pendiente de revisión en banco'}",
                anchor="w", font=T.font(10), text_color=T.TEXT_MUTED
            ).grid(row=1, column=1, sticky="w", pady=(0, 6))

            StatusPill(
                row, order["status"], T.STATUS_KIND.get(order["status"], "neutral"),
                dot=False, size=9
            ).grid(row=0, column=2, rowspan=2, padx=12)

            row.finalize()
            self._row_widgets[code] = row

        if self._selected_code:
            self._select_order(self._selected_code, silent=True)

    def _select_order(self, code, silent=False):
        self._selected_code = code
        for c, row in self._row_widgets.items():
            row.set_selected(c == code)

        order = next((o for o in self.get_orders() if o["code"] == code), None)
        if not order:
            return

        self.sel_pill.set(f"{order['code']} · {order['status']}", T.STATUS_KIND.get(order["status"], "info"))
        self.lbl_order_head.configure(text=f"{order['code']}  |  {order['equipment']}  —  Titular: {order['client']}")
        self.lbl_reported_fault.configure(text=f"Falla reportada por el cliente: {order.get('fault', 'Sin descripción')}")
        self.diag_notes.set(order.get("diagnosis", ""))
        self.diag_chips.sync(order.get("diagnosis", ""))
        self.labor_field.set(f"{order.get('labor', 60.0):.2f}")

        saved_checks = set(order.get("checks", []))
        for cb, label in zip(self.bench_checks, T.CHECKLIST):
            if label in saved_checks:
                cb.select()
            else:
                cb.deselect()

        part_name = order.get("part_name", "")
        if part_name in T.PARTS:
            self.part_combo.set(f"{part_name} (S/ {T.PARTS[part_name]:.2f})")
        else:
            self.part_combo.set("Ninguno (S/ 0.00)")

        self._recalc_quote()
        if not silent:
            self.feedback_lbl.configure(text="")

    def _get_part_and_price(self):
        sel = self.part_combo.get()
        for name, price in T.PARTS.items():
            if sel.startswith(name):
                return name, price
        return "", 0.0

    def _recalc_quote(self, *_):
        _, part_price = self._get_part_and_price()
        try:
            labor = max(0.0, float(self.labor_field.get() or 0))
        except ValueError:
            labor = 0.0
        total = part_price + labor
        self.lbl_total.configure(text=f"TOTAL COTIZACIÓN: S/ {total:.2f}")
        return total, labor

    def _save_status(self, new_status):
        if not self._selected_code:
            return
        total, labor = self._recalc_quote()
        part_name, _ = self._get_part_and_price()
        notes = self.diag_notes.get() or "Evaluación técnica completada en banco."
        checked = [lbl for cb, lbl in zip(self.bench_checks, T.CHECKLIST) if cb.get()]

        self.on_update_order(
            self._selected_code,
            status=new_status,
            diagnosis=notes,
            labor=labor,
            part_name=part_name,
            quote_total=total,
            checks=checked,
        )
        self.feedback_lbl.configure(
            text=f"✔ {self._selected_code} actualizado a '{new_status}' (Total: S/ {total:.2f})"
        )