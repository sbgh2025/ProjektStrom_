import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import os
import logging

# Arbeitsverzeichnis setzen
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Logging einrichten
logging.basicConfig(filename='/tmp/zaehlerstand_app.log', level=logging.DEBUG)

# Funktion, um die Verbindung zur SQLite-Datenbank herzustellen
def get_db_connection():
    db_path = 'meine_datenbank.db'

    # Überprüfen, ob die Datenbankdatei existiert
    if not os.path.exists(db_path):
        logging.error(f"Die Datenbank '{db_path}' existiert nicht.")
        messagebox.showerror("Datenbankfehler", f"Die Datenbank '{db_path}' wurde nicht gefunden.")
        return None

    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Verbinden mit der Datenbank: {e}")
        messagebox.showerror("Datenbankfehler", "Fehler beim Verbinden mit der Datenbank.")
        return None

# Funktion, um alle Datensätze aus tbl_berechgrundl zu holen
def get_berechgrundl_daten():
    conn = get_db_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    cursor.execute('SELECT datum_von, datum_bis, grundpreis, kwh_preis FROM tbl_berechgrundl ORDER BY datum_von')
    result = cursor.fetchall()
    conn.close()
    return result

# Funktion, um einen Datensatz aus tbl_berechgrundl zu löschen
def delete_berechgrundl_from_db(datum_von, datum_bis):
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    cursor.execute('DELETE FROM tbl_berechgrundl WHERE datum_von = ? AND datum_bis = ?', (datum_von, datum_bis))
    conn.commit()
    conn.close()

    return True

