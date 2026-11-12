"""widgets.py - Componentes reutilizables de ACDC Electronics Lab."""
import textwrap
from datetime import datetime

import customtkinter as ctk
import theme as T


def _is_ctk(widget):
    return any(c.__module__.startswith("customtkinter") for c in type(widget).__mro__)


# ════════════════════════════════════════════════════════════════════════
class ModernCard(ctk.CTkFrame):
    """Tarjeta elevada (level='card') o sub-panel (level='panel').
    Contenido en `.body`; widgets del encabezado en `.header_right`."""

    def __init__(self, master, title=None, subtitle=None, accent=False, level="card", **kw):
        panel = level == "panel"
        kw.setdefault("fg_color", T.PANEL if panel else T.CARD)
        kw.setdefault("border_color", T.ACCENT if accent else
                      (T.BORDER_STRONG if panel else T.BORDER))
        kw.setdefault("border_width", T.BORDER_W)
        kw.setdefault("corner_radius", T.RADIUS_SM if panel else T.RADIUS)
        super().__init__(master, **kw)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.header = None
        self.header_right = None
        if title:
            self.header = ctk.CTkFrame(self, fg_color="transparent")
            self.header.grid(row=0, column=0, sticky="ew", padx=T.INNER_PADX,
                             pady=(T.INNER_PADY, 0))
            self.header.columnconfigure(1, weight=1)
            ctk.CTkFrame(self.header, width=3, height=14, corner_radius=2,
                         fg_color=T.ACCENT).grid(row=0, column=0, padx=(0, 8))
            ctk.CTkLabel(self.header, text=title.upper(), anchor="w",
                         font=T.font(11, "bold"), text_color=T.TEXT
                         ).grid(row=0, column=1, sticky="w")
            self.header_right = ctk.CTkFrame(self.header, fg_color="transparent",
                                             width=0, height=0)
            self.header_right.grid(row=0, column=2, rowspan=2, sticky="e")
            if subtitle:
                ctk.CTkLabel(self.header, text=subtitle, anchor="w", justify="left",
                             wraplength=520, font=T.font(10), text_color=T.TEXT_MUTED
                             ).grid(row=1, column=1, sticky="w")
            ctk.CTkFrame(self, height=1, fg_color=T.BORDER, corner_radius=0
                         ).grid(row=1, column=0, sticky="ew", padx=T.INNER_PADX, pady=(10, 0))
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=2, column=0, sticky="nsew", padx=T.INNER_PADX,
                       pady=(12 if title else T.INNER_PADY, T.INNER_PADY))


# ════════════════════════════════════════════════════════════════════════
class InputField(ctk.CTkFrame):
    """Campo con label en mayúsculas, foco cian, estados y slot `.extra` inferior.
    Si se pasan `values` se comporta como ComboBox (editable o de solo lectura)."""

    def __init__(self, master, label, placeholder="", mono=False, values=None,
                 editable=False, initial=None):
        super().__init__(master, fg_color="transparent")
        self.columnconfigure(0, weight=1)
        self._callbacks = []
        self._state = "neutral"
        self._focused = False
        self._combo = bool(values)
        ctk.CTkLabel(self, text=label.upper(), anchor="w", font=T.font(10, "bold"),
                     text_color=T.TEXT_MUTED).grid(row=0, column=0, sticky="ew")
        if self._combo:
            self.entry = ctk.CTkComboBox(
                self, values=values, height=38, state="normal" if editable else "readonly",
                fg_color=T.INPUT_BG, border_color=T.BORDER_STRONG, border_width=1,
                button_color=T.PANEL, button_hover_color=T.ACCENT,
                dropdown_fg_color=T.PANEL, dropdown_hover_color=T.ACCENT_SOFT,
                dropdown_text_color=T.TEXT, text_color=T.TEXT,
                corner_radius=T.RADIUS_SM, font=T.font(12, mono=mono),
                dropdown_font=T.font(12), command=lambda _v: self._fire())
            self.entry.set(values[0] if initial is None else initial)
        else:
            self.entry = ctk.CTkEntry(
                self, placeholder_text=placeholder, height=38, fg_color=T.INPUT_BG,
                border_color=T.BORDER_STRONG, border_width=1, corner_radius=T.RADIUS_SM,
                text_color=T.TEXT, placeholder_text_color=T.TEXT_DIM,
                font=T.font(12, mono=mono))
        self.entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.hint = ctk.CTkLabel(self, text=" ", anchor="w", font=T.font(10),
                                 text_color=T.TEXT_DIM)
        self.hint.grid(row=2, column=0, sticky="ew")
        self.extra = ctk.CTkFrame(self, fg_color="transparent", width=0, height=0)
        self.extra.grid(row=3, column=0, sticky="w")
        self.entry.bind("<KeyRelease>", lambda _e: self._fire(), add=True)
        self.entry.bind("<FocusIn>", lambda _e: self._focus(True), add=True)
        self.entry.bind("<FocusOut>", lambda _e: self._focus(False), add=True)

    def _fire(self):
        for cb in self._callbacks:
            cb()

    def _focus(self, on):
        self._focused = on
        self._paint()

    def _paint(self):
        color = {"error": T.DANGER, "ok": T.SUCCESS, "warn": T.WARNING}.get(self._state)
        if color is None:
            color = T.ACCENT if self._focused else T.BORDER_STRONG
        self.entry.configure(border_color=color)

    def bind_change(self, callback):
        self._callbacks.append(callback)

    def get(self):
        return self.entry.get()

    def set(self, value):
        if self._combo:
            self.entry.set(value)
        else:
            self.entry.delete(0, "end")
            self.entry.insert(0, value)

    def clear(self):
        self.set("")

    def set_state(self, state="neutral", message=""):
        """state: neutral | ok | warn | error."""
        self._state = state
        txt = {"error": T.DANGER, "ok": T.SUCCESS, "warn": T.WARNING}.get(state, T.TEXT_DIM)
        self.hint.configure(text=message or " ", text_color=txt)
        self._paint()


