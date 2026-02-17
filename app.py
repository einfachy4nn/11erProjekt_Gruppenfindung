import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import csv
from ortools.linear_solver import pywraplp
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import A4


# --------------------------------------------------
# DARK MODE STYLE
# --------------------------------------------------
def apply_dark_mode(root):
    style = ttk.Style(root)
    style.theme_use("default")

    bg = "#1e1e1e"
    fg = "#ffffff"
    accent = "#3a7ff6"
    field = "#2b2b2b"

    root.configure(bg=bg)

    style.configure("TFrame", background=bg)
    style.configure("TLabel", background=bg, foreground=fg)
    style.configure("TButton", background=field, foreground=fg)
    style.map("TButton", background=[("active", accent)])

    style.configure("TEntry", fieldbackground=field, background=field, foreground=fg)

    style.configure("TNotebook", background=bg)
    style.configure("TNotebook.Tab", background=field, foreground=fg, padding=[10, 5])
    style.map("TNotebook.Tab",
              background=[("selected", accent)],
              foreground=[("selected", "#ffffff")])


def apply_light_mode(root):
    style = ttk.Style(root)
    style.theme_use("default")

    bg = "#f2f2f2"
    fg = "#000000"
    accent = "#3a7ff6"
    field = "#ffffff"

    root.configure(bg=bg)

    style.configure("TFrame", background=bg)
    style.configure("TLabel", background=bg, foreground=fg)
    style.configure("TButton", background=field, foreground=fg)
    style.map("TButton", background=[("active", accent)])

    style.configure("TEntry", fieldbackground=field, background=field, foreground=fg)

    style.configure("TNotebook", background=bg)
    style.configure("TNotebook.Tab", background=field, foreground=fg, padding=[10, 5])
    style.map("TNotebook.Tab",
              background=[("selected", accent)],
              foreground=[("selected", "#ffffff")])


# --------------------------------------------------
# DB
# --------------------------------------------------
def db_connect():
    return sqlite3.connect("projektwahl.db")


