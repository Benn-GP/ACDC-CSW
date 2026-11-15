"""main_window.py - Ventana principal de ACDC Electronics Lab (ACDC SmartFix)."""
from datetime import datetime

import customtkinter as ctk

import src.presentacion.themes as T
from src.presentacion.forms import NO_SERIAL, ClientForm, DiagnosticView, EquipmentForm
from src.presentacion.widgets import DataRow, LiveCustodyTicket, ModernCard, StatusPill

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NAV_MODULES = [
    ("pbi01", "PBI-01 | Registro Cliente"),
    ("pbi02", "PBI-02 | Ingreso Equipos"),
    ("diag", "Diagnóstico Técnico (CU13)"),
    ("parts", "Control Repuestos (CU24)"),
    ("cash", "Entrega y Caja (CU17)"),
]

PLACEHOLDERS = {
    "parts": (
        "Control de Repuestos (CU24)",
        "Inventario de componentes, reservas y órdenes de compra.",
        [("SKU activos", "1 248"), ("Bajo stock mínimo", "12"), ("Reservados hoy", "5")],
    ),
    "cash": (
        "Entrega y Caja (CU17)",
        "Cobro, entrega de equipos y emisión de comprobantes.",
        [("Listos para entrega", "4"), ("Cobros del día", "S/ 2 340"), ("Órdenes cerradas", "7")],
    ),
}