class TextAreaField(ctk.CTkFrame):
    """Label + CTkTextbox estilizado con foco cian y contador opcional."""

    def __init__(self, master, label, height=90, limit=None):
        super().__init__(master, fg_color="transparent")
        self.columnconfigure(0, weight=1)
        self.limit = limit
        self._callbacks = []
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text=label.upper(), anchor="w", font=T.font(10, "bold"),
                     text_color=T.TEXT_MUTED).grid(row=0, column=0, sticky="w")
        self.counter = ctk.CTkLabel(top, text="", font=T.font(10, "bold", mono=True),
                                    text_color=T.ACCENT)
        self.counter.grid(row=0, column=1, sticky="e")
        self.box = ctk.CTkTextbox(
            self, height=height, fg_color=T.INPUT_BG, border_color=T.BORDER_STRONG,
            border_width=1, corner_radius=T.RADIUS_SM, text_color=T.TEXT,
            font=T.font(12), wrap="word", scrollbar_button_color=T.BORDER_STRONG,
            scrollbar_button_hover_color=T.TEXT_MUTED)
        self.box.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.box.bind("<KeyRelease>", self._on_key, add=True)
        self.box.bind("<FocusIn>", lambda _e: self.box.configure(border_color=T.ACCENT), add=True)
        self.box.bind("<FocusOut>", lambda _e: self.box.configure(border_color=T.BORDER_STRONG),
                      add=True)
        self._update_counter()

    def _update_counter(self):
        if self.limit:
            n = len(self.get())
            self.counter.configure(text=f"{n} / {self.limit}",
                                   text_color=T.WARNING if n > self.limit * 0.9 else T.ACCENT)

    def _on_key(self, _e=None):
        if self.limit:
            text = self.box.get("1.0", "end-1c")
            if len(text) > self.limit:
                self.box.delete("1.0", "end")
                self.box.insert("1.0", text[:self.limit])
        self._update_counter()
        for cb in self._callbacks:
            cb()

    def bind_change(self, callback):
        self._callbacks.append(callback)

    def get(self):
        return self.box.get("1.0", "end-1c").strip()

    def set(self, text):
        self.box.delete("1.0", "end")
        self.box.insert("1.0", text)
        self._update_counter()


# ════════════════════════════════════════════════════════════════════════
class StatusPill(ctk.CTkFrame):
    """Pill de estado con borde suave. kind: success|danger|warning|info|quote|neutral."""

    def __init__(self, master, text="", kind="neutral", dot=True, size=10, **kw):
        bg, fg = T.BADGE_STYLES[kind]
        super().__init__(master, fg_color=bg, border_color=fg, border_width=1,
                         corner_radius=T.RADIUS_PILL, **kw)
        self._dot = dot
        self.label = ctk.CTkLabel(self, text="", text_color=fg, font=T.font(size, "bold"))
        self.label.pack(padx=10, pady=2)
        self.set(text, kind)

    def set(self, text, kind="neutral"):
        bg, fg = T.BADGE_STYLES[kind]
        self.configure(fg_color=bg, border_color=fg)
        self.label.configure(text=(("● " if self._dot else "") + text), text_color=fg)