# Tkinter GUI-Klasse
class BerechGrundlApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialisierung der GUI-Komponenten
        self.title("Grundpreis und kWh-Preis Eingabe")
        self.geometry("700x500")

        # Layout
        self.layout = tk.Frame(self)
        self.layout.pack(padx=20, pady=20)

        # Label für das Start- und Enddatum
        self.datum_von_label = tk.Label(self.layout, text="Datum von (YYYY-MM-DD):")
        self.datum_von_label.grid(row=0, column=0, sticky="e", pady=5)
        self.datum_von_input = tk.Entry(self.layout)
        self.datum_von_input.grid(row=0, column=1, pady=5)

        self.datum_bis_label = tk.Label(self.layout, text="Datum bis (YYYY-MM-DD):")
        self.datum_bis_label.grid(row=1, column=0, sticky="e", pady=5)
        self.datum_bis_input = tk.Entry(self.layout)
        self.datum_bis_input.grid(row=1, column=1, pady=5)

        # Label und Eingabefeld für den Grundpreis
        self.grundpreis_label = tk.Label(self.layout, text="Monatlicher Grundpreis (€):")
        self.grundpreis_label.grid(row=2, column=0, sticky="e", pady=5)
        self.grundpreis_input = tk.Entry(self.layout)
        self.grundpreis_input.grid(row=2, column=1, pady=5)

        # Label und Eingabefeld für den kWh-Preis
        self.kwh_preis_label = tk.Label(self.layout, text="kWh-Preis (Cent/kWh):")
        self.kwh_preis_label.grid(row=3, column=0, sticky="e", pady=5)
        self.kwh_preis_input = tk.Entry(self.layout)
        self.kwh_preis_input.grid(row=3, column=1, pady=5)

        # Hinweis, dass ein Punkt verwendet werden muss
        self.hinweis_label = tk.Label(self.layout, text="Hinweis: Bitte verwenden Sie einen Punkt (.) anstelle eines Kommas (,)", fg="blue")
        self.hinweis_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Buttons zum Speichern und Anzeigen
        self.buttons_frame = tk.Frame(self.layout)
        self.buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)

        # Button zum Speichern der Daten
        self.save_button = tk.Button(self.buttons_frame, text="Speichern", command=self.save_berechgrundl)
        self.save_button.grid(row=0, column=0, padx=10)

        # Button zum Anzeigen der Datensätze
        self.show_button = tk.Button(self.buttons_frame, text="Datensätze anzeigen", command=self.update_datensaetze)
        self.show_button.grid(row=0, column=1, padx=10)

        # Button zum Löschen eines Datensatzes
        self.delete_button = tk.Button(self.buttons_frame, text="Löschen", command=self.delete_berechgrundl)
        self.delete_button.grid(row=0, column=2, padx=10)

        # Treeview für die Anzeige der Datensätze
        self.table = ttk.Treeview(self, columns=("Datum von", "Datum bis", "Grundpreis", "kWh-Preis"), show="headings")
        self.table.heading("Datum von", text="Datum von")
        self.table.heading("Datum bis", text="Datum bis")
        self.table.heading("Grundpreis", text="Grundpreis (€)")
        self.table.heading("kWh-Preis", text="kWh-Preis (Cent/kWh)")
        self.table.pack(pady=10)

    def save_berechgrundl(self):
        datum_von = self.datum_von_input.get()
        datum_bis = self.datum_bis_input.get()
        grundpreis_input = self.grundpreis_input.get()
        kwh_preis_input = self.kwh_preis_input.get()

        try:
            # Datum validieren (Format: YYYY-MM-DD)
            datetime.strptime(datum_von, "%Y-%m-%d")
            datetime.strptime(datum_bis, "%Y-%m-%d")

            # Komma durch Punkt ersetzen, falls vorhanden
            grundpreis_input = grundpreis_input.replace(",", ".")
            kwh_preis_input = kwh_preis_input.replace(",", ".")

            # Preiswerte validieren (sollten Zahlen sein)
            grundpreis = float(grundpreis_input)
            kwh_preis = float(kwh_preis_input)

            # Daten in die Datenbank einfügen
            self.insert_berechgrundl(datum_von, datum_bis, grundpreis, kwh_preis)

            # Felder nach dem Speichern leeren
            self.datum_von_input.delete(0, tk.END)
            self.datum_bis_input.delete(0, tk.END)
            self.grundpreis_input.delete(0, tk.END)
            self.kwh_preis_input.delete(0, tk.END)

            messagebox.showinfo("Erfolg", "Die Daten wurden erfolgreich gespeichert!")

            # Datensätze nach dem Speichern aktualisieren
            self.update_datensaetze()

        except ValueError:
            messagebox.showerror("Ungültige Eingabe", "Bitte geben Sie gültige Daten ein!")

    def insert_berechgrundl(self, datum_von, datum_bis, grundpreis, kwh_preis):
        conn = get_db_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tbl_berechgrundl (datum_von, datum_bis, grundpreis, kwh_preis)
            VALUES (?, ?, ?, ?)
        ''', (datum_von, datum_bis, grundpreis, kwh_preis))
        conn.commit()
        conn.close()

    def update_datensaetze(self):
        # Alle Datensätze aus der Datenbank holen
        datensaetze = get_berechgrundl_daten()

        # Leere die Tabelle
        for row in self.table.get_children():
            self.table.delete(row)

        # Füge die Datensätze in die Tabelle ein
        for datum_von, datum_bis, grundpreis, kwh_preis in datensaetze:
            self.table.insert("", "end", values=(datum_von, datum_bis, grundpreis, kwh_preis))

    def delete_berechgrundl(self):
        selected_item = self.table.selection()
        if selected_item:
            datum_von = self.table.item(selected_item[0])["values"][0]
            datum_bis = self.table.item(selected_item[0])["values"][1]

            # Löschen des Datensatzes aus der Datenbank
            if delete_berechgrundl_from_db(datum_von, datum_bis):
                # Tabelle nach dem Löschen aktualisieren
                self.update_datensaetze()
                messagebox.showinfo("Erfolg", "Der Datensatz wurde erfolgreich gelöscht!")
            else:
                messagebox.showerror("Fehler", "Fehler beim Löschen des Datensatzes.")
        else:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie einen Datensatz zum Löschen aus.")

# Main-Funktion zum Starten der App
def main():
    app = BerechGrundlApp()
    app.mainloop()

if __name__ == '__main__':
    main()
