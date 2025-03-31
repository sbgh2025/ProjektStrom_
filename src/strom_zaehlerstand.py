import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import os
import logging

# Setze das Arbeitsverzeichnis auf das Verzeichnis des Skripts
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Logging einrichten
logging.basicConfig(filename='/tmp/zaehlerstand_app.log', level=logging.DEBUG)


def get_db_connection():
    db_path = 'meine_datenbank.db'
    if not os.path.exists(db_path):
        logging.error(f"Die Datenbank '{db_path}' existiert nicht.")
        messagebox.showerror("Datenbankfehler", f"Die Datenbank '{db_path}' wurde nicht gefunden.")
        return None
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Verbinden mit der Datenbank: {e}")
        messagebox.showerror("Datenbankfehler", "Fehler beim Verbinden mit der Datenbank.")
        return None


def get_zaehlerstaende_zwischen_daten(von_datum, bis_datum):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rowid, datum, zaehlerstand FROM tbl_zaehlerstand
        WHERE datum BETWEEN ? AND ? ORDER BY datum
    ''', (von_datum, bis_datum))
    result = cursor.fetchall()
    conn.close()
    return result


def insert_zaehlerstand(datum, zaehlerstand):
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tbl_zaehlerstand (datum, zaehlerstand) VALUES (?, ?)', (datum, zaehlerstand))
    conn.commit()
    conn.close()


def delete_zaehlerstand_from_db(rowid):
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tbl_zaehlerstand WHERE rowid = ?', (rowid,))
    conn.commit()
    conn.close()
    return True


class ZaehlerstandApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zählerstand Eingabe")
        self.geometry("600x400")

        self.layout = tk.Frame(self)
        self.layout.pack(padx=20, pady=20)

        self.datum_label_input = tk.Label(self.layout, text="Datum des Zählerstands (YYYY-MM-DD):")
        self.datum_label_input.pack()
        self.datum_input = tk.Entry(self.layout)
        self.datum_input.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.datum_input.pack()

        self.zaehlerstand_label_input = tk.Label(self.layout, text="Zählerstand (kWh):")
        self.zaehlerstand_label_input.pack()
        self.zaehlerstand_input = tk.Entry(self.layout)
        self.zaehlerstand_input.pack()

        self.save_button = tk.Button(self.layout, text="Speichern", command=self.save_zaehlerstand)
        self.save_button.pack(pady=5)

        self.von_datum_label = tk.Label(self.layout, text="Startdatum (YYYY-MM-DD):")
        self.von_datum_label.pack()
        self.von_datum_input = tk.Entry(self.layout)
        self.von_datum_input.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.von_datum_input.pack()

        self.bis_datum_label = tk.Label(self.layout, text="Enddatum (YYYY-MM-DD):")
        self.bis_datum_label.pack()
        self.bis_datum_input = tk.Entry(self.layout)
        self.bis_datum_input.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.bis_datum_input.pack()

        self.update_button = tk.Button(self.layout, text="Zählerstände anzeigen",
                                       command=self.open_zaehlerstand_fenster)
        self.update_button.pack(pady=5)

    def save_zaehlerstand(self):
        datum = self.datum_input.get()
        zaehlerstand_input = self.zaehlerstand_input.get()
        try:
            datetime.strptime(datum, "%Y-%m-%d")
            zaehlerstand = float(zaehlerstand_input)
            insert_zaehlerstand(datum, zaehlerstand)
            self.datum_input.delete(0, tk.END)
            self.zaehlerstand_input.delete(0, tk.END)
            self.open_zaehlerstand_fenster()
        except ValueError:
            messagebox.showerror("Ungültige Eingabe", "Bitte korrektes Datum und eine Zahl eingeben.")

    def open_zaehlerstand_fenster(self):
        zaehlerstand_fenster = tk.Toplevel(self)
        zaehlerstand_fenster.title("Zählerstände im Zeitraum")
        zaehlerstand_fenster.geometry("600x400")

        von_datum = self.von_datum_input.get()
        bis_datum = self.bis_datum_input.get()

        frame = tk.Frame(zaehlerstand_fenster)
        frame.pack(padx=20, pady=20)

        table = ttk.Treeview(frame, columns=("ID", "Datum", "Zählerstand"), show="headings")
        table.heading("ID", text="ID")
        table.heading("Datum", text="Datum")
        table.heading("Zählerstand", text="Zählerstand (kWh)")
        table.pack(fill=tk.BOTH, expand=True)

        zaehlerstaende = get_zaehlerstaende_zwischen_daten(von_datum, bis_datum)
        for rowid, datum, zaehlerstand in zaehlerstaende:
            table.insert("", "end", values=(rowid, datum, zaehlerstand))

        def delete_zaehlerstand():
            selected_item = table.selection()
            if selected_item:
                rowid = table.item(selected_item[0])["values"][0]
                if delete_zaehlerstand_from_db(rowid):
                    table.delete(selected_item)
                    messagebox.showinfo("Erfolg", "Zählerstand erfolgreich gelöscht.")
                else:
                    messagebox.showerror("Fehler", "Löschen fehlgeschlagen.")

        delete_button = tk.Button(frame, text="Löschen", command=delete_zaehlerstand)
        delete_button.pack(pady=5)
        close_button = tk.Button(frame, text="Schließen", command=zaehlerstand_fenster.destroy)
        close_button.pack(pady=5)


def main():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_zaehlerstand (
                datum DATE,
                zaehlerstand REAL
            )
        ''')
        conn.commit()
        conn.close()
    app = ZaehlerstandApp()
    app.mainloop()


if __name__ == '__main__':
    main()