# ════════════════════════════════════════════════════════════════════════
class Chip(ctk.CTkButton):
    """Píldora interactiva (hover + estado activo). kind: default | suggest."""

    def __init__(self, master, text, command, kind="default"):
        self._kind = kind
        self._plain = text
        super().__init__(master, text=text, width=int(len(text) * 6.6 + 28), height=26,
                         corner_radius=13, font=T.font(11), border_width=1, command=command)
        self.set_active(False)

    def set_active(self, active, text=None):
        if self._kind == "suggest":
            self.configure(fg_color=T.SUCCESS_SOFT, border_color=T.SUCCESS,
                           text_color=T.SUCCESS, hover_color=T.SUCCESS_SOFT_HOVER)
        elif active:
            self.configure(fg_color=T.ACCENT_SOFT, border_color=T.ACCENT,
                           text_color=T.ACCENT, hover_color=T.ACCENT_SOFT)
        else:
            self.configure(fg_color=T.PANEL, border_color=T.BORDER_STRONG,
                           text_color=T.TEXT_MUTED, hover_color=T.ACCENT_SOFT)
        if text is not None:
            self.configure(text=text)


class QuickChipBar(ctk.CTkFrame):
    """Barra de chips con salto de línea automático. `on_pick(snippet)` al pulsar;
    `sync(texto)` marca como activos los chips cuyo texto ya está en el campo."""

    def __init__(self, master, chips, on_pick, caption="AUTOCOMPLETAR RÁPIDO"):
        super().__init__(master, fg_color="transparent")
        self.columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=caption, anchor="w", font=T.font(9, "bold"),
                     text_color=T.TEXT_DIM).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.flow = ctk.CTkFrame(self, fg_color="transparent", width=0, height=0)
        self.flow.grid(row=1, column=0, sticky="ew")
        self._items = []
        self._last_width = 0
        for label, snippet in chips:
            chip = Chip(self.flow, f"+ {label}", lambda s=snippet: on_pick(s))
            self._items.append((chip, label, snippet))
        self.flow.bind("<Configure>", self._reflow)
        self.after(80, self._reflow)

    def _reflow(self, _e=None):
        width = self.flow.winfo_width()
        if width < 60 or width == self._last_width:
            return
        self._last_width = width
        for chip, _l, _s in self._items:
            chip.grid_forget()
        x = row = col = 0
        for chip, _l, _s in self._items:
            w = chip.winfo_reqwidth() + 6
            if col > 0 and x + w > width:
                row += 1
                col = x = 0
            chip.grid(row=row, column=col, padx=(0, 6), pady=(0, 6), sticky="w")
            x += w
            col += 1

    def sync(self, text):
        low = (text or "").lower()
        for chip, label, snippet in self._items:
            active = snippet.lower() in low
            chip.set_active(active, ("✓ " if active else "+ ") + label)


# ════════════════════════════════════════════════════════════════════════
class ValidationBanner(ctk.CTkFrame):
    """Banner de validación: rojo (errores), ámbar (espera) o verde (listo).
    Botones de acción en `.actions`."""

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=T.DANGER_SOFT, border_color=T.DANGER,
                         border_width=T.BORDER_W, corner_radius=T.RADIUS, **kw)
        self.columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(self, text="", anchor="w", font=T.font(12, "bold"),
                                        text_color=T.DANGER)
        self.title_label.grid(row=0, column=0, sticky="ew", padx=T.INNER_PADX,
                              pady=(T.INNER_PADY, 4))
        self.message_label = ctk.CTkLabel(self, text="", anchor="w", justify="left",
                                          font=T.font(11), text_color=T.TEXT, wraplength=520)
        self.message_label.grid(row=1, column=0, sticky="ew", padx=T.INNER_PADX)
        self.actions = ctk.CTkFrame(self, fg_color="transparent", width=0, height=0)
        self.actions.grid(row=2, column=0, sticky="ew", padx=T.INNER_PADX,
                          pady=(8, T.INNER_PADY))
        self.bind("<Configure>", self._rewrap)

    def _rewrap(self, event):
        self.message_label.configure(wraplength=max(180, event.width - 2 * T.INNER_PADX))

    def _apply(self, bg, border, color, title, message):
        self.configure(fg_color=bg, border_color=border)
        self.title_label.configure(text=title, text_color=color)
        self.message_label.configure(text=message)

    def show_errors(self, errors):
        self._apply(T.DANGER_SOFT, T.DANGER, T.DANGER, f"ERROR DE VALIDACIÓN  ({len(errors)})",
                    "\n".join(f"⚠  {e}" for e in errors))

    def show_waiting(self, message, title="◌  EN ESPERA DE DATOS"):
        self._apply(T.WARNING_SOFT, T.WARNING, T.WARNING, title, message)

    def show_ok(self, message, title="✔  VALIDACIÓN CORRECTA"):
        self._apply(T.SUCCESS_SOFT, T.SUCCESS, T.SUCCESS, title, message)


