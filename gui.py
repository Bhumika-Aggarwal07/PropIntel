"""Modern Tkinter interface for the PropIntel academic desktop application.

The UI is redesigned around the existing PropIntel backend:
- database.py
- analysis.py
- matching.py
- comparison.py

No property images are required. Property cards use text and factual attributes.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from analysis import calculate_location_analysis, format_currency
from comparison import build_comparison_rows
from database import DatabaseError, PropertyDatabase
from matching import rank_properties


class PropIntelApp(tk.Tk):
    # -----------------------------
    # Visual design system
    # -----------------------------
    BG = "#F5F7F6"
    SIDEBAR = "#151817"
    SIDEBAR_HOVER = "#202522"
    SIDEBAR_ACTIVE = "#1F2D28"

    CARD = "#FFFFFF"
    BORDER = "#E3E7E5"

    PRIMARY = "#16B981"
    PRIMARY_DARK = "#0F8F68"
    PRIMARY_LIGHT = "#E8F8F2"

    TEXT = "#171A19"
    MUTED = "#6B716D"
    WHITE = "#FFFFFF"

    WARNING = "#F59E0B"
    ERROR = "#D95F59"

    FONT = "Segoe UI"

    def __init__(self):
        super().__init__()

        self.title("PropIntel — Real Estate Intelligence")
        self.geometry("1280x780")
        self.minsize(1050, 680)
        self.configure(bg=self.BG)

        self.database = PropertyDatabase()
        self.current_page = None
        self.nav_buttons = {}

        self._configure_style()
        self._build_shell()
        self.show_dashboard()

    # =========================================================
    # STYLE
    # =========================================================

    def _configure_style(self):
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "TCombobox",
            fieldbackground=self.CARD,
            background=self.CARD,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
            padding=7,
        )

        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.CARD)],
            selectbackground=[("readonly", self.PRIMARY_LIGHT)],
            selectforeground=[("readonly", self.TEXT)],
        )

        style.configure(
            "TEntry",
            fieldbackground=self.CARD,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
            padding=8,
        )

        style.configure(
            "Treeview",
            background=self.CARD,
            fieldbackground=self.CARD,
            foreground=self.TEXT,
            rowheight=34,
            borderwidth=0,
            font=(self.FONT, 9),
        )

        style.configure(
            "Treeview.Heading",
            background="#EEF1EF",
            foreground=self.TEXT,
            font=(self.FONT, 9, "bold"),
            relief="flat",
            padding=9,
        )

        style.map(
            "Treeview",
            background=[("selected", self.PRIMARY_LIGHT)],
            foreground=[("selected", self.TEXT)],
        )

    # =========================================================
    # APP SHELL / SIDEBAR
    # =========================================================

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=self.SIDEBAR, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg=self.BG)
        self.content.pack(side="left", fill="both", expand=True)

        # Brand
        brand = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        brand.pack(fill="x", padx=20, pady=(26, 28))

        logo = tk.Frame(
            brand,
            bg=self.PRIMARY,
            width=38,
            height=38,
        )
        logo.pack(side="left")
        logo.pack_propagate(False)

        tk.Label(
            logo,
            text="P",
            bg=self.PRIMARY,
            fg=self.WHITE,
            font=(self.FONT, 18, "bold"),
        ).pack(expand=True)

        brand_text = tk.Frame(brand, bg=self.SIDEBAR)
        brand_text.pack(side="left", padx=10)

        tk.Label(
            brand_text,
            text="PROPINTEL",
            bg=self.SIDEBAR,
            fg=self.WHITE,
            font=(self.FONT, 13, "bold"),
        ).pack(anchor="w")

        tk.Label(
            brand_text,
            text="Real Estate Intelligence",
            bg=self.SIDEBAR,
            fg="#98A09B",
            font=(self.FONT, 8),
        ).pack(anchor="w", pady=(2, 0))

        # Navigation
        self._add_nav_button("Dashboard", self.show_dashboard, "dashboard")
        self._add_nav_button("Properties", self.show_search, "properties")
        self._add_nav_button("Analytics", self.show_analysis, "analytics")
        self._add_nav_button("Match Properties", self.show_matching, "matching")
        self._add_nav_button("Compare", self.show_comparison, "comparison")

        spacer = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        spacer.pack(fill="both", expand=True)

        separator = tk.Frame(self.sidebar, bg="#2C312E", height=1)
        separator.pack(fill="x", padx=18, pady=(0, 12))

        self._add_nav_button("About PropIntel", self.show_about, "about")
        self._add_nav_button("Exit", self.destroy, "exit", danger=True)

        # Footer
        tk.Label(
            self.sidebar,
            text="Academic Desktop Application",
            bg=self.SIDEBAR,
            fg="#68716C",
            font=(self.FONT, 8),
        ).pack(anchor="w", padx=22, pady=(12, 18))

    def _add_nav_button(self, text, command, key, danger=False):
        button = tk.Button(
            self.sidebar,
            text=f"   {text}",
            command=command,
            anchor="w",
            relief="flat",
            bd=0,
            highlightthickness=0,
            bg=self.SIDEBAR,
            fg="#D8DEDA",
            activebackground=self.SIDEBAR_HOVER,
            activeforeground=self.WHITE,
            font=(self.FONT, 10, "bold" if key == "dashboard" else "normal"),
            cursor="hand2",
            padx=8,
            pady=11,
        )
        button.pack(fill="x", padx=12, pady=2)

        if danger:
            button.configure(fg="#B9C0BC")

        self.nav_buttons[key] = button

    def _set_active_nav(self, key):
        for name, button in self.nav_buttons.items():
            if name == key:
                button.configure(
                    bg=self.SIDEBAR_ACTIVE,
                    fg=self.PRIMARY,
                    font=(self.FONT, 10, "bold"),
                )
            else:
                button.configure(
                    bg=self.SIDEBAR,
                    fg="#D8DEDA",
                    font=(self.FONT, 10, "normal"),
                )

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # =========================================================
    # COMMON UI HELPERS
    # =========================================================

    def _page_header(self, title, subtitle="", nav_key=None):
        self._clear_content()

        if nav_key:
            self._set_active_nav(nav_key)

        header = tk.Frame(self.content, bg=self.BG)
        header.pack(fill="x", padx=34, pady=(28, 20))

        tk.Label(
            header,
            text=title,
            bg=self.BG,
            fg=self.TEXT,
            font=(self.FONT, 24, "bold"),
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                header,
                text=subtitle,
                bg=self.BG,
                fg=self.MUTED,
                font=(self.FONT, 10),
            ).pack(anchor="w", pady=(5, 0))

        return header

    def _card(self, parent, padding=18, **kwargs):
        frame = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
            bd=0,
            **kwargs,
        )
        inner = tk.Frame(frame, bg=self.CARD)
        inner.pack(fill="both", expand=True, padx=padding, pady=padding)
        return frame, inner

    def _section_title(self, parent, title, subtitle=None):
        holder = tk.Frame(parent, bg=self.CARD)
        holder.pack(fill="x", pady=(0, 12))

        tk.Label(
            holder,
            text=title,
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 13, "bold"),
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                holder,
                text=subtitle,
                bg=self.CARD,
                fg=self.MUTED,
                font=(self.FONT, 9),
            ).pack(anchor="w", pady=(3, 0))

        return holder

    def _button(self, parent, text, command, primary=False, width=None):
        kwargs = {
            "text": text,
            "command": command,
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 0,
            "cursor": "hand2",
            "font": (self.FONT, 9, "bold"),
            "padx": 16,
            "pady": 9,
        }

        if width:
            kwargs["width"] = width

        if primary:
            kwargs.update(
                bg=self.PRIMARY,
                fg=self.WHITE,
                activebackground=self.PRIMARY_DARK,
                activeforeground=self.WHITE,
            )
        else:
            kwargs.update(
                bg="#EEF1EF",
                fg=self.TEXT,
                activebackground="#DDE5E1",
                activeforeground=self.TEXT,
            )

        return tk.Button(parent, **kwargs)

    def _label(self, parent, text, size=9, bold=False, color=None, **kwargs):
        return tk.Label(
            parent,
            text=text,
            bg=self.CARD,
            fg=color or self.TEXT,
            font=(self.FONT, size, "bold" if bold else "normal"),
            **kwargs,
        )

    def _entry(self, parent, variable, width=18):
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        return entry

    def _combo(self, parent, variable, values, width=18):
        combo = ttk.Combobox(
            parent,
            textvariable=variable,
            values=values,
            state="readonly",
            width=width,
        )
        return combo

    def _scrollable_frame(self, parent, bg=None):
        bg = bg or self.BG

        canvas = tk.Canvas(
            parent,
            bg=bg,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=canvas.yview,
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        inner = tk.Frame(canvas, bg=bg)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_configure(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def resize_inner(event):
            canvas.itemconfigure(window_id, width=event.width)

        inner.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", resize_inner)

        return canvas, inner

    def _make_tree(self, parent, columns, headings, height=12, selectmode="browse"):
        holder = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )

        tree = ttk.Treeview(
            holder,
            columns=columns,
            show="headings",
            height=height,
            selectmode=selectmode,
        )

        for column, heading in zip(columns, headings):
            tree.heading(column, text=heading)
            tree.column(column, width=130, anchor="center")

        vertical = ttk.Scrollbar(
            holder,
            orient="vertical",
            command=tree.yview,
        )
        horizontal = ttk.Scrollbar(
            holder,
            orient="horizontal",
            command=tree.xview,
        )

        tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )

        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        holder.columnconfigure(0, weight=1)
        holder.rowconfigure(0, weight=1)

        return holder, tree

    def _filter_options(self, column, city=None):
        try:
            return ["All"] + [
                str(value)
                for value in self.database.distinct_values(column, city)
            ]
        except DatabaseError:
            return ["All"]

    @staticmethod
    def _read_number(value, label, integer=False):
        if not value.strip():
            return None

        try:
            parsed = int(value) if integer else float(value)
            if parsed < 0:
                raise ValueError
            return parsed
        except ValueError as exc:
            raise ValueError(
                f"{label} must be a non-negative number."
            ) from exc

    @staticmethod
    def _safe_value(item, key, fallback="Unknown"):
        value = item.get(key)
        if value is None or str(value).strip() == "":
            return fallback
        return value

    # =========================================================
    # DASHBOARD
    # =========================================================

    def show_dashboard(self):
        self._page_header(
            "Dashboard",
            "Explore, compare and analyze residential properties.",
            "dashboard",
        )

        outer = tk.Frame(self.content, bg=self.BG)
        outer.pack(fill="both", expand=True, padx=34, pady=(0, 25))

        # Quick metrics
        metrics = tk.Frame(outer, bg=self.BG)
        metrics.pack(fill="x", pady=(0, 18))

        try:
            all_properties = self.database.search_properties({})
            property_count = len(all_properties)

            cities = {
                str(item.get("city"))
                for item in all_properties
                if item.get("city")
            }

            prices = [
                float(item["price_inr"])
                for item in all_properties
                if item.get("price_inr") is not None
            ]

            avg_price = (
                format_currency(sum(prices) / len(prices))
                if prices
                else "—"
            )

        except DatabaseError:
            all_properties = []
            property_count = "—"
            cities = set()
            avg_price = "—"

        metric_values = [
            ("Properties", f"{property_count:,}" if isinstance(property_count, int) else property_count),
            ("Cities", f"{len(cities):,}"),
            ("Average Price", avg_price),
        ]

        for index, (label, value) in enumerate(metric_values):
            metrics.columnconfigure(index, weight=1)

            card = tk.Frame(
                metrics,
                bg=self.CARD,
                highlightbackground=self.BORDER,
                highlightthickness=1,
            )
            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(0 if index == 0 else 7, 7 if index < 2 else 0),
            )

            tk.Frame(
                card,
                bg=self.PRIMARY,
                width=4,
            ).pack(side="left", fill="y")

            body = tk.Frame(card, bg=self.CARD)
            body.pack(fill="both", expand=True, padx=18, pady=15)

            tk.Label(
                body,
                text=label,
                bg=self.CARD,
                fg=self.MUTED,
                font=(self.FONT, 9),
            ).pack(anchor="w")

            tk.Label(
                body,
                text=value,
                bg=self.CARD,
                fg=self.TEXT,
                font=(self.FONT, 18, "bold"),
            ).pack(anchor="w", pady=(4, 0))

        # Search card
        search_card, search_inner = self._card(outer, padding=20)
        search_card.pack(fill="x", pady=(0, 18))

        tk.Label(
            search_inner,
            text="Quick Search",
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 13, "bold"),
        ).pack(anchor="w")

        tk.Label(
            search_inner,
            text="Start with a city or locality to explore available properties.",
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(anchor="w", pady=(4, 12))

        search_row = tk.Frame(search_inner, bg=self.CARD)
        search_row.pack(fill="x")

        city_var = tk.StringVar(value="All")
        city_box = self._combo(
            search_row,
            city_var,
            self._filter_options("city"),
            width=28,
        )
        city_box.pack(side="left", padx=(0, 10))

        locality_var = tk.StringVar(value="All")
        locality_box = self._combo(
            search_row,
            locality_var,
            self._filter_options("locality"),
            width=28,
        )
        locality_box.pack(side="left", padx=(0, 10))

        def open_search():
            self.show_search(
                preset_city=city_var.get(),
                preset_locality=locality_var.get(),
            )

        self._button(
            search_row,
            "Search Properties",
            open_search,
            primary=True,
        ).pack(side="left")

        def update_localities(_event=None):
            locality_box["values"] = self._filter_options(
                "locality",
                city_var.get() if city_var.get() != "All" else None,
            )
            locality_var.set("All")

        city_box.bind("<<ComboboxSelected>>", update_localities)

        # Recent properties
        recent_card, recent_inner = self._card(outer, padding=20)
        recent_card.pack(fill="both", expand=True)

        self._section_title(
            recent_inner,
            "Recent Properties",
            "A quick view of properties from the dataset.",
        )

        cards_canvas, cards_inner = self._scrollable_frame(
            recent_inner,
            bg=self.CARD,
        )
        cards_canvas.pack(fill="both", expand=True)

        sample = all_properties[:8]

        if not sample:
            tk.Label(
                cards_inner,
                text="No property data available. Import the dataset first.",
                bg=self.CARD,
                fg=self.MUTED,
                font=(self.FONT, 10),
            ).pack(anchor="w", pady=20)
        else:
            for index, item in enumerate(sample):
                self._create_property_card(
                    cards_inner,
                    item,
                    compact=True,
                    row=index // 2,
                    column=index % 2,
                )

            cards_inner.columnconfigure(0, weight=1)
            cards_inner.columnconfigure(1, weight=1)

    # =========================================================
    # PROPERTY SEARCH
    # =========================================================

    def show_search(self, preset_city=None, preset_locality=None):
        self._page_header(
            "Properties",
            "Search and filter the PropIntel property dataset.",
            "properties",
        )

        main = tk.Frame(self.content, bg=self.BG)
        main.pack(fill="both", expand=True, padx=34, pady=(0, 24))

        filter_card, filter_inner = self._card(main, padding=18)
        filter_card.pack(fill="x", pady=(0, 15))

        self._section_title(
            filter_inner,
            "Search Filters",
            "Use as many or as few filters as you need.",
        )

        variables = {}

        fields = [
            ("City", "city", "combo", self._filter_options("city")),
            ("Locality", "locality", "combo", self._filter_options("locality")),
            ("Property Type", "property_type", "combo", self._filter_options("property_type")),
            ("BHK", "bhk", "combo", self._filter_options("bhk")),
            ("Furnishing", "furnishing", "combo", self._filter_options("furnishing")),
            ("Parking", "parking", "combo", self._filter_options("parking")),
            ("Min Price", "min_price", "entry", None),
            ("Max Price", "max_price", "entry", None),
            ("Min Carpet Area", "min_area", "entry", None),
            ("Max Carpet Area", "max_area", "entry", None),
        ]

        form = tk.Frame(filter_inner, bg=self.CARD)
        form.pack(fill="x")

        for index, (label, name, kind, options) in enumerate(fields):
            row, column = divmod(index, 5)

            cell = tk.Frame(form, bg=self.CARD)
            cell.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(0, 10),
                pady=(0, 10),
            )

            tk.Label(
                cell,
                text=label,
                bg=self.CARD,
                fg=self.MUTED,
                font=(self.FONT, 8, "bold"),
            ).pack(anchor="w", pady=(0, 4))

            variable = tk.StringVar(
                value="All" if kind == "combo" else ""
            )
            variables[name] = variable

            if kind == "combo":
                widget = self._combo(
                    cell,
                    variable,
                    options,
                    width=18,
                )
            else:
                widget = self._entry(
                    cell,
                    variable,
                    width=20,
                )

            widget.pack(fill="x")

        for column in range(5):
            form.columnconfigure(column, weight=1)

        if preset_city is not None:
            variables["city"].set(preset_city)

            if preset_city != "All":
                locality_options = self._filter_options(
                    "locality",
                    preset_city,
                )
                locality_widget = None
                for child in form.winfo_children():
                    # Locality widget is recreated below via lookup.
                    pass
                variables["locality"].set(
                    preset_locality if preset_locality in locality_options else "All"
                )

        buttons = tk.Frame(filter_inner, bg=self.CARD)
        buttons.pack(fill="x", pady=(4, 0))

        results_label = tk.StringVar(value="Ready to search")

        tk.Label(
            buttons,
            textvariable=results_label,
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(side="left")

        # Results
        results_card, results_inner = self._card(main, padding=18)
        results_card.pack(fill="both", expand=True)

        top = tk.Frame(results_inner, bg=self.CARD)
        top.pack(fill="x", pady=(0, 12))

        tk.Label(
            top,
            text="Property Results",
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 13, "bold"),
        ).pack(side="left")

        tk.Label(
            top,
            text="Double-click a property to open its details.",
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(side="right")

        results_canvas, results_inner_frame = self._scrollable_frame(
            results_inner,
            bg=self.CARD,
        )
        results_canvas.pack(fill="both", expand=True)

        stored_rows = []

        def clear_results():
            for child in results_inner_frame.winfo_children():
                child.destroy()
            stored_rows.clear()
            results_label.set("Ready to search")

        def display_results(rows):
            clear_results()

            if not rows:
                tk.Label(
                    results_inner_frame,
                    text="No properties matched the selected filters.",
                    bg=self.CARD,
                    fg=self.MUTED,
                    font=(self.FONT, 10),
                ).pack(anchor="w", pady=25)
                results_label.set("0 properties found")
                return

            results_label.set(f"{len(rows):,} properties found")

            for index, item in enumerate(rows):
                stored_rows.append(item)
                self._create_property_card(
                    results_inner_frame,
                    item,
                    compact=False,
                    row=index,
                    column=0,
                )

            results_inner_frame.columnconfigure(0, weight=1)

        def search():
            try:
                filters = {
                    name: variable.get()
                    for name, variable in variables.items()
                }

                for key in (
                    "min_price",
                    "max_price",
                    "min_area",
                    "max_area",
                ):
                    filters[key] = self._read_number(
                        filters[key],
                        key.replace("_", " "),
                    )

                if (
                    filters["min_price"] is not None
                    and filters["max_price"] is not None
                    and filters["min_price"] > filters["max_price"]
                ):
                    raise ValueError(
                        "Minimum price cannot exceed maximum price."
                    )

                if (
                    filters["min_area"] is not None
                    and filters["max_area"] is not None
                    and filters["min_area"] > filters["max_area"]
                ):
                    raise ValueError(
                        "Minimum carpet area cannot exceed maximum area."
                    )

                rows = self.database.search_properties(filters)
                display_results(rows)

            except (ValueError, DatabaseError) as exc:
                messagebox.showerror("Search", str(exc))

        def reset():
            for name, variable in variables.items():
                variable.set("All" if name in {
                    "city",
                    "locality",
                    "property_type",
                    "bhk",
                    "furnishing",
                    "parking",
                } else "")
            clear_results()

        self._button(
            buttons,
            "Search Properties",
            search,
            primary=True,
        ).pack(side="right")

        self._button(
            buttons,
            "Reset",
            reset,
        ).pack(side="right", padx=(0, 8))

        # Connect locality dynamically after widgets exist.
        combo_widgets = []

        def find_combobox(widget):
            if isinstance(widget, ttk.Combobox):
                combo_widgets.append(widget)
            for child in widget.winfo_children():
                find_combobox(child)

        find_combobox(form)

        # Field order means first six widgets are the combo fields.
        if len(combo_widgets) >= 2:
            city_box = combo_widgets[0]
            locality_box = combo_widgets[1]

            def update_locality(_event=None):
                selected_city = variables["city"].get()
                locality_box["values"] = self._filter_options(
                    "locality",
                    selected_city if selected_city != "All" else None,
                )
                variables["locality"].set("All")

            city_box.bind("<<ComboboxSelected>>", update_locality)

        results_canvas.bind_all(
            "<Double-Button-1>",
            lambda event: self._open_selected_card(event, stored_rows),
        )

    def _create_property_card(
        self,
        parent,
        item,
        compact=False,
        row=0,
        column=0,
    ):
        card = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
            cursor="hand2",
        )

        if compact:
            card.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(0, 8 if column == 0 else 0),
                pady=(0, 10),
            )
        else:
            card.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=2,
                pady=6,
            )

        body = tk.Frame(card, bg=self.CARD)
        body.pack(fill="both", expand=True, padx=16, pady=14)

        top = tk.Frame(body, bg=self.CARD)
        top.pack(fill="x")

        property_type = self._safe_value(
            item,
            "property_type",
            "Property",
        )
        bhk = self._safe_value(item, "bhk", "—")
        title = f"{bhk} BHK {property_type}" if str(bhk) not in {"—", "nan"} else str(property_type)

        tk.Label(
            top,
            text=title,
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 11, "bold"),
        ).pack(side="left")

        price = item.get("price_inr")
        price_text = (
            format_currency(float(price))
            if price is not None
            else "Price unavailable"
        )

        tk.Label(
            top,
            text=price_text,
            bg=self.CARD,
            fg=self.PRIMARY_DARK,
            font=(self.FONT, 11, "bold"),
        ).pack(side="right")

        location = (
            f"{self._safe_value(item, 'locality')} • "
            f"{self._safe_value(item, 'city')}"
        )

        tk.Label(
            body,
            text=location,
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(anchor="w", pady=(5, 10))

        info = tk.Frame(body, bg=self.CARD)
        info.pack(fill="x")

        attributes = [
            ("BHK", self._safe_value(item, "bhk", "—")),
            ("Bath", self._safe_value(item, "bathrooms", "—")),
            ("Area", f"{self._safe_value(item, 'carpet_area_sqft', '—')} sqft"),
            ("Furnishing", self._safe_value(item, "furnishing", "—")),
        ]

        for index, (label, value) in enumerate(attributes):
            cell = tk.Frame(info, bg=self.CARD)
            cell.pack(side="left", padx=(0, 18))

            tk.Label(
                cell,
                text=label.upper(),
                bg=self.CARD,
                fg="#89908C",
                font=(self.FONT, 7, "bold"),
            ).pack(anchor="w")

            tk.Label(
                cell,
                text=str(value),
                bg=self.CARD,
                fg=self.TEXT,
                font=(self.FONT, 9, "bold"),
            ).pack(anchor="w", pady=(2, 0))

        bottom = tk.Frame(body, bg=self.CARD)
        bottom.pack(fill="x", pady=(14, 0))

        tk.Label(
            bottom,
            text=f"Property ID: {item.get('property_id', '—')}",
            bg=self.CARD,
            fg="#8A918D",
            font=(self.FONT, 8),
        ).pack(side="left")

        button = self._button(
            bottom,
            "View Details",
            lambda current=item: self._show_property_details(current),
            primary=True,
        )
        button.pack(side="right")

        return card

    def _open_selected_card(self, event, stored_rows):
        # This is intentionally harmless. Card buttons are the primary action.
        # Double-clicking a result card is supported below by finding the widget.
        widget = event.widget
        while widget is not None and widget is not self:
            if hasattr(widget, "_propintel_item"):
                self._show_property_details(widget._propintel_item)
                return
            try:
                widget = widget.master
            except AttributeError:
                break

    # =========================================================
    # PROPERTY DETAILS
    # =========================================================

    def _show_property_details(self, item):
        if not item:
            messagebox.showinfo(
                "Property details",
                "The selected property is no longer available.",
            )
            return

        dialog = tk.Toplevel(self)
        dialog.title(
            f"Property {item.get('property_id', '')} — PropIntel"
        )
        dialog.geometry("760x700")
        dialog.minsize(650, 600)
        dialog.configure(bg=self.BG)

        header = tk.Frame(dialog, bg=self.BG)
        header.pack(fill="x", padx=28, pady=(24, 15))

        tk.Label(
            header,
            text="Property Details",
            bg=self.BG,
            fg=self.TEXT,
            font=(self.FONT, 22, "bold"),
        ).pack(anchor="w")

        property_type = self._safe_value(
            item,
            "property_type",
            "Property",
        )
        bhk = self._safe_value(item, "bhk", "—")
        city = self._safe_value(item, "city")
        locality = self._safe_value(item, "locality")

        tk.Label(
            header,
            text=f"{bhk} BHK {property_type}",
            bg=self.BG,
            fg=self.TEXT,
            font=(self.FONT, 13, "bold"),
        ).pack(anchor="w", pady=(5, 0))

        tk.Label(
            header,
            text=f"{locality} • {city}",
            bg=self.BG,
            fg=self.MUTED,
            font=(self.FONT, 10),
        ).pack(anchor="w", pady=(2, 0))

        price = item.get("price_inr")
        price_text = (
            format_currency(float(price))
            if price is not None
            else "Price unavailable"
        )

        tk.Label(
            header,
            text=price_text,
            bg=self.BG,
            fg=self.PRIMARY_DARK,
            font=(self.FONT, 17, "bold"),
        ).pack(anchor="w", pady=(8, 0))

        canvas, inner = self._scrollable_frame(dialog, bg=self.BG)
        canvas.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        overview_card, overview = self._card(inner, padding=18)
        overview_card.pack(fill="x", pady=(0, 14))

        self._section_title(overview, "Property Overview")

        overview_fields = [
            ("BHK", item.get("bhk")),
            ("Bathrooms", item.get("bathrooms")),
            ("Balconies", item.get("balconies")),
            ("Carpet Area", self._format_area(item.get("carpet_area_sqft"))),
            ("Built-up Area", self._format_area(item.get("built_up_area_sqft"))),
            ("Super Built-up Area", self._format_area(item.get("super_built_up_area_sqft"))),
            ("Floor", item.get("floor")),
            ("Total Floors", item.get("total_floors")),
            ("Furnishing", item.get("furnishing")),
            ("Parking", item.get("parking")),
        ]

        self._details_grid(overview, overview_fields)

        info_card, info = self._card(inner, padding=18)
        info_card.pack(fill="x", pady=(0, 14))

        self._section_title(info, "Additional Information")

        additional_fields = [
            ("Property ID", item.get("property_id")),
            ("Source Listing ID", item.get("source_listing_id")),
            ("Building Type", item.get("building_type")),
            ("Age", item.get("age_years")),
            ("Facing", item.get("facing")),
            ("Amenities Count", item.get("amenities_count")),
            (
                "RERA Status",
                "Registered"
                if item.get("is_rera_registered")
                else "Not registered / Unknown",
            ),
        ]

        self._details_grid(info, additional_fields)

        self._button(
            dialog,
            "Close",
            dialog.destroy,
        ).pack(anchor="e", padx=28, pady=(0, 20))

    def _details_grid(self, parent, fields):
        grid = tk.Frame(parent, bg=self.CARD)
        grid.pack(fill="x")

        for index, (label, value) in enumerate(fields):
            row = index // 2
            column = index % 2

            cell = tk.Frame(grid, bg=self.CARD)
            cell.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(0, 22 if column == 0 else 0),
                pady=7,
            )

            grid.columnconfigure(column, weight=1)

            tk.Label(
                cell,
                text=label.upper(),
                bg=self.CARD,
                fg="#89908C",
                font=(self.FONT, 7, "bold"),
            ).pack(anchor="w")

            display = "Unknown" if value is None else str(value)

            tk.Label(
                cell,
                text=display,
                bg=self.CARD,
                fg=self.TEXT,
                font=(self.FONT, 9, "bold"),
            ).pack(anchor="w", pady=(3, 0))

    @staticmethod
    def _format_area(value):
        if value is None:
            return "Unknown"
        try:
            return f"{float(value):,.0f} sq ft"
        except (ValueError, TypeError):
            return str(value)

    # =========================================================
    # ANALYTICS
    # =========================================================

    def show_analysis(self):
        self._page_header(
            "Location Analytics",
            "Understand prices, areas and property distributions by location.",
            "analytics",
        )

        main = tk.Frame(self.content, bg=self.BG)
        main.pack(fill="both", expand=True, padx=34, pady=(0, 24))

        controls_card, controls = self._card(main, padding=18)
        controls_card.pack(fill="x", pady=(0, 15))

        self._section_title(
            controls,
            "Analysis Filters",
            "Choose a city and optionally narrow the analysis to a locality.",
        )

        row = tk.Frame(controls, bg=self.CARD)
        row.pack(fill="x")

        city = tk.StringVar(value="All")
        locality = tk.StringVar(value="All")

        tk.Label(
            row,
            text="CITY",
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 8, "bold"),
        ).pack(side="left")

        city_box = self._combo(
            row,
            city,
            self._filter_options("city"),
            width=25,
        )
        city_box.pack(side="left", padx=(8, 18))

        tk.Label(
            row,
            text="LOCALITY",
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 8, "bold"),
        ).pack(side="left")

        locality_box = self._combo(
            row,
            locality,
            self._filter_options("locality"),
            width=28,
        )
        locality_box.pack(side="left", padx=(8, 18))

        # Report area
        report_canvas, report_inner = self._scrollable_frame(
            main,
            bg=self.BG,
        )
        report_canvas.pack(fill="both", expand=True)

        def update_localities(_event=None):
            locality_box["values"] = self._filter_options(
                "locality",
                city.get() if city.get() != "All" else None,
            )
            locality.set("All")

        city_box.bind("<<ComboboxSelected>>", update_localities)

        def clear_report():
            for child in report_inner.winfo_children():
                child.destroy()

        def analyse():
            try:
                filters = {
                    "city": city.get(),
                    "locality": locality.get(),
                }

                result = calculate_location_analysis(
                    self.database.search_properties(filters)
                )

                clear_report()

                if not result:
                    card, inner = self._card(report_inner)
                    card.pack(fill="x")
                    tk.Label(
                        inner,
                        text="No properties are available for this location.",
                        bg=self.CARD,
                        fg=self.MUTED,
                        font=(self.FONT, 10),
                    ).pack(anchor="w")
                    return

                self._analysis_result_ui(report_inner, result)

            except DatabaseError as exc:
                messagebox.showerror("Location analysis", str(exc))

        self._button(
            row,
            "Generate Analysis",
            analyse,
            primary=True,
        ).pack(side="left")

        analyse()

    def _analysis_result_ui(self, parent, result):
        metrics = tk.Frame(parent, bg=self.BG)
        metrics.pack(fill="x", pady=(0, 14))

        metric_data = [
            ("Properties", f"{result['property_count']:,}"),
            ("Average Price", format_currency(result["average_price"])),
            ("Median Price", format_currency(result["median_price"])),
            ("Avg. Price / Sq Ft", format_currency(result["average_price_per_sqft"])),
        ]

        for index, (label, value) in enumerate(metric_data):
            metrics.columnconfigure(index, weight=1)

            card = tk.Frame(
                metrics,
                bg=self.CARD,
                highlightbackground=self.BORDER,
                highlightthickness=1,
            )
            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(0 if index == 0 else 6, 6 if index < 3 else 0),
            )

            tk.Label(
                card,
                text=label,
                bg=self.CARD,
                fg=self.MUTED,
                font=(self.FONT, 8),
            ).pack(anchor="w", padx=16, pady=(14, 0))

            tk.Label(
                card,
                text=value,
                bg=self.CARD,
                fg=self.TEXT,
                font=(self.FONT, 15, "bold"),
            ).pack(anchor="w", padx=16, pady=(3, 14))

        stats = tk.Frame(parent, bg=self.BG)
        stats.pack(fill="both", expand=True)

        left, left_inner = self._card(stats, padding=18)
        right, right_inner = self._card(stats, padding=18)

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 7),
        )
        right.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(7, 0),
        )

        self._section_title(left_inner, "Price & Area Statistics")

        rows = [
            ("Minimum Price", format_currency(result["minimum_price"])),
            ("Maximum Price", format_currency(result["maximum_price"])),
            ("Average Carpet Area", f"{result['average_carpet_area']:,.1f} sq ft"),
            ("Median Carpet Area", f"{result['median_carpet_area']:,.1f} sq ft"),
        ]

        for label, value in rows:
            line = tk.Frame(left_inner, bg=self.CARD)
            line.pack(fill="x", pady=7)

            tk.Label(
                line,
                text=label,
                bg=self.CARD,
                fg=self.MUTED,
                font=(self.FONT, 9),
            ).pack(side="left")

            tk.Label(
                line,
                text=value,
                bg=self.CARD,
                fg=self.TEXT,
                font=(self.FONT, 9, "bold"),
            ).pack(side="right")

        self._section_title(right_inner, "Property Type Distribution")

        distribution = result.get(
            "property_type_distribution",
            {},
        )

        if distribution:
            maximum = max(distribution.values()) or 1

            for key, value in distribution.items():
                tk.Label(
                    right_inner,
                    text=f"{key}: {value}",
                    bg=self.CARD,
                    fg=self.TEXT,
                    font=(self.FONT, 9),
                ).pack(anchor="w", pady=(2, 3))

                track = tk.Frame(
                    right_inner,
                    bg="#E9EEEB",
                    height=8,
                )
                track.pack(fill="x", pady=(0, 8))
                track.pack_propagate(False)

                fill = tk.Frame(
                    track,
                    bg=self.PRIMARY,
                    width=max(4, int(260 * value / maximum)),
                )
                fill.pack(side="left", fill="y")

        bhk_card, bhk_inner = self._card(parent, padding=18)
        bhk_card.pack(fill="x", pady=(14, 0))

        self._section_title(bhk_inner, "BHK Distribution")

        distribution = result.get("bhk_distribution", {})

        for key, value in distribution.items():
            row = tk.Frame(bhk_inner, bg=self.CARD)
            row.pack(fill="x", pady=4)

            tk.Label(
                row,
                text=str(key),
                bg=self.CARD,
                fg=self.TEXT,
                font=(self.FONT, 9, "bold"),
                width=10,
                anchor="w",
            ).pack(side="left")

            track = tk.Frame(
                row,
                bg="#E9EEEB",
                height=10,
            )
            track.pack(
                side="left",
                fill="x",
                expand=True,
                padx=10,
            )
            track.pack_propagate(False)

            maximum = max(distribution.values()) or 1
            width = max(4, int(300 * value / maximum))

            tk.Frame(
                track,
                bg=self.PRIMARY,
                width=width,
            ).pack(side="left", fill="y")

            tk.Label(
                row,
                text=str(value),
                bg=self.CARD,
                fg=self.MUTED,
                font=(self.FONT, 8),
                width=7,
                anchor="e",
            ).pack(side="right")

    # =========================================================
    # MATCHING
    # =========================================================

    def show_matching(self):
        self._page_header(
            "Match Properties",
            "Find properties that best fit a user's stated preferences.",
            "matching",
        )

        main = tk.Frame(self.content, bg=self.BG)
        main.pack(fill="both", expand=True, padx=34, pady=(0, 24))

        form_card, form_inner = self._card(main, padding=18)
        form_card.pack(fill="x", pady=(0, 15))

        self._section_title(
            form_inner,
            "Your Preferences",
            "Provide at least a city or locality.",
        )

        fields = [
            ("City", "city", "combo", self._filter_options("city")),
            ("Locality", "locality", "combo", self._filter_options("locality")),
            ("Maximum Budget", "budget", "entry", None),
            ("Property Type", "property_type", "combo", self._filter_options("property_type")),
            ("BHK", "bhk", "combo", self._filter_options("bhk")),
            ("Minimum Carpet Area", "min_area", "entry", None),
            ("Minimum Bathrooms", "bathrooms", "entry", None),
            ("Furnishing", "furnishing", "combo", self._filter_options("furnishing")),
        ]

        variables = {}

        form = tk.Frame(form_inner, bg=self.CARD)
        form.pack(fill="x")

        for index, (label, name, kind, options) in enumerate(fields):
            row, column = divmod(index, 4)

            cell = tk.Frame(form, bg=self.CARD)
            cell.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(0, 12),
                pady=(0, 10),
            )

            tk.Label(
                cell,
                text=label,
                bg=self.CARD,
                fg=self.MUTED,
                font=(self.FONT, 8, "bold"),
            ).pack(anchor="w", pady=(0, 4))

            variable = tk.StringVar(
                value="All" if kind == "combo" else ""
            )
            variables[name] = variable

            widget = (
                self._combo(cell, variable, options, width=22)
                if kind == "combo"
                else self._entry(cell, variable, width=23)
            )
            widget.pack(fill="x")

        for column in range(4):
            form.columnconfigure(column, weight=1)

        combo_widgets = []

        def collect_combos(widget):
            if isinstance(widget, ttk.Combobox):
                combo_widgets.append(widget)
            for child in widget.winfo_children():
                collect_combos(child)

        collect_combos(form)

        if len(combo_widgets) >= 2:
            city_box = combo_widgets[0]
            locality_box = combo_widgets[1]

            def update_localities(_event=None):
                locality_box["values"] = self._filter_options(
                    "locality",
                    variables["city"].get()
                    if variables["city"].get() != "All"
                    else None,
                )
                variables["locality"].set("All")

            city_box.bind("<<ComboboxSelected>>", update_localities)

        action_row = tk.Frame(form_inner, bg=self.CARD)
        action_row.pack(fill="x")

        # Results
        results_card, results_inner = self._card(main, padding=18)
        results_card.pack(fill="both", expand=True)

        header = tk.Frame(results_inner, bg=self.CARD)
        header.pack(fill="x", pady=(0, 12))

        tk.Label(
            header,
            text="Best Matches",
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 13, "bold"),
        ).pack(side="left")

        match_count = tk.StringVar(value="No search performed")
        tk.Label(
            header,
            textvariable=match_count,
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(side="right")

        results_canvas, results_frame = self._scrollable_frame(
            results_inner,
            bg=self.CARD,
        )
        results_canvas.pack(fill="both", expand=True)

        stored_matches = {}

        def find_matches():
            try:
                preferences = {
                    name: var.get()
                    for name, var in variables.items()
                }

                if preferences["city"] == "All":
                    preferences["city"] = ""

                if preferences["locality"] == "All":
                    preferences["locality"] = ""

                if (
                    not preferences["city"]
                    and not preferences["locality"]
                ):
                    raise ValueError(
                        "Please select a city or locality before matching."
                    )

                for key in ("budget", "min_area", "bathrooms"):
                    preferences[key] = self._read_number(
                        preferences[key],
                        key.replace("_", " "),
                    )

                matches = rank_properties(
                    self.database.search_properties({}),
                    preferences,
                )

                stored_matches.clear()

                for child in results_frame.winfo_children():
                    child.destroy()

                if not matches:
                    match_count.set("0 matches")

                    tk.Label(
                        results_frame,
                        text="No properties are available to match.",
                        bg=self.CARD,
                        fg=self.MUTED,
                        font=(self.FONT, 10),
                    ).pack(anchor="w", pady=20)
                    return

                match_count.set(f"{len(matches):,} matches")

                for index, item in enumerate(matches):
                    stored_matches[
                        str(item["property_id"])
                    ] = item

                    self._create_match_card(
                        results_frame,
                        item,
                    )

            except (ValueError, DatabaseError) as exc:
                messagebox.showerror("Matching", str(exc))

        self._button(
            action_row,
            "Find Best Matches",
            find_matches,
            primary=True,
        ).pack(side="right")

    def _create_match_card(self, parent, item):
        card = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        card.pack(fill="x", pady=6)

        body = tk.Frame(card, bg=self.CARD)
        body.pack(fill="both", expand=True, padx=18, pady=15)

        top = tk.Frame(body, bg=self.CARD)
        top.pack(fill="x")

        property_type = self._safe_value(
            item,
            "property_type",
            "Property",
        )
        bhk = self._safe_value(item, "bhk", "—")

        tk.Label(
            top,
            text=f"{bhk} BHK {property_type}",
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 11, "bold"),
        ).pack(side="left")

        score = float(item.get("score", 0))

        badge = tk.Label(
            top,
            text=f"{score:.1f}% MATCH",
            bg=self.PRIMARY_LIGHT,
            fg=self.PRIMARY_DARK,
            font=(self.FONT, 8, "bold"),
            padx=9,
            pady=5,
        )
        badge.pack(side="right")

        tk.Label(
            body,
            text=(
                f"{self._safe_value(item, 'locality')} • "
                f"{self._safe_value(item, 'city')}"
            ),
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(anchor="w", pady=(5, 8))

        price = item.get("price_inr")
        price_text = (
            format_currency(float(price))
            if price is not None
            else "Price unavailable"
        )

        tk.Label(
            body,
            text=price_text,
            bg=self.CARD,
            fg=self.PRIMARY_DARK,
            font=(self.FONT, 13, "bold"),
        ).pack(anchor="w")

        attributes = tk.Frame(body, bg=self.CARD)
        attributes.pack(fill="x", pady=(8, 0))

        attribute_text = (
            f"{bhk} BHK   •   "
            f"{self._safe_value(item, 'bathrooms', '—')} Bath   •   "
            f"{self._safe_value(item, 'carpet_area_sqft', '—')} sqft"
        )

        tk.Label(
            attributes,
            text=attribute_text,
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(side="left")

        buttons = tk.Frame(body, bg=self.CARD)
        buttons.pack(fill="x", pady=(13, 0))

        self._button(
            buttons,
            "View Details",
            lambda current=item: self._show_property_details(
                current
            ),
        ).pack(side="right")

        self._button(
            buttons,
            "Why this match?",
            lambda current=item: self._show_match_explanation(
                current
            ),
            primary=True,
        ).pack(side="right", padx=(0, 8))

    def _show_match_explanation(self, item):
        explanation = item.get("explanation", [])

        if not explanation:
            explanation = ["No explanation was returned."]

        dialog = tk.Toplevel(self)
        dialog.title("Match Explanation")
        dialog.geometry("560x420")
        dialog.configure(bg=self.BG)

        tk.Label(
            dialog,
            text=f"{float(item.get('score', 0)):.1f}% Match",
            bg=self.BG,
            fg=self.TEXT,
            font=(self.FONT, 20, "bold"),
        ).pack(anchor="w", padx=25, pady=(25, 5))

        tk.Label(
            dialog,
            text="Why this property matched the selected preferences",
            bg=self.BG,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(anchor="w", padx=25)

        card, inner = self._card(dialog, padding=18)
        card.pack(fill="both", expand=True, padx=25, pady=20)

        for text in explanation:
            row = tk.Frame(inner, bg=self.CARD)
            row.pack(fill="x", pady=5)

            tk.Label(
                row,
                text="✓",
                bg=self.CARD,
                fg=self.PRIMARY,
                font=(self.FONT, 11, "bold"),
            ).pack(side="left", padx=(0, 8))

            tk.Label(
                row,
                text=str(text),
                bg=self.CARD,
                fg=self.TEXT,
                font=(self.FONT, 9),
                wraplength=430,
                justify="left",
            ).pack(side="left", anchor="w")

        self._button(
            dialog,
            "Close",
            dialog.destroy,
        ).pack(anchor="e", padx=25, pady=(0, 20))

    # =========================================================
    # COMPARISON
    # =========================================================

    def show_comparison(self):
        self._page_header(
            "Compare Properties",
            "Select two or more properties and compare their factual attributes.",
            "comparison",
        )

        main = tk.Frame(self.content, bg=self.BG)
        main.pack(fill="both", expand=True, padx=34, pady=(0, 24))

        card, inner = self._card(main, padding=18)
        card.pack(fill="both", expand=True)

        top = tk.Frame(inner, bg=self.CARD)
        top.pack(fill="x", pady=(0, 12))

        tk.Label(
            top,
            text="Property Selection",
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 13, "bold"),
        ).pack(side="left")

        tk.Label(
            top,
            text="Hold Ctrl to select multiple properties.",
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(side="right")

        columns = (
            "id",
            "city",
            "locality",
            "type",
            "bhk",
            "price",
        )

        holder, choices = self._make_tree(
            inner,
            columns,
            [
                "Property ID",
                "City",
                "Locality",
                "Type",
                "BHK",
                "Price",
            ],
            height=14,
            selectmode="extended",
        )
        holder.pack(fill="both", expand=True)

        try:
            rows = self.database.search_properties({})

            for item in rows:
                choices.insert(
                    "",
                    "end",
                    values=(
                        item["property_id"],
                        item["city"] or "Unknown",
                        item["locality"] or "Unknown",
                        item["property_type"],
                        item["bhk"],
                        format_currency(
                            float(item["price_inr"])
                        ),
                    ),
                )

        except DatabaseError as exc:
            messagebox.showerror(
                "Property comparison",
                str(exc),
            )

        action = tk.Frame(inner, bg=self.CARD)
        action.pack(fill="x", pady=(12, 0))

        def compare():
            selected = choices.selection()

            if len(selected) < 2:
                messagebox.showwarning(
                    "Property comparison",
                    "Select at least two properties.",
                )
                return

            try:
                ids = [
                    choices.item(entry, "values")[0]
                    for entry in selected
                ]

                properties = self.database.get_properties(ids)
                self._show_comparison(properties)

            except DatabaseError as exc:
                messagebox.showerror(
                    "Property comparison",
                    str(exc),
                )

        self._button(
            action,
            "Compare Selected Properties",
            compare,
            primary=True,
        ).pack(side="right")

    def _show_comparison(self, properties):
        dialog = tk.Toplevel(self)
        dialog.title("Property Comparison — PropIntel")
        dialog.geometry("1100x650")
        dialog.minsize(900, 550)
        dialog.configure(bg=self.BG)

        header = tk.Frame(dialog, bg=self.BG)
        header.pack(fill="x", padx=25, pady=(22, 12))

        tk.Label(
            header,
            text="Property Comparison",
            bg=self.BG,
            fg=self.TEXT,
            font=(self.FONT, 21, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text=f"Comparing {len(properties)} selected properties.",
            bg=self.BG,
            fg=self.MUTED,
            font=(self.FONT, 9),
        ).pack(anchor="w", pady=(4, 0))

        card = tk.Frame(
            dialog,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        columns = [
            "attribute"
        ] + [
            f"p{item['property_id']}"
            for item in properties
        ]

        headings = [
            "Attribute"
        ] + [
            f"Property {item['property_id']}"
            for item in properties
        ]

        holder, tree = self._make_tree(
            card,
            columns,
            headings,
            height=20,
        )
        holder.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        tree.column(
            "attribute",
            width=220,
            anchor="w",
        )

        for column in columns[1:]:
            tree.column(
                column,
                width=220,
                anchor="center",
            )

        for row in build_comparison_rows(properties):
            tree.insert(
                "",
                "end",
                values=row,
            )

    # =========================================================
    # ABOUT
    # =========================================================

    def show_about(self):
        self._page_header(
            "About PropIntel",
            "A Python-based academic real-estate analysis application.",
            "about",
        )

        main = tk.Frame(self.content, bg=self.BG)
        main.pack(fill="both", expand=True, padx=34, pady=(0, 25))

        card, inner = self._card(main, padding=28)
        card.pack(fill="x")

        tk.Label(
            inner,
            text="PropIntel",
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 24, "bold"),
        ).pack(anchor="w")

        tk.Label(
            inner,
            text="Residential Real Estate Analysis System",
            bg=self.CARD,
            fg=self.PRIMARY_DARK,
            font=(self.FONT, 12, "bold"),
        ).pack(anchor="w", pady=(5, 15))

        description = (
            "PropIntel is a desktop application designed to explore, "
            "filter, analyze, match and compare residential real-estate "
            "properties using a structured property dataset."
        )

        tk.Label(
            inner,
            text=description,
            bg=self.CARD,
            fg=self.MUTED,
            font=(self.FONT, 10),
            wraplength=850,
            justify="left",
        ).pack(anchor="w")

        features = [
            "Property search and filtering",
            "Location-specific price and area analysis",
            "Rule-based property matching",
            "Explainable match scores",
            "Factual property comparison",
            "MySQL database integration",
            "Pandas-based analysis",
            "Tkinter desktop interface",
        ]

        tk.Label(
            inner,
            text="Core Features",
            bg=self.CARD,
            fg=self.TEXT,
            font=(self.FONT, 13, "bold"),
        ).pack(anchor="w", pady=(25, 10))

        for feature in features:
            row = tk.Frame(inner, bg=self.CARD)
            row.pack(anchor="w", fill="x", pady=3)

            tk.Label(
                row,
                text="✓",
                bg=self.CARD,
                fg=self.PRIMARY,
                font=(self.FONT, 10, "bold"),
            ).pack(side="left", padx=(0, 8))

            tk.Label(
                row,
                text=feature,
                bg=self.CARD,
                fg=self.TEXT,
                font=(self.FONT, 9),
            ).pack(side="left")

        note = tk.Frame(
            inner,
            bg=self.PRIMARY_LIGHT,
        )
        note.pack(fill="x", pady=(25, 0))

        tk.Label(
            note,
            text=(
                "Dataset note: PropIntel currently focuses on factual "
                "property data. Property images are not required for the "
                "application."
            ),
            bg=self.PRIMARY_LIGHT,
            fg=self.PRIMARY_DARK,
            font=(self.FONT, 9),
            wraplength=850,
            justify="left",
        ).pack(padx=15, pady=12)

    # =========================================================
    # STARTUP
    # =========================================================


if __name__ == "__main__":
    app = PropIntelApp()
    app.mainloop()