class ModuleView(ctk.CTkFrame):
    """Vista de referencia para módulos administrativos complementarios."""

    def __init__(self, master, title, description, kpis):
        super().__init__(master, fg_color=T.CANVAS, corner_radius=0)
        self.columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self, text=title, anchor="w", font=T.font(18, "bold"), text_color=T.TEXT
        ).grid(row=0, column=0, sticky="w", padx=T.OUTER_PAD, pady=(T.OUTER_PAD, 0))
        ctk.CTkLabel(
            self, text=description, anchor="w", font=T.font(11), text_color=T.TEXT_MUTED
        ).grid(row=1, column=0, sticky="w", padx=T.OUTER_PAD, pady=(0, T.OUTER_PAD))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=T.OUTER_PAD)
        row.columnconfigure((0, 1, 2), weight=1, uniform="k")
        for i, (cap, val) in enumerate(kpis):
            card = ModernCard(row)
            card.grid(row=0, column=i, sticky="nsew", padx=(0, 5) if i == 0 else (5, 0) if i == 2 else 5)
            ctk.CTkLabel(card.body, text=val, anchor="w", font=T.font(24, "bold"), text_color=T.ACCENT).pack(anchor="w")
            ctk.CTkLabel(card.body, text=cap.upper(), anchor="w", font=T.font(9, "bold"), text_color=T.TEXT_MUTED).pack(anchor="w")

        info = ModernCard(self, "Módulo Integrado SmartFix", "Sincronización activa con laboratorio Cusco")
        info.grid(row=3, column=0, sticky="ew", padx=T.OUTER_PAD, pady=T.OUTER_PAD)
        ctk.CTkLabel(
            info.body, text="Operando en red local de ACDC Electronics — Wanchaq, Cusco.",
            anchor="w", font=T.font(12), text_color=T.TEXT_MUTED
        ).pack(anchor="w")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=T.CANVAS)
        self.title("ACDC Electronics Lab · SmartFix")
        self.geometry("1600x900")
        self.minsize(1240, 720)

        # ── Estado compartido ───────────────────────────────────────────
        self.order_seq = 89
        self.printed = False
        self.issued_at = None
        self.equipos = 14
        self.en_meson = 3
        self.capacity = 20

        self.client = {
            "name": "Carlos Mendoza Quispe",
            "doc": "72849102",
            "phone": "984 512 309",
            "client_type": T.CLIENT_TYPES[0],
        }
        self.serials = {
            "SOLE0092114": "#TALLER-2026-088",
            "LG20458831": "#TALLER-2026-086",
            "SN-1049-A": "#TALLER-2026-084",
        }
        self.orders = [
            {
                "code": "#TALLER-2026-088",
                "client": "Rosa Huamán",
                "equipment": "Sole SOL10L / GN",
                "time": "10:32",
                "status": "EN MESA",
                "fault": "No enciende el piloto ni calienta el agua al abrir la llave.",
                "diagnosis": "",
                "labor": 60.0,
                "part_name": "Sensor / Termostato",
                "checks": ["Fuente de poder"],
            },
            {
                "code": "#TALLER-2026-087",
                "client": "Jorge Condori",
                "equipment": "LG Lavadora 12 Kg",
                "time": "11:05",
                "status": "DIAGNÓSTICO",
                "fault": "Muestra error OE y no desagua al terminar ciclo.",
                "diagnosis": "Bomba / Electroválvula obstruida con bobina abierta.",
                "labor": 65.0,
                "part_name": "Bomba / Electroválvula",
                "checks": ["Fuente de poder", "Sensores"],
            },
            {
                "code": "#TALLER-2026-086",
                "client": "Marleny Quispe",
                "equipment": 'Samsung Smart TV 50"',
                "time": "11:48",
                "status": "COTIZADO",
                "fault": "Tiene audio normal pero sin imagen en pantalla.",
                "diagnosis": "Fuente de poder sin salida de voltaje hacia backlights.",
                "labor": 80.0,
                "part_name": "Fuente de poder",
                "checks": ["Fuente de poder", "Placa principal"],
            },
            {
                "code": "#TALLER-2026-085",
                "client": "Edwin Salas",
                "equipment": "Sony Equipo de Sonido",
                "time": "12:20",
                "status": "LISTO",
                "fault": "Se apaga solo tras unos minutos de uso.",
                "diagnosis": "Capacitores hinchados o con fuga en etapa amplificadora.",
                "labor": 70.0,
                "part_name": "Capacitores (kit)",
                "checks": list(T.CHECKLIST),
            },
        ]

        # ── Grid de 3 columnas ──────────────────────────────────────────
        self.columnconfigure(0, weight=0, minsize=T.SIDEBAR_W)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=0, minsize=T.RIGHT_W + T.OUTER_PAD)
        self.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_center()
        self._build_right()

        self.show_view("pbi01")
        self._render_metrics()
        self._render_recent()
        self._refresh_ticket()
        self._tick()
        self.after(100, self._maximize)

    def _maximize(self):
        try:
            self.state("zoomed")
        except Exception: # noqa: BLE001
            try:
                self.attributes("-zoomed", True)
            except Exception: # noqa: BLE001, S110
                pass

    def _tick(self):
        now = datetime.now()
        self.lbl_clock.configure(text=now.strftime("%d/%m/%Y  •  %H:%M:%S"))
        if not self.printed:
            self.ticket.update_clock(now)
        self.after(1000, self._tick)

    # ── Columna 1: Sidebar ──────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(
            self, width=T.SIDEBAR_W, fg_color=T.CARD,
            border_color=T.BORDER, border_width=1, corner_radius=0
        )
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.columnconfigure(0, weight=1)
        sb.rowconfigure(4, weight=1)

        logo = ctk.CTkFrame(sb, fg_color="transparent")
        logo.grid(row=0, column=0, sticky="ew", padx=T.INNER_PADX, pady=(20, 12))
        ctk.CTkLabel(
            logo, text="ACDC", anchor="w", font=T.font(34, "bold"), text_color=T.ACCENT
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo, text="ELECTRONICS LAB • CUSCO", anchor="w",
            font=T.font(10, "bold"), text_color=T.TEXT_MUTED
        ).pack(anchor="w")

        server = ctk.CTkFrame(
            sb, fg_color=T.INPUT_BG, border_color=T.BORDER_STRONG,
            border_width=T.BORDER_W, corner_radius=T.RADIUS
        )
        server.grid(row=1, column=0, sticky="ew", padx=T.OUTER_PAD, pady=(0, 16))
        server.columnconfigure(1, weight=1)
        ctk.CTkLabel(
            server, text="●", text_color=T.SUCCESS, font=T.font(16)
        ).grid(row=0, column=0, rowspan=2, padx=(12, 6), pady=8)
        ctk.CTkLabel(
            server, text="Gateway en Línea v4.8.2", anchor="w",
            font=T.font(11, "bold"), text_color=T.TEXT
        ).grid(row=0, column=1, sticky="w", pady=(8, 0))
        ctk.CTkLabel(
            server, text="Sync SmartFix Activo", anchor="w",
            font=T.font(10), text_color=T.TEXT_MUTED
        ).grid(row=1, column=1, sticky="w", pady=(0, 8))

        ctk.CTkLabel(
            sb, text="MÓDULOS", anchor="w", font=T.font(10, "bold"), text_color=T.TEXT_MUTED
        ).grid(row=2, column=0, sticky="ew", padx=T.INNER_PADX, pady=(0, 6))

        nav = ctk.CTkFrame(sb, fg_color="transparent")
        nav.grid(row=3, column=0, sticky="ew", padx=T.OUTER_PAD)
        nav.columnconfigure(0, weight=1)
        self.nav_buttons = {}
        for i, (key, label) in enumerate(NAV_MODULES):
            btn = ctk.CTkButton(
                nav, text=label, anchor="w", height=40, corner_radius=T.RADIUS_SM,
                font=T.font(12, "bold"), command=lambda k=key: self.show_view(k)
            )
            btn.grid(row=i, column=0, sticky="ew", pady=3)
            self.nav_buttons[key] = btn

        shift = ctk.CTkFrame(
            sb, fg_color=T.INPUT_BG, border_color=T.BORDER_STRONG,
            border_width=T.BORDER_W, corner_radius=T.RADIUS
        )
        shift.grid(row=5, column=0, sticky="ew", padx=T.OUTER_PAD, pady=T.OUTER_PAD)
        ctk.CTkLabel(
            shift, text="TURNO ACTIVO", anchor="w", font=T.font(9, "bold"), text_color=T.TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(10, 0))
        ctk.CTkLabel(
            shift, text="Mesa Técnica 01 • Wanchaq", anchor="w",
            font=T.font(11, "bold"), text_color=T.TEXT
        ).pack(anchor="w", padx=12)
        ctk.CTkLabel(
            shift, text=f"Horario: {T.COMPANY_HOURS}", anchor="w",
            font=T.font(10), text_color=T.SUCCESS
        ).pack(anchor="w", padx=12, pady=(0, 10))

    def _style_nav(self, active):
        for key, btn in self.nav_buttons.items():
            if key == active:
                btn.configure(fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER, text_color=T.TEXT)
            else:
                btn.configure(fg_color="transparent", hover_color=T.PANEL, text_color=T.TEXT_MUTED)

    # ── Columna 2: TopBar Global + Vistas Centrales ─────────────────────
    def _build_center(self):
        self.center = ctk.CTkFrame(self, fg_color=T.CANVAS, corner_radius=0)
        self.center.grid(row=0, column=1, sticky="nsew")
        self.center.columnconfigure(0, weight=1)
        self.center.rowconfigure(1, weight=1)

        # Header Global moderno
        topbar = ctk.CTkFrame(
            self.center, height=52, fg_color=T.CARD,
            border_color=T.BORDER, border_width=1, corner_radius=0
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.columnconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(
            topbar, height=34, width=320,
            placeholder_text="Buscar orden (#TALLER...), cliente o equipo...",
            fg_color=T.INPUT_BG, border_color=T.BORDER_STRONG, border_width=1,
            corner_radius=T.RADIUS_PILL, text_color=T.TEXT,
            placeholder_text_color=T.TEXT_DIM, font=T.font(11)
        )
        self.search_entry.grid(row=0, column=0, padx=T.OUTER_PAD, pady=9, sticky="w")
        self.search_entry.bind("<Return>", self._quick_search)

        self.lbl_clock = ctk.CTkLabel(
            topbar, text="", anchor="e", font=T.font(11, "bold", mono=True), text_color=T.TEXT_MUTED
        )
        self.lbl_clock.grid(row=0, column=2, padx=(8, 12), pady=9, sticky="e")

        StatusPill(topbar, "CUSCO · SEDE CENTRAL", "info", size=9).grid(
            row=0, column=3, padx=(0, T.OUTER_PAD), pady=9, sticky="e"
        )

        # Contenedor de vistas
        body = ctk.CTkFrame(self.center, fg_color=T.CANVAS, corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self.views = {
            "pbi01": ClientForm(body, on_register=self._on_client_registered),
            "pbi02": EquipmentForm(
                body,
                on_change=self._refresh_ticket,
                on_generate=self._on_generate,
                on_new_equipment=self._on_new_equipment,
                on_change_client=lambda: self.show_view("pbi01"),
                serial_lookup=self._serial_owner,
            ),
            "diag": DiagnosticView(
                body,
                get_orders=lambda: self.orders,
                on_update_order=self._on_update_order,
            ),
        }
        for key, (title, desc, kpis) in PLACEHOLDERS.items():
            self.views[key] = ModuleView(body, title, desc, kpis)

        for v in self.views.values():
            v.grid(row=0, column=0, sticky="nsew")
            v.grid_remove()
        self.current = None

    def _quick_search(self, _event=None):
        q = self.search_entry.get().strip().lower()
        if not q:
            return
        match = next(
            (o for o in self.orders if q in o["code"].lower() or q in o["client"].lower() or q in o["equipment"].lower()),
            None
        )
        if match:
            self.show_view("diag")
            self.views["diag"].refresh_orders(select_code=match["code"])

    def show_view(self, key):
        if self.current:
            self.views[self.current].grid_remove()
        self.views[key].grid()
        self.current = key
        self._style_nav(key)
        if key == "diag":
            self.views["diag"].refresh_orders()

    # ── Columna 3: Panel Derecho ────────────────────────────────────────
    def _build_right(self):
        right = ctk.CTkFrame(self, width=T.RIGHT_W, fg_color=T.CANVAS, corner_radius=0)
        right.grid(row=0, column=2, sticky="nsew", padx=(0, T.OUTER_PAD))
        right.grid_propagate(False)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        m = ModernCard(right, "Métricas de Recepción", "Turno actual")
        m.grid(row=0, column=0, sticky="ew", pady=T.OUTER_PAD)
        mb = m.body
        mb.columnconfigure((0, 1), weight=1)

        self.lbl_equipos = ctk.CTkLabel(mb, text="", anchor="w", font=T.font(24, "bold"), text_color=T.ACCENT)
        self.lbl_equipos.grid(row=0, column=0, sticky="w")
        self.lbl_meson = ctk.CTkLabel(mb, text="", anchor="e", font=T.font(24, "bold"), text_color=T.WARNING)
        self.lbl_meson.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(mb, text="INGRESADOS EN EL TURNO", anchor="w", font=T.font(9, "bold"), text_color=T.TEXT_MUTED).grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(mb, text="EN MESÓN", anchor="e", font=T.font(9, "bold"), text_color=T.TEXT_MUTED).grid(row=1, column=1, sticky="e")

        self.progress = ctk.CTkProgressBar(
            mb, height=8, fg_color=T.INPUT_BG, progress_color=T.ACCENT, corner_radius=4
        )
        self.progress.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 4))
        self.lbl_capacity = ctk.CTkLabel(mb, text="", anchor="w", font=T.font(10), text_color=T.TEXT_MUTED)
        self.lbl_capacity.grid(row=3, column=0, columnspan=2, sticky="w")

        recent = ModernCard(right, "Últimos Registrados", "Clic para abrir en Diagnóstico CU13")
        recent.grid(row=1, column=0, sticky="ew", pady=(0, T.OUTER_PAD))
        self.recent_body = recent.body
        self.recent_body.columnconfigure(0, weight=1)

        self.ticket = LiveCustodyTicket(right)
        self.ticket.grid(row=2, column=0, sticky="nsew", pady=(0, T.OUTER_PAD))

    def _render_metrics(self):
        self.lbl_equipos.configure(text=f"{self.equipos} Equipos")
        self.lbl_meson.configure(text=f"{self.en_meson} En Mesón")
        ratio = min(self.equipos / self.capacity, 1.0)
        self.progress.set(ratio)
        self.progress.configure(progress_color=T.WARNING if ratio >= 0.9 else T.ACCENT)
        self.lbl_capacity.configure(
            text=f"Capacidad diaria del taller: {int(ratio * 100)}%  ({self.equipos}/{self.capacity})"
        )

    def _render_recent(self):
        for w in self.recent_body.winfo_children():
            w.destroy()
        for i, order in enumerate(self.orders[:4]):
            code = order["code"]
            row = DataRow(self.recent_body, on_click=lambda c=code: self._open_in_diag(c), edge=T.BORDER)
            row.grid(row=i, column=0, sticky="ew", pady=3)
            row.columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row, text=order["client"], anchor="w", font=T.font(11, "bold"), text_color=T.TEXT
            ).grid(row=0, column=0, sticky="w", padx=10, pady=(6, 0))

            ctk.CTkLabel(
                row, text=f"{order['equipment']}  ·  {order['time']}", anchor="w",
                font=T.font(10), text_color=T.TEXT_MUTED
            ).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 6))

            StatusPill(
                row, order["status"], T.STATUS_KIND.get(order["status"], "neutral"),
                dot=False, size=9
            ).grid(row=0, column=1, rowspan=2, padx=10)
            row.finalize()

    def _open_in_diag(self, code):
        self.show_view("diag")
        self.views["diag"].refresh_orders(select_code=code)

    # ── Lógica compartida entre vistas ──────────────────────────────────
    @property
    def order_code(self):
        return f"#TALLER-2026-{self.order_seq:03d}"

    def _serial_owner(self, serial):
        owner = self.serials.get(serial)
        return owner if owner and owner != self.order_code else None

    def _refresh_ticket(self):
        form = self.views["pbi02"]
        form.set_order_code(self.order_code)
        when = self.issued_at if self.printed and self.issued_at else datetime.now()
        status = "EMITIDO" if self.printed else "BORRADOR"
        self.ticket.render(self.order_code, self.client, form.get_data(), self.printed, when, status)

    def _advance_order_if_printed(self):
        if self.printed:
            self.order_seq += 1
            self.printed = False
            self.issued_at = None

    def _on_client_registered(self, data):
        self._advance_order_if_printed()
        self.client = {
            "name": data["name"],
            "doc": data["doc"],
            "phone": data["phone"],
            "client_type": data["client_type"],
        }
        form = self.views["pbi02"]
        form.set_client(self.client)
        form.reset_equipment()
        self._refresh_ticket()
        self.show_view("pbi02")

    def _on_new_equipment(self):
        self._advance_order_if_printed()
        self.views["pbi02"].reset_equipment()
        self._refresh_ticket()

    def _on_generate(self, equipment):
        code = self.order_code
        self.serials = {s: o for s, o in self.serials.items() if o != code}
        if equipment["serial"] and equipment["serial"] not in NO_SERIAL:
            self.serials[equipment["serial"]] = code

        if not self.printed:
            self.printed = True
            self.issued_at = datetime.now()
            self.equipos += 1
            self.en_meson += 1
            label = f"{equipment['brand']} {equipment['model']}".strip()
            self.orders.insert(0, {
                "code": code,
                "client": self.client["name"],
                "equipment": label,
                "time": self.issued_at.strftime("%H:%M"),
                "status": "EN MESA",
                "fault": equipment["fault"],
                "diagnosis": "",
                "labor": 60.0,
                "part_name": "",
                "checks": [],
            })
            self._render_metrics()
            self._render_recent()
            self.views["diag"].refresh_orders(select_code=code)

        self._refresh_ticket()
        self.ticket.flash()

    def _on_update_order(self, code, **updates):
        for order in self.orders:
            if order["code"] == code:
                order.update(updates)
                break
        self._render_recent()
        self.views["diag"].refresh_orders(select_code=code)


if __name__ == "__main__":
    MainWindow().mainloop()