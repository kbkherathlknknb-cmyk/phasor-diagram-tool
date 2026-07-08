"""
Phasor Diagram Tool — Electrical Engineering
=============================================
A formal, professional-grade GUI application for constructing
and analysing phasor diagrams used in AC circuit analysis.

Enter magnitude and angle (degrees) in float format.
Full colour customisation is supported.

Dependencies: Python 3.8+, numpy, matplotlib (TkAgg backend)
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import numpy as np
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyArrowPatch
import math
import time

# ───────────────────────── Formal Colour Scheme ─────────────────────────
# Professional dark palette — subdued, legible, engineering-grade
BG_PRIMARY      = "#1b1f2b"
BG_SECONDARY    = "#232838"
BG_TERTIARY     = "#2b3044"
BG_INPUT        = "#1e2233"
ACCENT_BLUE     = "#4a90d9"
ACCENT_BLUE_H   = "#5fa3ec"
TEXT_WHITE       = "#dce0ea"
TEXT_DIM         = "#8890a4"
TEXT_MUTED       = "#5c6478"
BORDER           = "#353b50"
BORDER_FOCUS     = "#4a90d9"
DANGER           = "#c0392b"
SUCCESS          = "#27ae60"

# Diagram defaults
DIAGRAM_BG      = "#f5f6fa"
DIAGRAM_GRID    = "#d0d4de"
DIAGRAM_AXIS    = "#7f8694"
DIAGRAM_LABEL   = "#2c3e50"

# Default phasor colours (professional, distinct on light background)
PHASOR_COLORS = [
    "#2c3e50",  # dark navy
    "#c0392b",  # engineering red
    "#2980b9",  # steel blue
    "#27ae60",  # green
    "#8e44ad",  # purple
    "#d35400",  # orange
    "#16a085",  # teal
    "#f39c12",  # amber
    "#2c3e50",  # charcoal
    "#e74c3c",  # bright red
]


# ═══════════════════════════════════════════════════════════════════════
#  DATA MODEL
# ═══════════════════════════════════════════════════════════════════════
# Line style constants
LINE_STYLES = ["Solid", "Dotted", "Dashed"]
LINE_STYLE_MAP = {
    "Solid":  "-",
    "Dotted": (0, (2, 3)),
    "Dashed": (0, (6, 4)),
}


class Phasor:
    """Single phasor: magnitude, angle (degrees), colour, label, line style."""

    _counter = 0

    def __init__(self, magnitude: float, angle_deg: float,
                 color: str = None, label: str = None,
                 line_style: str = "Solid", start_from: int | None = None):
        Phasor._counter += 1
        self.id = Phasor._counter
        self.magnitude = magnitude
        self.angle_deg = angle_deg
        self.color = color or PHASOR_COLORS[(self.id - 1) % len(PHASOR_COLORS)]
        self.label = label or f"E{self.id}"
        self.line_style = line_style if line_style in LINE_STYLES else "Solid"
        self.start_from: int | None = start_from  # None = origin, else phasor ID

    @property
    def angle_rad(self):
        return math.radians(self.angle_deg)

    @property
    def x(self):
        return self.magnitude * math.cos(self.angle_rad)

    @property
    def y(self):
        return self.magnitude * math.sin(self.angle_rad)

    @property
    def mpl_linestyle(self):
        return LINE_STYLE_MAP.get(self.line_style, "-")

    def polar_str(self):
        return f"{self.magnitude:.2f} ∠ {self.angle_deg:.1f}°"

    def rect_str(self):
        sign = "+" if self.y >= 0 else "−"
        return f"{self.x:.2f} {sign} j{abs(self.y):.2f}"


# ═══════════════════════════════════════════════════════════════════════
#  APPLICATION
# ═══════════════════════════════════════════════════════════════════════
class PhasorDiagramApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Phasor Diagram Tool — Electrical Engineering")
        self.root.configure(bg=BG_PRIMARY)
        self.root.minsize(1280, 740)

        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1440x860")

        self.phasors: list[Phasor] = []
        self._editing_id: int | None = None  # phasor ID being edited, or None

        # Diagram appearance (user-editable)
        self.diagram_bg    = DIAGRAM_BG
        self.diagram_grid  = DIAGRAM_GRID
        self.diagram_axis  = DIAGRAM_AXIS
        self.diagram_label = DIAGRAM_LABEL

        self.show_grid        = tk.BooleanVar(value=True)
        self.show_labels      = tk.BooleanVar(value=True)
        self.show_angle_arcs  = tk.BooleanVar(value=True)
        self.show_projections = tk.BooleanVar(value=False)
        self.show_components  = tk.BooleanVar(value=False)


        self._build_styles()
        self._build_menu_bar()
        self._build_toolbar()
        self._build_main_layout()
        self._build_status_bar()
        self._draw_diagram()

    # ─────────────────────── Styles ───────────────────────
    def _build_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("Main.TFrame",   background=BG_PRIMARY)
        s.configure("Panel.TFrame",  background=BG_SECONDARY)
        s.configure("Card.TFrame",   background=BG_TERTIARY)
        s.configure("Sep.TFrame",    background=BORDER)

        s.configure("Panel.TLabel",  background=BG_SECONDARY, foreground=TEXT_WHITE,
                    font=("Segoe UI", 10))
        s.configure("PanelDim.TLabel", background=BG_SECONDARY, foreground=TEXT_DIM,
                    font=("Segoe UI", 9))
        s.configure("Section.TLabel", background=BG_SECONDARY, foreground=TEXT_DIM,
                    font=("Segoe UI", 8, "bold"))
        s.configure("Card.TLabel",   background=BG_TERTIARY, foreground=TEXT_WHITE,
                    font=("Segoe UI", 9))
        s.configure("CardDim.TLabel", background=BG_TERTIARY, foreground=TEXT_DIM,
                    font=("Segoe UI", 8))
        s.configure("Status.TLabel", background=BG_PRIMARY, foreground=TEXT_DIM,
                    font=("Segoe UI", 8))
        s.configure("Toolbar.TLabel", background=BG_SECONDARY, foreground=TEXT_DIM,
                    font=("Segoe UI", 9))

        s.configure("Accent.TButton", background=ACCENT_BLUE, foreground="white",
                    font=("Segoe UI", 9), padding=(14, 6), borderwidth=0)
        s.map("Accent.TButton",
              background=[("active", ACCENT_BLUE_H), ("pressed", ACCENT_BLUE)])

        s.configure("Flat.TButton", background=BG_TERTIARY, foreground=TEXT_WHITE,
                    font=("Segoe UI", 9), padding=(10, 5), borderwidth=0)
        s.map("Flat.TButton",
              background=[("active", BORDER)])

        s.configure("Toolbar.TButton", background=BG_SECONDARY, foreground=TEXT_WHITE,
                    font=("Segoe UI", 9), padding=(10, 4), borderwidth=0)
        s.map("Toolbar.TButton",
              background=[("active", BG_TERTIARY)])

        s.configure("Danger.TButton", background=DANGER, foreground="white",
                    font=("Segoe UI", 9), padding=(10, 5), borderwidth=0)
        s.map("Danger.TButton",
              background=[("active", "#a93226")])

        s.configure("Panel.TCheckbutton", background=BG_SECONDARY, foreground=TEXT_WHITE,
                    font=("Segoe UI", 9))
        s.map("Panel.TCheckbutton", background=[("active", BG_SECONDARY)])

        s.configure("Diagram.TLabelframe",       background=BG_PRIMARY, foreground=TEXT_DIM,
                    font=("Segoe UI", 9))
        s.configure("Diagram.TLabelframe.Label",  background=BG_PRIMARY, foreground=TEXT_DIM,
                    font=("Segoe UI", 9))

    # ─────────────────────── Menu Bar ───────────────────────
    def _build_menu_bar(self):
        menubar = tk.Menu(self.root, bg=BG_SECONDARY, fg=TEXT_WHITE,
                         activebackground=ACCENT_BLUE, activeforeground="white",
                         font=("Segoe UI", 9), relief="flat", bd=0)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=BG_TERTIARY, fg=TEXT_WHITE,
                           activebackground=ACCENT_BLUE, activeforeground="white",
                           font=("Segoe UI", 9), bd=0)
        file_menu.add_command(label="Save Image…", command=self._save_image, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=BG_TERTIARY, fg=TEXT_WHITE,
                           activebackground=ACCENT_BLUE, activeforeground="white",
                           font=("Segoe UI", 9), bd=0)
        edit_menu.add_command(label="Clear All Phasors", command=self._clear_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=BG_TERTIARY, fg=TEXT_WHITE,
                           activebackground=ACCENT_BLUE, activeforeground="white",
                           font=("Segoe UI", 9), bd=0)
        view_menu.add_checkbutton(label="Grid", variable=self.show_grid, command=self._draw_diagram)
        view_menu.add_checkbutton(label="Labels", variable=self.show_labels, command=self._draw_diagram)
        view_menu.add_checkbutton(label="Angle Arcs", variable=self.show_angle_arcs, command=self._draw_diagram)
        view_menu.add_checkbutton(label="Axis Projections", variable=self.show_projections, command=self._draw_diagram)
        view_menu.add_checkbutton(label="Component Values", variable=self.show_components, command=self._draw_diagram)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)

        # Keyboard shortcut
        self.root.bind("<Control-s>", lambda e: self._save_image())

    # ─────────────────────── Toolbar ───────────────────────
    def _build_toolbar(self):
        tb = ttk.Frame(self.root, style="Panel.TFrame")
        tb.pack(fill=tk.X, side=tk.TOP)

        inner = ttk.Frame(tb, style="Panel.TFrame")
        inner.pack(fill=tk.X, padx=8, pady=(4, 4))

        ttk.Button(inner, text="Save Image", style="Toolbar.TButton",
                   command=self._save_image).pack(side=tk.LEFT, padx=(0, 4))

        # Separator
        ttk.Frame(inner, style="Sep.TFrame", width=1).pack(
            side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

        ttk.Button(inner, text="Clear All", style="Toolbar.TButton",
                   command=self._clear_all).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Frame(inner, style="Sep.TFrame", width=1).pack(
            side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

        # View toggles in toolbar
        ttk.Checkbutton(inner, text="Grid", variable=self.show_grid,
                        style="Panel.TCheckbutton",
                        command=self._draw_diagram).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(inner, text="Labels", variable=self.show_labels,
                        style="Panel.TCheckbutton",
                        command=self._draw_diagram).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(inner, text="Arcs", variable=self.show_angle_arcs,
                        style="Panel.TCheckbutton",
                        command=self._draw_diagram).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(inner, text="Projections", variable=self.show_projections,
                        style="Panel.TCheckbutton",
                        command=self._draw_diagram).pack(side=tk.LEFT, padx=4)


        # Bottom border
        ttk.Frame(self.root, style="Sep.TFrame", height=1).pack(fill=tk.X, side=tk.TOP)

    # ─────────────────────── Main Layout ───────────────────────
    def _build_main_layout(self):
        self.main = ttk.Frame(self.root, style="Main.TFrame")
        self.main.pack(fill=tk.BOTH, expand=True)

        # ── Left Panel (inputs & list) ── width fixed at 380
        self.left_panel = ttk.Frame(self.main, style="Panel.TFrame", width=390)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.left_panel.pack_propagate(False)

        self._build_input_panel()

        # ── Vertical separator ──
        ttk.Frame(self.main, style="Sep.TFrame", width=1).pack(side=tk.LEFT, fill=tk.Y)

        # ── Right: Diagram ──
        self.right_frame = ttk.Frame(self.main, style="Main.TFrame")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._build_diagram_panel()

    def _build_input_panel(self):
        container = self.left_panel

        # Scrollable interior
        canvas = tk.Canvas(container, bg=BG_SECONDARY, highlightthickness=0, bd=0)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas, style="Panel.TFrame")

        self.inner.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw", width=370)
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        def _wheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
        canvas.bind_all("<MouseWheel>", _wheel)

        p = self.inner

        # ── Section: Input ──
        self._heading(p, "PHASOR INPUT")
        input_frame = self._card(p)

        # Form fields in a grid
        fields = tk.Frame(input_frame, bg=BG_TERTIARY)
        fields.pack(fill=tk.X)

        # Row 0 — Label
        tk.Label(fields, text="Label:", bg=BG_TERTIARY, fg=TEXT_DIM,
                 font=("Segoe UI", 9), anchor="w").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 6))
        self.entry_label = self._entry(fields, width=22)
        self.entry_label.grid(row=0, column=1, sticky="ew", pady=(0, 6))
        self.entry_label.insert(0, f"E{Phasor._counter + 1}")

        # Row 1 — Magnitude
        tk.Label(fields, text="Magnitude:", bg=BG_TERTIARY, fg=TEXT_DIM,
                 font=("Segoe UI", 9), anchor="w").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 6))
        self.entry_mag = self._entry(fields, width=22)
        self.entry_mag.grid(row=1, column=1, sticky="ew", pady=(0, 6))

        # Row 2 — Angle
        tk.Label(fields, text="Angle (deg):", bg=BG_TERTIARY, fg=TEXT_DIM,
                 font=("Segoe UI", 9), anchor="w").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 6))
        self.entry_angle = self._entry(fields, width=22)
        self.entry_angle.grid(row=2, column=1, sticky="ew", pady=(0, 6))

        # Row 3 — Line Style
        tk.Label(fields, text="Line Style:", bg=BG_TERTIARY, fg=TEXT_DIM,
                 font=("Segoe UI", 9), anchor="w").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=(0, 6))
        self.line_style_var = tk.StringVar(value="Solid")
        style_frame = tk.Frame(fields, bg=BG_TERTIARY)
        style_frame.grid(row=3, column=1, sticky="w", pady=(0, 6))
        for ls in LINE_STYLES:
            tk.Radiobutton(
                style_frame, text=ls, variable=self.line_style_var, value=ls,
                bg=BG_TERTIARY, fg=TEXT_WHITE, selectcolor=BG_INPUT,
                activebackground=BG_TERTIARY, activeforeground=TEXT_WHITE,
                font=("Segoe UI", 8), indicatoron=1, bd=0,
                highlightthickness=0
            ).pack(side=tk.LEFT, padx=(0, 8))

        # Row 4 — Start From
        tk.Label(fields, text="Start From:", bg=BG_TERTIARY, fg=TEXT_DIM,
                 font=("Segoe UI", 9), anchor="w").grid(
            row=4, column=0, sticky="w", padx=(0, 10), pady=(0, 6))
        self.start_from_var = tk.StringVar(value="Origin")
        self.start_from_frame = tk.Frame(fields, bg=BG_TERTIARY)
        self.start_from_frame.grid(row=4, column=1, sticky="ew", pady=(0, 6))
        self._rebuild_start_from_dropdown()

        # Row 5 — Colour
        tk.Label(fields, text="Colour:", bg=BG_TERTIARY, fg=TEXT_DIM,
                 font=("Segoe UI", 9), anchor="w").grid(
            row=5, column=0, sticky="w", padx=(0, 10), pady=(0, 4))
        color_frame = tk.Frame(fields, bg=BG_TERTIARY)
        color_frame.grid(row=5, column=1, sticky="w", pady=(0, 4))

        self.new_color = PHASOR_COLORS[Phasor._counter % len(PHASOR_COLORS)]
        self.color_swatch = tk.Canvas(
            color_frame, width=22, height=22, bg=self.new_color,
            highlightthickness=1, highlightbackground=BORDER, cursor="hand2")
        self.color_swatch.pack(side=tk.LEFT)
        self.color_swatch.bind("<Button-1>", self._pick_new_color)

        self.color_hex_label = tk.Label(
            color_frame, text=self.new_color, bg=BG_TERTIARY, fg=TEXT_DIM,
            font=("Consolas", 9))
        self.color_hex_label.pack(side=tk.LEFT, padx=(8, 0))

        fields.columnconfigure(1, weight=1)

        # Button row
        self.btn_row = tk.Frame(input_frame, bg=BG_TERTIARY)
        self.btn_row.pack(fill=tk.X, pady=(12, 0))
        self.add_btn = ttk.Button(self.btn_row, text="Add Phasor",
                                  style="Accent.TButton",
                                  command=self._add_phasor)
        self.add_btn.pack(fill=tk.X)

        # ── Keyboard navigation ──
        # Ordered list of input fields for arrow-key cycling
        self._input_fields = [self.entry_label, self.entry_mag, self.entry_angle]

        for idx, field in enumerate(self._input_fields):
            field.bind("<Down>", lambda e, i=idx: self._focus_field((i + 1) % 3))
            field.bind("<Up>",   lambda e, i=idx: self._focus_field((i - 1) % 3))
            field.bind("<Return>", lambda e: self._add_phasor())
            # Tab already moves forward natively; bind Shift-Tab for reverse
            field.bind("<Shift-Tab>", lambda e, i=idx: self._focus_field((i - 1) % 3))

        # ── Section: Phasor Table ──
        self._heading(p, "PHASOR TABLE")
        self.table_frame = ttk.Frame(p, style="Panel.TFrame")
        self.table_frame.pack(fill=tk.X, padx=12, pady=(0, 6))
        self._refresh_table()

        # ── Section: Diagram Colours ──
        self._heading(p, "DIAGRAM COLOURS")
        colors_card = self._card(p)

        for label_text, attr_name in [
            ("Background",  "diagram_bg"),
            ("Grid Lines",  "diagram_grid"),
            ("Axes",        "diagram_axis"),
            ("Text Labels", "diagram_label"),
        ]:
            row = tk.Frame(colors_card, bg=BG_TERTIARY)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label_text, bg=BG_TERTIARY, fg=TEXT_DIM,
                     font=("Segoe UI", 9), anchor="w").pack(side=tk.LEFT)
            swatch = tk.Canvas(
                row, width=20, height=20, bg=getattr(self, attr_name),
                highlightthickness=1, highlightbackground=BORDER, cursor="hand2")
            swatch.pack(side=tk.RIGHT)
            hex_lbl = tk.Label(row, text=getattr(self, attr_name), bg=BG_TERTIARY,
                              fg=TEXT_MUTED, font=("Consolas", 8))
            hex_lbl.pack(side=tk.RIGHT, padx=(0, 8))
            swatch.bind("<Button-1>",
                        lambda e, a=attr_name, s=swatch, h=hex_lbl:
                            self._pick_diagram_color(a, s, h))

    def _focus_field(self, index: int):
        """Move focus to the input field at the given index."""
        self._input_fields[index].focus_set()
        return "break"  # prevent default handling

    def _build_diagram_panel(self):
        self.fig = plt.Figure(facecolor=self.diagram_bg, dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas_mpl.get_tk_widget().configure(bg=BG_PRIMARY)
        self.canvas_mpl.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # ─────────────────────── Status Bar ───────────────────────
    def _build_status_bar(self):
        ttk.Frame(self.root, style="Sep.TFrame", height=1).pack(fill=tk.X, side=tk.BOTTOM)
        sb = ttk.Frame(self.root, style="Main.TFrame")
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        inner = ttk.Frame(sb, style="Main.TFrame")
        inner.pack(fill=tk.X, padx=10, pady=3)

        self.status_left = ttk.Label(inner, text="Ready", style="Status.TLabel")
        self.status_left.pack(side=tk.LEFT)

        self.status_right = ttk.Label(inner, text="Phasors: 0", style="Status.TLabel")
        self.status_right.pack(side=tk.RIGHT)

    def _update_status(self, msg: str = None):
        count = len(self.phasors)
        self.status_right.config(text=f"Phasors: {count}")
        if msg:
            self.status_left.config(text=msg)

    # ─────────────────────── Widget Helpers ───────────────────────
    def _heading(self, parent, text):
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.pack(fill=tk.X, padx=12, pady=(16, 4))
        ttk.Label(frame, text=text, style="Section.TLabel").pack(side=tk.LEFT)
        # Horizontal rule
        hr = ttk.Frame(frame, style="Sep.TFrame", height=1)
        hr.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), pady=1)

    def _card(self, parent):
        outer = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        outer.pack(fill=tk.X, padx=12, pady=(0, 4))
        inner = tk.Frame(outer, bg=BG_TERTIARY, padx=14, pady=12)
        inner.pack(fill=tk.BOTH)
        return inner

    def _entry(self, parent, width=14):
        return tk.Entry(
            parent, width=width, font=("Consolas", 10),
            bg=BG_INPUT, fg=TEXT_WHITE, insertbackground=ACCENT_BLUE,
            relief="flat", highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=BORDER_FOCUS,
            selectbackground=ACCENT_BLUE, selectforeground="white")

    def _rebuild_start_from_dropdown(self):
        """Rebuild the 'Start From' dropdown with current phasors."""
        for w in self.start_from_frame.winfo_children():
            w.destroy()

        # Build options: Origin + tip of each existing phasor
        choices = ["Origin"]
        # When editing, exclude the phasor being edited from the list
        for p in self.phasors:
            if self._editing_id is not None and p.id == self._editing_id:
                continue
            choices.append(f"Tip of {p.label}")

        # Validate current selection
        if self.start_from_var.get() not in choices:
            self.start_from_var.set("Origin")

        om = tk.OptionMenu(self.start_from_frame, self.start_from_var, *choices)
        om.configure(
            bg=BG_INPUT, fg=TEXT_WHITE, font=("Segoe UI", 9),
            activebackground=ACCENT_BLUE, activeforeground="white",
            highlightthickness=1, highlightbackground=BORDER,
            relief="flat", bd=0)
        om["menu"].configure(
            bg=BG_TERTIARY, fg=TEXT_WHITE, font=("Segoe UI", 9),
            activebackground=ACCENT_BLUE, activeforeground="white", bd=0)
        om.pack(fill=tk.X)

    def _start_from_var_to_id(self) -> int | None:
        """Convert the Start From dropdown value to a phasor ID or None."""
        val = self.start_from_var.get()
        if val == "Origin":
            return None
        # Format: "Tip of E1" — find matching phasor by label
        prefix = "Tip of "
        if val.startswith(prefix):
            label = val[len(prefix):]
            for p in self.phasors:
                if p.label == label:
                    return p.id
        return None

    def _id_to_start_from_var(self, phasor_id: int | None) -> str:
        """Convert a phasor ID (or None) to the dropdown display string."""
        if phasor_id is None:
            return "Origin"
        for p in self.phasors:
            if p.id == phasor_id:
                return f"Tip of {p.label}"
        return "Origin"

    # ─────────────────────── Phasor CRUD ───────────────────────
    def _add_phasor(self):
        # Validate magnitude
        try:
            mag = float(self.entry_mag.get().strip())
        except ValueError:
            messagebox.showwarning("Input Error",
                                   "Magnitude must be a floating-point number.\n"
                                   "Example: 120.0")
            self.entry_mag.focus_set()
            return
        if mag <= 0:
            messagebox.showwarning("Input Error", "Magnitude must be a positive value.")
            self.entry_mag.focus_set()
            return

        # Validate angle
        try:
            angle = float(self.entry_angle.get().strip())
        except ValueError:
            messagebox.showwarning("Input Error",
                                   "Angle must be a floating-point number in degrees.\n"
                                   "Example: 30.0")
            self.entry_angle.focus_set()
            return

        label = self.entry_label.get().strip() or None
        line_style = self.line_style_var.get()
        start_from_id = self._start_from_var_to_id()

        if self._editing_id is not None:
            # ── Update existing phasor ──
            for p in self.phasors:
                if p.id == self._editing_id:
                    p.magnitude = mag
                    p.angle_deg = angle
                    p.color = self.new_color
                    p.line_style = line_style
                    p.start_from = start_from_id
                    if label:
                        p.label = label
                    self._update_status(f"Updated phasor '{p.label}'")
                    break
            self._editing_id = None
            self.add_btn.configure(text="Add Phasor")
        else:
            # ── Add new phasor ──
            p = Phasor(mag, angle, color=self.new_color, label=label,
                       line_style=line_style, start_from=start_from_id)
            self.phasors.append(p)
            self._update_status(f"Added phasor '{p.label}'")

        # Reset inputs
        self.entry_mag.delete(0, tk.END)
        self.entry_angle.delete(0, tk.END)
        self.entry_label.delete(0, tk.END)
        self.entry_label.insert(0, f"E{Phasor._counter + 1}")
        self.line_style_var.set("Solid")
        self.start_from_var.set("Origin")
        self.new_color = PHASOR_COLORS[Phasor._counter % len(PHASOR_COLORS)]
        self.color_swatch.configure(bg=self.new_color)
        self.color_hex_label.configure(text=self.new_color)

        self.entry_mag.focus_set()
        self._rebuild_start_from_dropdown()
        self._refresh_table()
        self._draw_diagram()

    def _select_phasor(self, phasor_id: int):
        """Select a phasor from the table and load its values into the form."""
        target = None
        for p in self.phasors:
            if p.id == phasor_id:
                target = p
                break
        if target is None:
            return

        self._editing_id = phasor_id

        # Populate fields with selected phasor's values
        self.entry_label.delete(0, tk.END)
        self.entry_label.insert(0, target.label)
        self.entry_mag.delete(0, tk.END)
        self.entry_mag.insert(0, str(target.magnitude))
        self.entry_angle.delete(0, tk.END)
        self.entry_angle.insert(0, str(target.angle_deg))
        self.line_style_var.set(target.line_style)
        self._rebuild_start_from_dropdown()
        self.start_from_var.set(self._id_to_start_from_var(target.start_from))
        self.new_color = target.color
        self.color_swatch.configure(bg=self.new_color)
        self.color_hex_label.configure(text=self.new_color)

        # Switch button to "Update" mode
        self.add_btn.configure(text="Update Phasor")

        self._refresh_table()
        self.entry_mag.focus_set()
        self._update_status(f"Selected '{target.label}' for editing")

    def _start_new_phasor(self):
        """Clear the form and switch to Add mode (called by 'Add New Phasor' button)."""
        self._editing_id = None
        self.add_btn.configure(text="Add Phasor")
        self.entry_mag.delete(0, tk.END)
        self.entry_angle.delete(0, tk.END)
        self.entry_label.delete(0, tk.END)
        self.entry_label.insert(0, f"E{Phasor._counter + 1}")
        self.line_style_var.set("Solid")
        self.start_from_var.set("Origin")
        self._rebuild_start_from_dropdown()
        self.new_color = PHASOR_COLORS[Phasor._counter % len(PHASOR_COLORS)]
        self.color_swatch.configure(bg=self.new_color)
        self.color_hex_label.configure(text=self.new_color)
        self._refresh_table()
        self.entry_mag.focus_set()
        self._update_status("Ready to add new phasor")

    def _remove_phasor(self, pid):
        # If we're editing this phasor, switch to add mode
        if self._editing_id == pid:
            self._start_new_phasor()
        # Clear start_from references pointing to the deleted phasor
        for p in self.phasors:
            if p.start_from == pid:
                p.start_from = None
        self.phasors = [p for p in self.phasors if p.id != pid]
        self._rebuild_start_from_dropdown()
        self._refresh_table()
        self._draw_diagram()
        self._update_status("Phasor removed")

    def _edit_phasor_color(self, phasor: Phasor, swatch: tk.Canvas, hex_lbl: tk.Label):
        result = colorchooser.askcolor(
            initialcolor=phasor.color, title=f"Colour — {phasor.label}")
        if result and result[1]:
            phasor.color = result[1]
            swatch.configure(bg=phasor.color)
            hex_lbl.configure(text=phasor.color)
            self._draw_diagram()

    def _refresh_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        if not self.phasors:
            ttk.Label(self.table_frame, text="No phasors defined.",
                      style="PanelDim.TLabel").pack(pady=12, anchor="center")
            return

        # Table header
        hdr = tk.Frame(self.table_frame, bg=BG_TERTIARY)
        hdr.pack(fill=tk.X)
        for col, w in [("", 4), ("Label", 6), ("Polar", 13), ("Rectangular", 14), ("", 3)]:
            tk.Label(hdr, text=col, bg=BG_TERTIARY, fg=TEXT_MUTED,
                     font=("Segoe UI", 8, "bold"), width=w,
                     anchor="w").pack(side=tk.LEFT, padx=2, pady=(4, 2))

        # Separator below header
        tk.Frame(self.table_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, 1))

        # Rows — click a row to select it for editing
        for i, p in enumerate(self.phasors):
            is_selected = (self._editing_id == p.id)
            bg = BG_SECONDARY if i % 2 == 0 else BG_TERTIARY
            row_bg = "#2a3552" if is_selected else bg
            row = tk.Frame(self.table_frame, bg=row_bg, cursor="hand2")
            row.pack(fill=tk.X)

            # Colour swatch
            swatch = tk.Canvas(row, width=14, height=14, bg=p.color,
                              highlightthickness=1, highlightbackground=BORDER)
            swatch.pack(side=tk.LEFT, padx=(8, 4), pady=4)

            # Selection indicator
            if is_selected:
                tk.Label(row, text=">", bg=row_bg, fg=ACCENT_BLUE,
                         font=("Consolas", 9, "bold")).pack(side=tk.LEFT, padx=(0, 2))

            # Label
            lbl = tk.Label(row, text=p.label, bg=row_bg, fg=TEXT_WHITE,
                     font=("Segoe UI", 9, "bold" if is_selected else "normal"),
                     width=6, anchor="w")
            lbl.pack(side=tk.LEFT, padx=2, pady=2)

            # Polar
            polar_lbl = tk.Label(row, text=p.polar_str(), bg=row_bg, fg=TEXT_WHITE,
                     font=("Consolas", 8), width=13, anchor="w")
            polar_lbl.pack(side=tk.LEFT, padx=2, pady=2)

            # Start-from indicator
            if p.start_from is not None:
                src_label = "?"
                for other in self.phasors:
                    if other.id == p.start_from:
                        src_label = other.label
                        break
                from_text = f">{src_label}"
            else:
                from_text = ">O"
            from_lbl = tk.Label(row, text=from_text, bg=row_bg, fg=TEXT_MUTED,
                     font=("Consolas", 7), width=4, anchor="w")
            from_lbl.pack(side=tk.LEFT, padx=1, pady=2)

            # Line style indicator
            style_char = {"Solid": "\u2500", "Dotted": "\u2504", "Dashed": "\u2508"}
            style_lbl = tk.Label(row, text=style_char.get(p.line_style, "\u2500"),
                     bg=row_bg, fg=TEXT_DIM, font=("Consolas", 9), width=2, anchor="center")
            style_lbl.pack(side=tk.LEFT, padx=1, pady=2)

            # Delete button (right side)
            del_btn = tk.Button(
                row, text="X", bg=row_bg, fg=DANGER,
                font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
                activebackground=row_bg, activeforeground="#a93226", bd=0,
                width=3,
                command=lambda pid=p.id: self._remove_phasor(pid)
            )
            del_btn.pack(side=tk.RIGHT, padx=(0, 6), pady=2)

            # Bind click on the row and all child labels to select this phasor
            def _bind_click(widget, pid=p.id):
                widget.bind("<Button-1>", lambda e, _pid=pid: self._select_phasor(_pid))

            _bind_click(row)
            _bind_click(swatch)
            _bind_click(lbl)
            _bind_click(polar_lbl)
            _bind_click(from_lbl)
            _bind_click(style_lbl)

        # ── "Add New Phasor" button at the bottom of the table ──
        tk.Frame(self.table_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=(4, 0))
        tk.Button(
            self.table_frame, text="+ Add New Phasor",
            bg=BG_TERTIARY, fg=ACCENT_BLUE,
            font=("Segoe UI", 9), relief="flat", cursor="hand2",
            activebackground=BG_SECONDARY, activeforeground=ACCENT_BLUE_H,
            bd=0, pady=6,
            command=self._start_new_phasor
        ).pack(fill=tk.X, pady=(2, 4))

    # ─────────────────────── Colour Pickers ───────────────────────
    def _pick_new_color(self, event):
        result = colorchooser.askcolor(
            initialcolor=self.new_color, title="Phasor Colour")
        if result and result[1]:
            self.new_color = result[1]
            self.color_swatch.configure(bg=self.new_color)
            self.color_hex_label.configure(text=self.new_color)

    def _pick_diagram_color(self, attr_name, swatch, hex_lbl):
        current = getattr(self, attr_name)
        result = colorchooser.askcolor(initialcolor=current, title="Diagram Colour")
        if result and result[1]:
            setattr(self, attr_name, result[1])
            swatch.configure(bg=result[1])
            hex_lbl.configure(text=result[1])
            self._draw_diagram()

    # ═══════════════════════════════════════════════════════════════
    #  LABEL COLLISION AVOIDANCE
    # ═══════════════════════════════════════════════════════════════
    @staticmethod
    def _resolve_label_positions(phasors, limit, show_components: bool):
        """Compute non-overlapping label positions for all phasors.

        Returns a list of (lx, ly) tuples, one per phasor in order.
        Uses iterative repulsion to push apart labels whose bounding
        boxes would overlap.
        """
        if not phasors:
            return []

        # Estimate label bounding-box half-sizes in data coordinates.
        # A single-line label is roughly 6 chars wide × 1 line tall;
        # with component text it doubles in height.
        char_w = limit * 0.045       # approximate half-width per char
        line_h = limit * 0.04        # approximate half-height per line

        positions = []
        sizes = []  # (half_w, half_h) for each label

        for p in phasors:
            # Initial placement: 12 % beyond the tip, along the phasor angle
            offset_r = p.magnitude * 1.12
            lx = offset_r * math.cos(p.angle_rad)
            ly = offset_r * math.sin(p.angle_rad)
            positions.append([lx, ly])

            n_chars = len(p.label)
            if show_components:
                polar_len = len(p.polar_str())
                n_chars = max(n_chars, polar_len)
            hw = max(char_w * n_chars * 0.5, limit * 0.06)
            n_lines = 2 if show_components else 1
            hh = line_h * n_lines
            sizes.append((hw, hh))

        # Iterative repulsion (up to 60 passes — converges quickly)
        for _ in range(60):
            moved = False
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    xi, yi = positions[i]
                    xj, yj = positions[j]
                    # Overlap test (axis-aligned bounding boxes)
                    overlap_x = (sizes[i][0] + sizes[j][0]) - abs(xi - xj)
                    overlap_y = (sizes[i][1] + sizes[j][1]) - abs(yi - yj)
                    if overlap_x > 0 and overlap_y > 0:
                        # Push apart along the axis of least overlap
                        dx = xi - xj
                        dy = yi - yj
                        dist = math.hypot(dx, dy)
                        if dist < 1e-9:
                            # Coincident — push along a slightly different angle
                            dx, dy = 1.0, 0.3
                            dist = math.hypot(dx, dy)
                        nudge = max(overlap_x, overlap_y) * 0.55
                        nx = dx / dist * nudge
                        ny = dy / dist * nudge
                        positions[i][0] += nx
                        positions[i][1] += ny
                        positions[j][0] -= nx
                        positions[j][1] -= ny
                        moved = True
            if not moved:
                break

        # Clamp labels inside the visible area with a small margin
        margin = limit * 0.06
        for pos, (hw, hh) in zip(positions, sizes):
            pos[0] = max(-limit + margin + hw, min(limit - margin - hw, pos[0]))
            pos[1] = max(-limit + margin + hh, min(limit - margin - hh, pos[1]))

        return positions

    # ═══════════════════════════════════════════════════════════════
    #  DIAGRAM RENDERING
    # ═══════════════════════════════════════════════════════════════
    def _compute_phasor_origin(self, phasor: Phasor) -> tuple[float, float]:
        """Recursively resolve the absolute origin (ox, oy) for a phasor
        based on its start_from setting. Detects cycles."""
        visited = set()
        current = phasor
        ox, oy = 0.0, 0.0
        while current.start_from is not None:
            if current.start_from in visited:
                break  # cycle detected, stop
            visited.add(current.id)
            source = None
            for p in self.phasors:
                if p.id == current.start_from:
                    source = p
                    break
            if source is None:
                break  # referenced phasor deleted
            # Origin of source + source's own displacement = tip of source
            src_ox, src_oy = self._compute_phasor_origin(source)
            ox = src_ox + source.x
            oy = src_oy + source.y
            break  # only one level of reference needed per call
        return (ox, oy)

    def _draw_diagram(self):
        self.ax.clear()
        self.fig.set_facecolor(self.diagram_bg)
        self.ax.set_facecolor(self.diagram_bg)

        if not self.phasors:
            self._draw_empty()
            self.canvas_mpl.draw()
            return

        # Compute per-phasor origins and tips
        origins = []
        tips = []
        for p in self.phasors:
            ox, oy = self._compute_phasor_origin(p)
            origins.append((ox, oy))
            tips.append((ox + p.x, oy + p.y))

        # Determine axis limits from all origins and tips
        all_x = [o[0] for o in origins] + [t[0] for t in tips] + [0]
        all_y = [o[1] for o in origins] + [t[1] for t in tips] + [0]
        max_extent = max(max(abs(v) for v in all_x), max(abs(v) for v in all_y))
        max_mag = max(p.magnitude for p in self.phasors)
        margin = max(max_extent, max_mag) * 0.35
        limit = max(max_extent, max_mag) + margin

        self.ax.set_xlim(-limit, limit)
        self.ax.set_ylim(-limit, limit)
        self.ax.set_aspect("equal")

        # ── Grid ──
        if self.show_grid.get():
            grid_r = max(max_extent, max_mag)
            for r in np.linspace(grid_r * 0.25, grid_r, 4):
                circle = plt.Circle((0, 0), r, fill=False,
                                    edgecolor=self.diagram_grid, linewidth=0.6,
                                    linestyle=(0, (5, 5)), alpha=0.6)
                self.ax.add_patch(circle)

            for deg in range(0, 360, 30):
                rad = math.radians(deg)
                self.ax.plot(
                    [0, limit * math.cos(rad)],
                    [0, limit * math.sin(rad)],
                    color=self.diagram_grid, linewidth=0.4,
                    linestyle=":", alpha=0.4)

        # ── Axes ──
        self.ax.axhline(0, color=self.diagram_axis, linewidth=1.0, alpha=0.7)
        self.ax.axvline(0, color=self.diagram_axis, linewidth=1.0, alpha=0.7)

        self.ax.text(limit * 0.96, -limit * 0.06, "Re", fontsize=9,
                     color=self.diagram_axis, ha="right", fontstyle="italic")
        self.ax.text(limit * 0.06, limit * 0.94, "Im", fontsize=9,
                     color=self.diagram_axis, va="top", fontstyle="italic")

        tick_vals = np.linspace(-limit * 0.8, limit * 0.8, 5)
        tick_vals = tick_vals[tick_vals != 0]
        self.ax.set_xticks(tick_vals)
        self.ax.set_yticks(tick_vals)
        self.ax.tick_params(colors=self.diagram_axis, labelsize=7, length=3, width=0.6)

        # Degree labels on outer ring
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            r = limit * 0.96
            self.ax.text(
                r * math.cos(rad), r * math.sin(rad), f"{deg}\u00b0",
                ha="center", va="center", fontsize=6.5,
                color=self.diagram_axis, alpha=0.55)

        # ── Compute non-overlapping label positions ──
        show_comp = self.show_components.get()
        label_positions = self._resolve_label_positions_with_origins(
            self.phasors, origins, tips, limit, show_comp)

        # ── Draw each phasor ──
        for idx, p in enumerate(self.phasors):
            ox, oy = origins[idx]
            tx, ty = tips[idx]
            lbl_pos = label_positions[idx] if self.show_labels.get() else None
            self._draw_phasor(p, ox, oy, tx, ty, max_mag, limit, lbl_pos, show_comp)

        # Clean up frame
        for spine in self.ax.spines.values():
            spine.set_edgecolor(self.diagram_grid)
            spine.set_linewidth(0.5)

        self.ax.set_xlabel("Real Axis", fontsize=8, color=self.diagram_axis, labelpad=8)
        self.ax.set_ylabel("Imaginary Axis", fontsize=8, color=self.diagram_axis, labelpad=8)

        self.fig.tight_layout(pad=1.5)
        self.canvas_mpl.draw()
        self._update_status()

    @staticmethod
    def _resolve_label_positions_with_origins(phasors, origins, tips, limit, show_components):
        """Compute non-overlapping label positions, accounting for arbitrary origins."""
        if not phasors:
            return []

        char_w = limit * 0.045
        line_h = limit * 0.04

        positions = []
        sizes = []

        for i, p in enumerate(phasors):
            tx, ty = tips[i]
            ox, oy = origins[i]
            # Place label slightly beyond the midpoint, offset outward
            mx = (ox + tx) / 2
            my = (oy + ty) / 2
            # Offset perpendicular to the phasor direction
            angle = p.angle_rad + math.pi / 2
            offset = limit * 0.06
            lx = mx + offset * math.cos(angle)
            ly = my + offset * math.sin(angle)
            positions.append([lx, ly])

            n_chars = len(p.label)
            if show_components:
                n_chars = max(n_chars, len(p.polar_str()))
            hw = max(char_w * n_chars * 0.5, limit * 0.06)
            n_lines = 2 if show_components else 1
            hh = line_h * n_lines
            sizes.append((hw, hh))

        # Iterative repulsion
        for _ in range(60):
            moved = False
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    xi, yi = positions[i]
                    xj, yj = positions[j]
                    overlap_x = (sizes[i][0] + sizes[j][0]) - abs(xi - xj)
                    overlap_y = (sizes[i][1] + sizes[j][1]) - abs(yi - yj)
                    if overlap_x > 0 and overlap_y > 0:
                        dx = xi - xj
                        dy = yi - yj
                        dist = math.hypot(dx, dy)
                        if dist < 1e-9:
                            dx, dy = 1.0, 0.3
                            dist = math.hypot(dx, dy)
                        nudge = max(overlap_x, overlap_y) * 0.55
                        nx = dx / dist * nudge
                        ny = dy / dist * nudge
                        positions[i][0] += nx
                        positions[i][1] += ny
                        positions[j][0] -= nx
                        positions[j][1] -= ny
                        moved = True
            if not moved:
                break

        margin = limit * 0.06
        for pos, (hw, hh) in zip(positions, sizes):
            pos[0] = max(-limit + margin + hw, min(limit - margin - hw, pos[0]))
            pos[1] = max(-limit + margin + hh, min(limit - margin - hh, pos[1]))

        return positions

    def _draw_phasor(self, p: Phasor, ox: float, oy: float,
                     tx: float, ty: float,
                     max_mag: float, limit: float,
                     label_pos: list = None, show_comp: bool = False):
        """Draw a single phasor arrow from (ox,oy) to (tx,ty)."""
        ls = p.mpl_linestyle

        # Main arrow
        arrow = FancyArrowPatch(
            (ox, oy), (tx, ty),
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=2.2,
            color=p.color,
            linestyle=ls,
            zorder=10)
        self.ax.add_patch(arrow)

        # Tip marker
        self.ax.plot(tx, ty, "o", color=p.color, markersize=4, zorder=11)

        # Label
        if label_pos is not None:
            lx, ly = label_pos

            label_text = p.label
            if show_comp:
                label_text += f"\n{p.polar_str()}"

            self.ax.text(
                lx, ly, label_text, ha="center", va="center",
                fontsize=8, fontweight="bold", color=p.color,
                bbox=dict(facecolor=self.diagram_bg, edgecolor=p.color,
                          alpha=0.9, boxstyle="round,pad=0.3", linewidth=0.7),
                zorder=12)

            # Leader line from phasor midpoint to label if displaced
            mid_x = (ox + tx) / 2
            mid_y = (oy + ty) / 2
            disp = math.hypot(lx - mid_x, ly - mid_y)
            if disp > max_mag * 0.18:
                self.ax.plot(
                    [mid_x, lx], [mid_y, ly],
                    color=p.color, linewidth=0.6, linestyle="-",
                    alpha=0.35, zorder=9)

        # Angle arc (drawn at the origin of this phasor)
        if self.show_angle_arcs.get():
            arc_r = min(p.magnitude * 0.22, max_mag * 0.12)
            theta = np.linspace(0, p.angle_rad, 50)
            self.ax.plot(
                ox + arc_r * np.cos(theta), oy + arc_r * np.sin(theta),
                color=p.color, linewidth=1.0, alpha=0.65, zorder=8)
            mid = p.angle_rad / 2
            tr = arc_r * 1.6
            self.ax.text(
                ox + tr * math.cos(mid), oy + tr * math.sin(mid),
                f"{p.angle_deg:.1f}\u00b0", ha="center", va="center",
                fontsize=6.5, color=p.color, alpha=0.75, zorder=9)

        # Projections (only in non-chain mode, from origin)
        if self.show_projections.get() and ox == 0 and oy == 0:
            self.ax.plot([tx, tx], [0, ty], color=p.color,
                        linewidth=0.8, linestyle="--", alpha=0.35, zorder=4)
            self.ax.plot([0, tx], [ty, ty], color=p.color,
                        linewidth=0.8, linestyle="--", alpha=0.35, zorder=4)
            self.ax.plot(tx, 0, "|", color=p.color, markersize=6, alpha=0.4)
            self.ax.plot(0, ty, "_", color=p.color, markersize=6, alpha=0.4)

    def _draw_empty(self):
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect("equal")
        self.ax.axhline(0, color=self.diagram_axis, linewidth=0.6, alpha=0.3)
        self.ax.axvline(0, color=self.diagram_axis, linewidth=0.6, alpha=0.3)
        self.ax.text(0, 0.06, "No phasors defined", ha="center", va="center",
                     fontsize=12, color=self.diagram_axis, alpha=0.4)
        self.ax.text(0, -0.10, "Enter magnitude and angle to begin",
                     ha="center", va="center", fontsize=9,
                     color=self.diagram_axis, alpha=0.3)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    # ─────────────────────── Actions ───────────────────────
    def _save_image(self):
        if not self.phasors:
            messagebox.showinfo("Save Image", "No phasors to save.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg *.jpeg"),
                ("SVG Vector", "*.svg"),
                ("PDF Document", "*.pdf"),
                ("All Files", "*.*"),
            ],
            title="Save Phasor Diagram")
        if path:
            self.fig.savefig(path, dpi=200, facecolor=self.diagram_bg,
                            bbox_inches="tight")
            messagebox.showinfo("Image Saved", f"Diagram saved to:\n{path}")
            self._update_status(f"Saved to {path}")

    def _clear_all(self):
        if not self.phasors:
            return
        if messagebox.askyesno("Confirm", "Remove all phasors from the diagram?"):
            self.phasors.clear()
            Phasor._counter = 0
            self._editing_id = None
            self.add_btn.configure(text="Add Phasor")
            self.entry_label.delete(0, tk.END)
            self.entry_label.insert(0, "E1")
            self.new_color = PHASOR_COLORS[0]
            self.color_swatch.configure(bg=self.new_color)
            self.color_hex_label.configure(text=self.new_color)
            self._refresh_table()
            self._draw_diagram()
            self._update_status("All phasors cleared")


# ═══════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = PhasorDiagramApp(root)
    root.mainloop()