# ════════════════════════════════════════════════════════════════════════
class DataRow(ctk.CTkFrame):
    """Fila interactiva con hover y selección. Llamar a `finalize()` tras añadir hijos."""

    def __init__(self, master, on_click=None, edge=T.CARD):
        super().__init__(master, fg_color="transparent", corner_radius=T.RADIUS_SM,
                         border_width=1, border_color=edge)
        self._edge = edge
        self._on_click = on_click
        self._hover = False
        self._selected = False

    def finalize(self):
        self._bind_tree(self)

    def _bind_tree(self, widget):
        widget.bind("<Enter>", self._enter, add=True)
        widget.bind("<Leave>", self._leave, add=True)
        widget.bind("<Button-1>", self._click, add=True)
        for child in widget.winfo_children():
            if _is_ctk(child):
                self._bind_tree(child)

    def _enter(self, _e=None):
        self._hover = True
        self._paint()

    def _leave(self, _e=None):
        try:
            x, y = self.winfo_pointerxy()
            under = self.winfo_containing(x, y)
            if under is not None and str(under).startswith(str(self)):
                return
        except Exception:  # noqa: BLE001, S110
            pass
        self._hover = False
        self._paint()

    def _click(self, _e=None):
        if self._on_click:
            self._on_click()

    def set_selected(self, selected):
        self._selected = selected
        self._paint()

    def _paint(self):
        if self._selected:
            self.configure(fg_color=T.ROW_SELECTED, border_color=T.ACCENT)
        elif self._hover:
            self.configure(fg_color=T.ROW_HOVER, border_color=T.BORDER_STRONG)
        else:
            self.configure(fg_color="transparent", border_color=self._edge)


