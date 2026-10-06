"""Tkinter interface for the PropIntel academic desktop application."""

import tkinter as tk
from tkinter import messagebox, ttk

from analysis import calculate_location_analysis, format_currency
from comparison import build_comparison_rows
from database import DatabaseError, PropertyDatabase
from matching import rank_properties


class PropIntelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PropIntel - Real Estate Analysis System")
        self.geometry("1120x700")
        self.minsize(900, 600)
        self.database = PropertyDatabase()
        self.current_frame = None
        self._configure_style()
        self.show_main_menu()

    def _configure_style(self):
        style = ttk.Style(self)
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("TButton", padding=(8, 5))
        style.configure("Treeview", rowheight=26)

    def _new_screen(self, title):
        if self.current_frame:
            self.current_frame.destroy()
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=title, style="Title.TLabel").pack(anchor="w")
        self.current_frame = frame
        return frame

    def _back_button(self, parent):
        ttk.Button(parent, text="Back to Main Menu", command=self.show_main_menu).pack(anchor="w", pady=(12, 0))

    def show_main_menu(self):
        frame = self._new_screen("PropIntel")
        ttk.Label(frame, text="Residential Real Estate Analysis System", style="Heading.TLabel").pack(anchor="w", pady=(0, 28))
        menu = ttk.Frame(frame)
        menu.pack(anchor="w")
        for text, command in [
            ("Search & Filter Properties", self.show_search),
            ("Location Analysis", self.show_analysis),
            ("Match Properties", self.show_matching),
            ("Compare Properties", self.show_comparison),
            ("Exit", self.destroy),
        ]:
            ttk.Button(menu, text=text, command=command, width=30).pack(fill="x", pady=6)
        ttk.Label(frame, text="Import data first using: python data_import.py", foreground="#555555").pack(anchor="w", pady=(25, 0))

    def _filter_options(self, column, city=None):
        try:
            return ["All"] + [str(value) for value in self.database.distinct_values(column, city)]
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
            raise ValueError(f"{label} must be a non-negative number.") from exc

    def _make_tree(self, parent, columns, headings, height=12, selectmode="browse"):
        holder = ttk.Frame(parent)
        tree = ttk.Treeview(holder, columns=columns, show="headings", height=height, selectmode=selectmode)
        for column, heading in zip(columns, headings):
            tree.heading(column, text=heading)
            tree.column(column, width=130, anchor="center")
        vertical = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(holder, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        holder.columnconfigure(0, weight=1)
        holder.rowconfigure(0, weight=1)
        return holder, tree

    def show_search(self):
        frame = self._new_screen("Search & Filter Properties")
        form = ttk.LabelFrame(frame, text="Filters", padding=10)
        form.pack(fill="x", pady=12)
        fields = [
            ("City", "city", "combo", self._filter_options("city")),
            ("Locality", "locality", "combo", self._filter_options("locality")),
            ("Property Type", "property_type", "combo", self._filter_options("property_type")),
            ("BHK", "bhk", "combo", self._filter_options("bhk")),
            ("Furnishing", "furnishing", "combo", self._filter_options("furnishing")),
            ("Parking", "parking", "combo", self._filter_options("parking")),
            ("Min Price", "min_price", "entry", None), ("Max Price", "max_price", "entry", None),
            ("Min Carpet Area", "min_area", "entry", None), ("Max Carpet Area", "max_area", "entry", None),
        ]
        variables = {}
        for index, (label, name, kind, options) in enumerate(fields):
            row, column = divmod(index, 5)
            ttk.Label(form, text=label).grid(row=row * 2, column=column, sticky="w", padx=5, pady=(0, 2))
            variable = tk.StringVar(value="All" if kind == "combo" else "")
            variables[name] = variable
            if kind == "combo":
                widget = ttk.Combobox(form, textvariable=variable, values=options, state="readonly", width=18)
            else:
                widget = ttk.Entry(form, textvariable=variable, width=20)
            widget.grid(row=row * 2 + 1, column=column, sticky="ew", padx=5, pady=(0, 8))
        columns = ("id", "city", "locality", "type", "bhk", "area", "bathrooms", "furnishing", "price")
        holder, results = self._make_tree(frame, columns, ["Property ID", "City", "Locality", "Type", "BHK", "Carpet Area", "Bathrooms", "Furnishing", "Price"])
        holder.pack(fill="both", expand=True, pady=8)

        def search():
            try:
                filters = {name: variable.get() for name, variable in variables.items()}
                for key in ("min_price", "max_price", "min_area", "max_area"):
                    filters[key] = self._read_number(filters[key], key.replace("_", " "))
                if filters["min_price"] and filters["max_price"] and filters["min_price"] > filters["max_price"]:
                    raise ValueError("Minimum price cannot exceed maximum price.")
                rows = self.database.search_properties(filters)
                results.delete(*results.get_children())
                for item in rows:
                    results.insert("", "end", values=(
                        item["property_id"], item["city"] or "Unknown", item["locality"] or "Unknown",
                        item["property_type"], item["bhk"], item["carpet_area_sqft"], item["bathrooms"],
                        item["furnishing"] or "Unknown", format_currency(float(item["price_inr"])),
                    ))
                if not rows:
                    messagebox.showinfo("Search", "No properties matched the selected filters.")
            except (ValueError, DatabaseError) as exc:
                messagebox.showerror("Search", str(exc))

        def details():
            selected = results.selection()
            if not selected:
                messagebox.showwarning("Property details", "Select a property first.")
                return
            property_id = results.item(selected[0], "values")[0]
            try:
                self._show_property_details(self.database.get_property(property_id))
            except DatabaseError as exc:
                messagebox.showerror("Property details", str(exc))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=5)
        ttk.Button(buttons, text="Search", command=search).pack(side="left")
        ttk.Button(buttons, text="View Selected Property Details", command=details).pack(side="left", padx=8)
        self._back_button(frame)

    def _show_property_details(self, item):
        if not item:
            messagebox.showinfo("Property details", "The selected property is no longer available.")
            return
        dialog = tk.Toplevel(self)
        dialog.title(f"Property {item['property_id']} Details")
        dialog.geometry("620x620")
        tree_holder, tree = self._make_tree(dialog, ("field", "value"), ("Field", "Value"), height=21)
        tree_holder.pack(fill="both", expand=True, padx=15, pady=15)
        tree.column("field", width=230, anchor="w")
        tree.column("value", width=330, anchor="w")
        labels = {
            "property_id": "Property ID", "source_listing_id": "Source Listing ID", "city": "City", "locality": "Locality",
            "property_type": "Property Type", "bhk": "BHK", "bathrooms": "Bathrooms", "balconies": "Balconies",
            "price_inr": "Price", "carpet_area_sqft": "Carpet Area", "built_up_area_sqft": "Built-up Area",
            "super_built_up_area_sqft": "Super Built-up Area", "floor": "Floor", "total_floors": "Total Floors",
            "furnishing": "Furnishing", "parking": "Parking", "building_type": "Building Type", "age_years": "Age",
            "facing": "Facing", "amenities_count": "Amenities Count", "is_rera_registered": "RERA Status",
        }
        for key, label in labels.items():
            value = format_currency(float(item[key])) if key == "price_inr" else (item.get(key) if item.get(key) is not None else "Unknown")
            tree.insert("", "end", values=(label, value))

    def show_analysis(self):
        frame = self._new_screen("Location Analysis")
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=12)
        ttk.Label(controls, text="City").grid(row=0, column=0, sticky="w")
        city = tk.StringVar(value="All")
        city_box = ttk.Combobox(controls, textvariable=city, values=self._filter_options("city"), state="readonly", width=25)
        city_box.grid(row=1, column=0, padx=(0, 12))
        ttk.Label(controls, text="Locality (optional)").grid(row=0, column=1, sticky="w")
        locality = tk.StringVar(value="All")
        locality_box = ttk.Combobox(controls, textvariable=locality, values=self._filter_options("locality"), state="readonly", width=28)
        locality_box.grid(row=1, column=1, padx=(0, 12))
        report = tk.Text(frame, height=20, wrap="word", font=("Consolas", 10))
        report.pack(fill="both", expand=True, pady=8)
        report.configure(state="disabled")

        def update_localities(_event=None):
            locality_box["values"] = self._filter_options("locality", city.get() if city.get() != "All" else None)
            locality.set("All")
        city_box.bind("<<ComboboxSelected>>", update_localities)

        def analyse():
            try:
                filters = {"city": city.get(), "locality": locality.get()}
                result = calculate_location_analysis(self.database.search_properties(filters))
                report.configure(state="normal")
                report.delete("1.0", "end")
                if not result:
                    report.insert("end", "No properties are available for this location.")
                else:
                    report.insert("end", "LOCATION ANALYSIS\n\n")
                    report.insert("end", f"Number of properties: {result['property_count']}\n")
                    report.insert("end", f"Average price: {format_currency(result['average_price'])}\nMedian price: {format_currency(result['median_price'])}\n")
                    report.insert("end", f"Minimum price: {format_currency(result['minimum_price'])}\nMaximum price: {format_currency(result['maximum_price'])}\n")
                    report.insert("end", f"Average carpet area: {result['average_carpet_area']:,.1f} sq ft\n")
                    report.insert("end", f"Median carpet area: {result['median_carpet_area']:,.1f} sq ft\n")
                    report.insert("end", f"Average price per sq ft: {format_currency(result['average_price_per_sqft'])}\n\n")
                    report.insert("end", "Property type distribution\n")
                    for key, value in result["property_type_distribution"].items(): report.insert("end", f"  {key}: {value}\n")
                    report.insert("end", "\nBHK distribution\n")
                    for key, value in result["bhk_distribution"].items(): report.insert("end", f"  {key}: {value}\n")
                report.configure(state="disabled")
            except DatabaseError as exc:
                messagebox.showerror("Location analysis", str(exc))
        ttk.Button(controls, text="Generate Analysis", command=analyse).grid(row=1, column=2)
        self._back_button(frame)

    def show_matching(self):
        frame = self._new_screen("Rule-Based Property Matching")
        form = ttk.LabelFrame(frame, text="Preferences (provide at least a city or locality)", padding=10)
        form.pack(fill="x", pady=12)
        fields = [("City", "city", "combo", self._filter_options("city")), ("Locality", "locality", "combo", self._filter_options("locality")),
                  ("Budget (maximum)", "budget", "entry", None), ("Property Type", "property_type", "combo", self._filter_options("property_type")),
                  ("BHK", "bhk", "combo", self._filter_options("bhk")), ("Minimum Carpet Area", "min_area", "entry", None),
                  ("Minimum Bathrooms", "bathrooms", "entry", None), ("Furnishing", "furnishing", "combo", self._filter_options("furnishing"))]
        variables = {}
        for index, (label, name, kind, options) in enumerate(fields):
            row, column = divmod(index, 4)
            ttk.Label(form, text=label).grid(row=row * 2, column=column, sticky="w", padx=5)
            variable = tk.StringVar(value="All" if kind == "combo" else "")
            variables[name] = variable
            widget = ttk.Combobox(form, textvariable=variable, values=options, state="readonly", width=23) if kind == "combo" else ttk.Entry(form, textvariable=variable, width=25)
            widget.grid(row=row * 2 + 1, column=column, padx=5, pady=(1, 8))
        columns = ("id", "score", "city", "locality", "type", "bhk", "price")
        holder, results = self._make_tree(frame, columns, ["Property ID", "Match Score", "City", "Locality", "Type", "BHK", "Price"])
        holder.pack(fill="both", expand=True, pady=8)
        stored_matches = {}
        def find_matches():
            try:
                preferences = {name: var.get() for name, var in variables.items()}
                if preferences["city"] == "All": preferences["city"] = ""
                if preferences["locality"] == "All": preferences["locality"] = ""
                if not preferences["city"] and not preferences["locality"]:
                    raise ValueError("Please select a city or locality before matching.")
                for key in ("budget", "min_area", "bathrooms"): preferences[key] = self._read_number(preferences[key], key.replace("_", " "))
                matches = rank_properties(self.database.search_properties({}), preferences)
                results.delete(*results.get_children()); stored_matches.clear()
                for item in matches:
                    stored_matches[str(item["property_id"])] = item
                    results.insert("", "end", values=(item["property_id"], f"{item['score']:.1f}%", item["city"] or "Unknown", item["locality"] or "Unknown", item["property_type"], item["bhk"], format_currency(float(item["price_inr"]))))
                if not matches: messagebox.showinfo("Matching", "No properties are available to match.")
            except (ValueError, DatabaseError) as exc: messagebox.showerror("Matching", str(exc))
        def show_explanation():
            selected = results.selection()
            if not selected: messagebox.showwarning("Match explanation", "Select a matching property first."); return
            item = stored_matches[results.item(selected[0], "values")[0]]
            messagebox.showinfo(f"Match Score: {item['score']:.1f}%", "\n".join(item["explanation"]))
        buttons = ttk.Frame(frame); buttons.pack(fill="x")
        ttk.Button(buttons, text="Find Matches", command=find_matches).pack(side="left")
        ttk.Button(buttons, text="Show Selected Explanation", command=show_explanation).pack(side="left", padx=8)
        self._back_button(frame)

    def show_comparison(self):
        frame = self._new_screen("Property Comparison")
        ttk.Label(frame, text="Select two or more properties, then compare their factual attributes.").pack(anchor="w", pady=10)
        columns = ("id", "city", "locality", "type", "bhk", "price")
        holder, choices = self._make_tree(frame, columns, ["Property ID", "City", "Locality", "Type", "BHK", "Price"], height=15, selectmode="extended")
        holder.pack(fill="both", expand=True)
        try:
            for item in self.database.search_properties({}):
                choices.insert("", "end", values=(item["property_id"], item["city"] or "Unknown", item["locality"] or "Unknown", item["property_type"], item["bhk"], format_currency(float(item["price_inr"]))))
        except DatabaseError as exc:
            messagebox.showerror("Property comparison", str(exc))
        def compare():
            selected = choices.selection()
            if len(selected) < 2: messagebox.showwarning("Property comparison", "Select at least two properties."); return
            try:
                ids = [choices.item(entry, "values")[0] for entry in selected]
                properties = self.database.get_properties(ids)
                self._show_comparison(properties)
            except DatabaseError as exc: messagebox.showerror("Property comparison", str(exc))
        ttk.Button(frame, text="Compare Selected Properties", command=compare).pack(anchor="w", pady=10)
        self._back_button(frame)

    def _show_comparison(self, properties):
        dialog = tk.Toplevel(self); dialog.title("Property Comparison"); dialog.geometry("1050x620")
        columns = ["attribute"] + [f"p{item['property_id']}" for item in properties]
        headings = ["Attribute"] + [f"Property {item['property_id']}" for item in properties]
        holder, tree = self._make_tree(dialog, columns, headings, height=20); holder.pack(fill="both", expand=True, padx=15, pady=15)
        for row in build_comparison_rows(properties): tree.insert("", "end", values=row)