# --------------------------------------------------
# TAB: GRUPPEN
# --------------------------------------------------
class GroupsTab(ttk.Frame):
    def __init__(self, parent, status):
        super().__init__(parent)
        self.status = status

        ttk.Label(self, text="Gruppe hinzufügen", font=("Segoe UI", 14)).grid(row=0, column=0, columnspan=2, pady=15)

        ttk.Label(self, text="Name").grid(row=1, column=0, sticky="e", padx=5)
        self.entry = ttk.Entry(self, width=30)
        self.entry.grid(row=1, column=1)

        ttk.Button(self, text="Speichern", command=self.save).grid(row=2, column=0, columnspan=2, pady=15)

    def save(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showerror("Fehler", "Bitte Gruppennamen eingeben.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO groups (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()

        self.entry.delete(0, tk.END)
        self.status.set("Gruppe gespeichert ✔")


# --------------------------------------------------
# TAB: SCHÜLER
# --------------------------------------------------
class StudentsTab(ttk.Frame):
    def __init__(self, parent, status):
        super().__init__(parent)
        self.status = status

        ttk.Label(self, text="Schüler hinzufügen", font=("Segoe UI", 14)).grid(row=0, column=0, columnspan=2, pady=15)

        labels = ["Name", "Klasse", "Erstwunsch", "Zweitwunsch", "Drittwunsch"]
        self.entries = []

        for i, text in enumerate(labels):
            ttk.Label(self, text=text).grid(row=i+1, column=0, sticky="e", padx=5)
            e = ttk.Entry(self, width=30)
            e.grid(row=i+1, column=1)
            self.entries.append(e)

        ttk.Button(self, text="Speichern", command=self.save).grid(row=6, column=0, columnspan=2, pady=15)

    def save(self):
        values = [e.get().strip() for e in self.entries]
        if any(v == "" for v in values):
            messagebox.showerror("Fehler", "Alle Felder ausfüllen.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO students (name, klasse, choice1, choice2, choice3)
                    VALUES (?, ?, ?, ?, ?)
                    """, values)
        conn.commit()
        conn.close()

        for e in self.entries:
            e.delete(0, tk.END)

        self.status.set("Schüler gespeichert ✔")


# --------------------------------------------------
# TAB: GENERIEREN
# --------------------------------------------------
class GenerateTab(ttk.Frame):
    def __init__(self, parent, status):
        super().__init__(parent)
        self.status = status

        ttk.Label(self, text="Zuteilung generieren", font=("Segoe UI", 14)).grid(row=0, column=0, columnspan=2, pady=15)

        labels = [
            "Max. Schüler pro Gruppe",
            "Min. Schüler pro Gruppe",
            "Max. Schüler pro Klasse"
        ]

        self.entries = []
        for i, text in enumerate(labels):
            ttk.Label(self, text=text).grid(row=i+1, column=0, sticky="e", padx=5)
            e = ttk.Entry(self, width=20)
            e.grid(row=i+1, column=1)
            self.entries.append(e)

        ttk.Button(self, text="Generieren", command=self.generate).grid(row=4, column=0, columnspan=2, pady=20)


    def generate(self):
        try:
            MAX_S, MIN_S, MAX_K = map(int, [e.get() for e in self.entries])
        except ValueError:
            messagebox.showerror("Fehler", "Bitte Zahlen eingeben.")
            return

        conn = db_connect()
        cur = conn.cursor()

        # -----------------------
        # Daten laden
        # -----------------------
        cur.execute("SELECT id, klasse, choice1, choice2, choice3 FROM students")
        students = cur.fetchall()

        cur.execute("SELECT id, name FROM groups")
        groups = cur.fetchall()

        if not students or not groups:
            messagebox.showerror("Fehler", "Nicht genug Daten.")
            return

        solver = pywraplp.Solver.CreateSolver("CBC")

        # -----------------------
        # Variablen x[s,g]
        # -----------------------
        x = {}
        for s in students:
            for g in groups:
                x[(s[0], g[0])] = solver.IntVar(0, 1, f"x_{s[0]}_{g[0]}")

        # -----------------------
        # Jeder Schüler genau 1 Gruppe
        # -----------------------
        for s in students:
            solver.Add(sum(x[(s[0], g[0])] for g in groups) == 1)

        # -----------------------
        # Gruppengröße MIN/MAX
        # -----------------------
        for g in groups:
            solver.Add(sum(x[(s[0], g[0])] for s in students) <= MAX_S)
            solver.Add(sum(x[(s[0], g[0])] for s in students) >= MIN_S)

        # -----------------------
        # Klassenlimit pro Gruppe
        # -----------------------
        klassen = list(set(s[1] for s in students))

        for g in groups:
            for k in klassen:
                solver.Add(
                    sum(x[(s[0], g[0])] for s in students if s[1] == k) <= MAX_K
                )

        # -----------------------
        # Wunschgewichtung
        # -----------------------
        objective = solver.Objective()

        for s in students:
            sid, _, c1, c2, c3 = s
            for g in groups:
                gid, gname = g

                weight = 0
                if gname == c1:
                    weight = 100
                elif gname == c2:
                    weight = 50
                elif gname == c3:
                    weight = 10

                objective.SetCoefficient(x[(sid, gid)], weight)

        objective.SetMaximization()

        # -----------------------
        # Solve
        # -----------------------
        status = solver.Solve()

        if status != pywraplp.Solver.OPTIMAL:
            messagebox.showerror("Fehler", "Keine gültige Lösung gefunden.")
            return

        # -----------------------
        # Alte Zuweisungen löschen
        # -----------------------
        cur.execute("DELETE FROM assignments")

        # -----------------------
        # Ergebnisse speichern
        # -----------------------
        for s in students:
            sid = s[0]
            for g in groups:
                gid = g[0]
                if x[(sid, gid)].solution_value() == 1:
                    cur.execute(
                        "INSERT INTO assignments (student_id, group_id) VALUES (?,?)",
                        (sid, gid)
                    )

        conn.commit()
        conn.close()

        self.status.set("Zuteilung erfolgreich generiert ✔")
        messagebox.showinfo("Fertig", "Zuteilung wurde berechnet.")




# --------------------------------------------------
# TAB: BEARBEITEN
# --------------------------------------------------
class EditTab(ttk.Frame):
    def __init__(self, parent, status):
        super().__init__(parent)
        self.status = status

        ttk.Label(self, text="Datenbank bearbeiten", font=("Segoe UI", 14)).pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Schülerliste", command=self.open_students).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Gruppenliste", command=self.open_groups).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Zuweisungen", command=self.open_assignments).pack(side="left", padx=5)

    def sort_column(self, tv, col, reverse):
        data = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            data.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)

        for index, (val, k) in enumerate(data):
            tv.move(k, '', index)

        tv.heading(col, command=lambda: self.sort_column(tv, col, not reverse))

    def open_table(self, title, query, columns, table_name, id_column):
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("1000x550")

        table = ttk.Treeview(window, columns=columns, show="headings")

        for col in columns:
            table.heading(col, text=col,
                          command=lambda c=col: self.sort_column(table, c, False))
            table.column(col, width=160)

        table.pack(fill="both", expand=True)

        def reload_data():
            table.delete(*table.get_children())
            conn = db_connect()
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            conn.close()
            for row in rows:
                table.insert("", tk.END, values=row)

        reload_data()

        def delete_entry():
            sel = table.selection()
            if not sel:
                return
            values = table.item(sel[0])['values']

            conn = db_connect()
            cur = conn.cursor()

            if table_name == "assignments":
                cur.execute(
                    "DELETE FROM assignments WHERE student_id=? AND group_id=?",
                    (values[0], values[3])
                )
            else:
                cur.execute(f"DELETE FROM {table_name} WHERE {id_column}=?",
                            (values[0],))

            conn.commit()
            conn.close()
            reload_data()

        def edit_entry():
            if table_name == "assignments":
                messagebox.showinfo("Info", "Nur löschbar.")
                return

            sel = table.selection()
            if not sel:
                return

            values = table.item(sel[0])['values']
            record_id = values[0]

            win = tk.Toplevel(window)
            win.title("Bearbeiten")

            entries = []
            for i, col in enumerate(columns[1:], start=1):
                ttk.Label(win, text=col).grid(row=i, column=0)
                e = ttk.Entry(win, width=40)
                e.insert(0, values[i])
                e.grid(row=i, column=1)
                entries.append((col, e))

            def save():
                conn = db_connect()
                cur = conn.cursor()
                set_clause = ", ".join([f"{c.lower()}=?" for c, _ in entries])
                new_vals = [e.get() for _, e in entries]
                cur.execute(
                    f"UPDATE {table_name} SET {set_clause} WHERE {id_column}=?",
                    (*new_vals, record_id)
                )
                conn.commit()
                conn.close()
                win.destroy()
                reload_data()

            ttk.Button(win, text="Speichern", command=save).grid(row=99, columnspan=2)

        def export_csv():
            with open(f"{title}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                for rid in table.get_children():
                    writer.writerow(table.item(rid)['values'])

        def export_pdf():
            doc = SimpleDocTemplate(f"{title}.pdf", pagesize=A4)
            data = [columns]
            for rid in table.get_children():
                data.append(table.item(rid)['values'])
            doc.build([Table(data)])

        btns = ttk.Frame(window)
        btns.pack(pady=10)

        ttk.Button(btns, text="Reload", command=reload_data).pack(side="left", padx=5)
        ttk.Button(btns, text="Bearbeiten", command=edit_entry).pack(side="left", padx=5)
        ttk.Button(btns, text="Löschen", command=delete_entry).pack(side="left", padx=5)
        ttk.Button(btns, text="Export CSV", command=export_csv).pack(side="left", padx=5)
        ttk.Button(btns, text="Export PDF", command=export_pdf).pack(side="left", padx=5)

    def open_students(self):
        self.open_table(
            "Schülerliste",
            "SELECT id, klasse, name, choice1, choice2, choice3 FROM students",
            ("ID", "Klasse", "Name", "choice1", "choice2", "choice3"),
            "students",
            "id"
        )

    def open_groups(self):
        self.open_table(
            "Gruppenliste",
            "SELECT id, name FROM groups",
            ("ID", "name"),
            "groups",
            "id"
        )

    def open_assignments(self):
        self.open_table(
            "Zuweisungsliste",
            """
            SELECT s.name, s.klasse, a.group_id, g.name
            FROM assignments a
                     JOIN students s ON a.student_id=s.id
                     JOIN groups g ON a.group_id=g.id
            """,
            ("Name", "Klasse", "GruppeID", "Gruppenname"),
            "assignments",
            None
        )


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Projektwahl")
        self.geometry("700x450")

        self.current_theme = tk.StringVar(value="dark")
        apply_dark_mode(self)

        self.status = tk.StringVar(value="Bereit")

        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_checkbutton(
            label="Dark Mode",
            onvalue="dark",
            offvalue="light",
            variable=self.current_theme,
            command=self.toggle_theme
        )
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.quit)

        navigate_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Navigieren", menu=navigate_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(
            label="Über",
            command=lambda: messagebox.showinfo(
                "Über",
                "Made with Python\nby Yann Peroche"
            )
        )
        help_menu.add_command(
            label="Support",
            command=lambda: messagebox.showinfo(
                "Support",
                "E-Mail: yann@peroche.de\nmit Betreff: '11er Projekt'"
            )
        )


        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=5, pady=5)

        self.tabs.add(GroupsTab(self.tabs, self.status), text="Gruppen")
        self.tabs.add(StudentsTab(self.tabs, self.status), text="Schüler")
        self.tabs.add(GenerateTab(self.tabs, self.status), text="Generieren")
        self.tabs.add(EditTab(self.tabs, self.status), text="Bearbeiten")

        navigate_menu.add_command(label="Gruppen", command=lambda: self.tabs.select(0))
        navigate_menu.add_command(label="Schüler", command=lambda: self.tabs.select(1))
        navigate_menu.add_command(label="Generieren", command=lambda: self.tabs.select(2))
        navigate_menu.add_command(label="Bearbeiten", command=lambda: self.tabs.select(3))

        ttk.Label(self, textvariable=self.status, anchor="w") \
            .pack(fill="x", side="bottom", padx=5, pady=3)

    def toggle_theme(self):
        if self.current_theme.get() == "dark":
            apply_dark_mode(self)
        else:
            apply_light_mode(self)


if __name__ == "__main__":
    App().mainloop()