# ════════════════════════════════════════════════════════════════════════
class LiveCustodyTicket(ctk.CTkFrame):
    """Comprobante térmico de custodia (Consolas) que se redibuja en vivo."""

    WIDTH = 34

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=T.CARD, border_color=T.BORDER,
                         border_width=T.BORDER_W, corner_radius=T.RADIUS, **kw)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._date_line = None
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=T.INNER_PADX, pady=(T.INNER_PADY, 8))
        head.columnconfigure(1, weight=1)
        ctk.CTkFrame(head, width=3, height=14, corner_radius=2, fg_color=T.ACCENT
                     ).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkLabel(head, text="COMPROBANTE DE CUSTODIA", anchor="w",
                     font=T.font(11, "bold"), text_color=T.TEXT
                     ).grid(row=0, column=1, sticky="w")
        StatusPill(head, "EN VIVO", "success").grid(row=0, column=2, sticky="e")
        self.text = ctk.CTkTextbox(
            self, fg_color=T.PAPER, text_color=T.PAPER_TEXT, font=T.font(10, mono=True),
            corner_radius=T.RADIUS_SM, border_width=0, wrap="word",
            scrollbar_button_color=T.BORDER_STRONG, scrollbar_button_hover_color=T.TEXT_MUTED)
        self.text.grid(row=1, column=0, sticky="nsew", padx=T.INNER_PADX,
                       pady=(0, T.INNER_PADY))
        try:
            self.text._textbox.tag_configure("bold", font=(T.FONT_MONO, 10, "bold"))
        except Exception: # noqa: BLE001, S110
            pass
        self.text.configure(state="disabled")

    @staticmethod
    def _stamp(when):
        return when.strftime("%d/%m/%Y %H:%M:%S")

    def render(self, order, client, equipment, printed=False, when=None, status="BORRADOR"):
        W = self.WIDTH
        when = when or datetime.now()
        out = []

        def add(t="", bold=False):
            out.append((t, bold))

        def center(t, bold=False):
            add(t.center(W), bold)

        def kv(label, value, bold=False, lw=7):
            value = (value or "").strip() or "........"
            lines = textwrap.wrap(value, W - lw - 2) or [""]
            add(f"{label:<{lw}}: {lines[0]}", bold)
            for ln in lines[1:]:
                add(f"{'':<{lw + 2}}{ln}", bold)

        def block(text):
            text = (text or "").strip()
            for ln in (textwrap.wrap(text, W) if text else ["........"]):
                add(ln)

        eq, dv = "=" * W, "-" * W
        add(eq)
        center(T.COMPANY_NAME, True)
        center("Servicio Técnico Especializado")
        center(T.COMPANY_ADDRESS)
        center("Wanchaq - Cusco")
        center(f"RUC: {T.COMPANY_RUC}")
        center(f"Tel: {T.COMPANY_TEL}")
        center(f"Atención: {T.COMPANY_HOURS} hrs")
        add(eq)
        center("COMPROBANTE DE CUSTODIA", True)
        center("ORDEN DE SERVICIO")
        add(eq)
        kv("ORDEN", order, bold=True)
        self._date_line = len(out) + 1
        kv("FECHA", self._stamp(when))
        kv("ESTADO", status)
        add(dv)
        add("TITULAR", True)
        kv("Nombre", client.get("name", ""))
        kv("Doc.", client.get("doc", ""))
        kv("Tel.", client.get("phone", ""))
        add(dv)
        add("EQUIPO RECEPCIONADO", True)
        kv("Tipo", equipment.get("category", ""))
        kv("Marca", equipment.get("brand", ""))
        kv("Modelo", equipment.get("model", ""))
        kv("S/N", equipment.get("serial", ""))
        add(dv)
        add("ESTADO FISICO / DAÑOS PREVIOS", True)
        block(equipment.get("condition", ""))
        add(dv)
        add("FALLA REPORTADA", True)
        block(equipment.get("fault", ""))
        add(dv)
        add("ACCESORIOS EN CUSTODIA", True)
        accessories = equipment.get("accessories") or []
        if accessories:
            for a in accessories:
                for ln in textwrap.wrap(f"[X] {a}", W, subsequent_indent="    "):
                    add(ln)
        else:
            add("(ninguno declarado)")
        add(dv)
        dest = "REPARACIÓN" if equipment.get("destination") == T.DESTINATIONS[0] \
            else "EVAL. RAEE / RECICLAJE"
        kv("DESTINO", dest)
        add(dv)
        add("CONFORMIDAD DEL CLIENTE", True)
        add("")
        add("")
        add("_" * 24)
        add((client.get("name", "") or "FIRMA / DNI")[:W])
        add("FIRMA DIGITALIZADA")
        add(dv)
        block("El cliente declara conformidad con el estado físico y los accesorios "
              "descritos en este comprobante.")
        block("Garantía de reparación según política vigente de ACDC.")
        add(eq)
        center("** ORDEN EMITIDA **" if printed else "-- BORRADOR / SIN EMITIR --", True)
        center("Conserve este comprobante")
        center("para el retiro del equipo")
        add(eq)

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        for i, (t, bold) in enumerate(out):
            self.text.insert("end", t + ("\n" if i < len(out) - 1 else ""),
                             "bold" if bold else None)
        self.text.configure(state="disabled")
        self.scroll_top()

    def scroll_top(self):
        self.text.yview("moveto", 0)

    def update_clock(self, when):
        """Actualiza solo la línea de fecha/hora (sin redibujar ni mover el scroll)."""
        if not self._date_line:
            return
        ln = self._date_line
        self.text.configure(state="normal")
        self.text.delete(f"{ln}.0", f"{ln}.end")
        self.text.insert(f"{ln}.0", f"{'FECHA':<7}: {self._stamp(when)}")
        self.text.configure(state="disabled")

    def flash(self):
        self.configure(border_color=T.SUCCESS, border_width=2)
        self.after(900, lambda: self.configure(border_color=T.BORDER, border_width=T.BORDER_W))