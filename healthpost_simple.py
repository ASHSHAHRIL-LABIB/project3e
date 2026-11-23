import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "healthpost.db")


def connect():
    return sqlite3.connect(DB)


def setup():
    with connect() as db:   
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY, password TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, age INTEGER, phone TEXT);
        CREATE TABLE IF NOT EXISTS medicines(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, stock INTEGER NOT NULL DEFAULT 0,
            threshold INTEGER NOT NULL DEFAULT 10);
        CREATE TABLE IF NOT EXISTS visits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER, medicine_id INTEGER,
            quantity INTEGER, date TEXT DEFAULT CURRENT_DATE);
        """)
        if not db.execute("SELECT 1 FROM users").fetchone():  #.fetchone() gets the first row of the result
            db.execute("INSERT INTO users VALUES (?, ?)", ("admin", "admin"))


class HealthPost:
    def __init__(self, root):
        self.root = root
        root.title("HealthPost Desktop")
        root.geometry("760x480")
        self.login()

    def clear(self):
        for w in self.root.winfo_children(): #returns a list of all the widgets directly inside the window
            w.destroy()

    def login(self):
        self.clear()
        box = ttk.Frame(self.root, padding=30)
        box.pack(expand=True)
        ttk.Label(box, text="HealthPost Login", font=("Arial", 18)).pack(pady=10)
        ttk.Label(box, text="Username").pack()
        self.username = ttk.Entry(box)
        self.username.pack(pady=4)
        ttk.Label(box, text="Password").pack()
        self.password = ttk.Entry(box, show="*")
        self.password.pack(pady=4)
        ttk.Button(box, text="Login", command=self.check_login).pack(pady=10)
        ttk.Label(box, text="First login: admin / admin").pack()

    def check_login(self):
        with connect() as db:
            row = db.execute("SELECT 1 FROM users WHERE username=? AND password=?",
                             (self.username.get(), self.password.get())).fetchone()
        if row:
            self.main()
        else:
            messagebox.showerror("Login failed", "Wrong username or password")

    def main(self):
        self.clear()
        bar = ttk.Frame(self.root, padding=8)
        bar.pack(fill="x") #stretch the Frame horizontally to fill the available width
        ttk.Label(bar, text="HealthPost Desktop", font=("Arial", 16)).pack(side="left")
        

        tabs = ttk.Notebook(self.root)  #create multiple tabs inside one window
        tabs.pack(fill="both", expand=True, padx=8, pady=8)
        self.patient_tab = ttk.Frame(tabs, padding=10)
        self.medicine_tab = ttk.Frame(tabs, padding=10)
        self.dispense_tab = ttk.Frame(tabs, padding=10)
        tabs.add(self.patient_tab, text="Patients")
        tabs.add(self.medicine_tab, text="Medicines")
        tabs.add(self.dispense_tab, text="Dispense")
        self.build_patients()
        self.build_medicines()
        self.build_dispense()

    def table(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        for c in columns:
            tree.heading(c, text=c.title())
            tree.column(c, width=130)
        tree.pack(fill="both", expand=True, pady=8)
        return tree

    def build_patients(self):
        form = ttk.Frame(self.patient_tab)
        form.pack(fill="x")
        self.p_name = ttk.Entry(form, width=22)
        self.p_age = ttk.Entry(form, width=8)
        self.p_phone = ttk.Entry(form, width=16)
        for label, entry in (("Name", self.p_name), ("Age", self.p_age),
                             ("Phone", self.p_phone)):
            ttk.Label(form, text=label).pack(side="left", padx=(0, 4))
            entry.pack(side="left", padx=(0, 10))
        ttk.Button(form, text="Add patient", command=self.add_patient).pack(side="left")
        self.p_tree = self.table(self.patient_tab, ("id", "name", "age", "phone"))
        self.refresh_patients()

    def add_patient(self):
        name = self.p_name.get().strip()
        if not name:
            messagebox.showerror("Missing name", "Enter the patient's name.")
            return
        try:
            age = int(self.p_age.get()) if self.p_age.get() else None
        except ValueError:
            messagebox.showerror("Invalid age", "Age must be a number.")
            return
        with connect() as db:
            db.execute("INSERT INTO patients(name, age, phone) VALUES(?,?,?)",
                       (name, age, self.p_phone.get().strip()))
        self.p_name.delete(0, "end")
        self.p_age.delete(0, "end")
        self.p_phone.delete(0, "end")
        self.refresh_patients()
        self.refresh_dispense()

    def refresh_patients(self):
        self.p_tree.delete(*self.p_tree.get_children())
        with connect() as db:
            for row in db.execute("SELECT id,name,age,phone FROM patients ORDER BY id DESC"):
                self.p_tree.insert("", "end", values=row)

    def build_medicines(self):
        form = ttk.Frame(self.medicine_tab)
        form.pack(fill="x")
        self.m_name = ttk.Entry(form, width=25)
        self.m_stock = ttk.Entry(form, width=8)
        self.m_threshold = ttk.Entry(form, width=8)
        self.m_stock.insert(0, "0")
        self.m_threshold.insert(0, "10")
        for label, entry in (("Medicine", self.m_name), ("Stock", self.m_stock),
                             ("Low-stock limit", self.m_threshold)):
            ttk.Label(form, text=label).pack(side="left", padx=(0, 4))
            entry.pack(side="left", padx=(0, 10))
        ttk.Button(form, text="Add medicine", command=self.add_medicine).pack(side="left")
        self.m_tree = self.table(self.medicine_tab, ("id", "name", "stock", "threshold"))
        self.refresh_medicines()

    def add_medicine(self):
        name = self.m_name.get().strip()
        try:
            stock, threshold = int(self.m_stock.get()), int(self.m_threshold.get())
            if not name or stock < 0 or threshold < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid data", "Enter a name and non-negative whole numbers.")
            return
        with connect() as db:
            db.execute("INSERT INTO medicines(name,stock,threshold) VALUES(?,?,?)",
                       (name, stock, threshold))
        self.m_name.delete(0, "end")
        self.refresh_medicines()
        self.refresh_dispense()

    def refresh_medicines(self):
        self.m_tree.delete(*self.m_tree.get_children())
        with connect() as db:
            for row in db.execute("SELECT id,name,stock,threshold FROM medicines ORDER BY name"):
                status = " LOW STOCK" if row[2] <= row[3] else ""
                self.m_tree.insert("", "end", values=(row[0], row[1] + status, row[2], row[3]))

    def build_dispense(self):
        form = ttk.Frame(self.dispense_tab)
        form.pack(fill="x", pady=8)
        ttk.Label(form, text="Patient").pack(side="left")
        self.d_patient = ttk.Combobox(form, state="readonly", width=24)
        self.d_patient.pack(side="left", padx=6)
        ttk.Label(form, text="Medicine").pack(side="left")
        self.d_medicine = ttk.Combobox(form, state="readonly", width=24)
        self.d_medicine.pack(side="left", padx=6)
        ttk.Label(form, text="Quantity").pack(side="left")
        self.d_qty = ttk.Entry(form, width=6)
        self.d_qty.pack(side="left", padx=6)
        ttk.Button(form, text="Dispense", command=self.dispense).pack(side="left")
        self.v_tree = self.table(self.dispense_tab, ("date", "patient", "medicine", "quantity"))
        self.refresh_dispense()

    def refresh_dispense(self):
        if not hasattr(self, "d_patient"):
            return
        with connect() as db:
            self.patient_rows = db.execute("SELECT id,name FROM patients ORDER BY name").fetchall()
            self.medicine_rows = db.execute("SELECT id,name FROM medicines ORDER BY name").fetchall()
            self.d_patient["values"] = [f"{i} - {n}" for i, n in self.patient_rows]
            self.d_medicine["values"] = [f"{i} - {n}" for i, n in self.medicine_rows]
            self.v_tree.delete(*self.v_tree.get_children())
            rows = db.execute("""SELECT visits.date, patients.name, medicines.name, visits.quantity
                FROM visits JOIN patients ON patients.id=visits.patient_id
                JOIN medicines ON medicines.id=visits.medicine_id ORDER BY visits.id DESC""")
            for row in rows:
                self.v_tree.insert("", "end", values=row)

    def dispense(self):
        try:
            patient_id = int(self.d_patient.get().split(" - ")[0])
            medicine_id = int(self.d_medicine.get().split(" - ")[0])
            qty = int(self.d_qty.get())
            if qty <= 0:
                raise ValueError
        except (ValueError, IndexError):
            messagebox.showerror("Invalid data", "Choose a patient and medicine, and enter a positive quantity.")
            return
        with connect() as db:
            row = db.execute("SELECT stock FROM medicines WHERE id=?", (medicine_id,)).fetchone()
            if not row or row[0] < qty:
                messagebox.showerror("Not enough stock", "There is not enough medicine in stock.")
                return
            db.execute("UPDATE medicines SET stock=stock-? WHERE id=?", (qty, medicine_id))
            db.execute("INSERT INTO visits(patient_id,medicine_id,quantity) VALUES(?,?,?)",
                       (patient_id, medicine_id, qty))
        self.d_qty.delete(0, "end")
        self.refresh_medicines()
        self.refresh_dispense()
        messagebox.showinfo("Done", "Dispensing recorded.")


if __name__ == "__main__":    #useful because you can import functions and classes from a file without accidentally executing its main application code
    setup()
    root = tk.Tk()
    HealthPost(root)
    root.mainloop()
