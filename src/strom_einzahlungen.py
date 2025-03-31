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
logging.basicConfig(filename='/tmp/einzahlungen_app.log', level=logging.DEBUG)


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


# Funktion, um alle Einzahlungen zwischen zwei Daten zu holen
def get_einzahlungen_zwischen_daten(von_datum, bis_datum):
    conn = get_db_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    cursor.execute('''
        SELECT rowid, datum, einzahlungen
        FROM tbl_einzahlungen
        WHERE datum BETWEEN ? AND ?
        ORDER BY datum
    ''', (von_datum, bis_datum))

    result = cursor.fetchall()
    conn.close()
    return result


# Funktion, um eine neue Einzahlung zu speichern
def insert_einzahlung(datum, einzahlungen):
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute('INSERT INTO tbl_einzahlungen (datum, einzahlungen) VALUES (?, ?)', (datum, einzahlungen))
    conn.commit()
    conn.close()


# Funktion, um einen Datensatz zu löschen
def delete_einzahlung_from_db(rowid):
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    cursor.execute('DELETE FROM tbl_einzahlungen WHERE rowid = ?', (rowid,))
    conn.commit()
    conn.close()

    return True


# Tkinter GUI-Klasse
class EinzahlungenApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Fenster konfigurieren
        self.title("Einzahlungen Eingabe")
        self.geometry("600x400")

        # Layouts
        self.layout = tk.Frame(self)
        self.layout.pack(padx=20, pady=20)

        # Eingabefelder für Datum und Betrag
        self.datum_label_input = tk.Label(self.layout, text="Datum der Einzahlung (YYYY-MM-DD):")
        self.datum_label_input.pack()
        self.datum_input = tk.Entry(self.layout)
        self.datum_input.insert(0, datetime.today().strftime('%Y-%m-%d'))  # Default auf das heutige Datum
        self.datum_input.pack()

        # Betrag Eingabe
        self.betrag_label_input = tk.Label(self.layout, text="Betrag (€):")
        self.betrag_label_input.pack()
        self.einzahlung_input = tk.Entry(self.layout)
        self.einzahlung_input.pack()

        # Buttons
        self.save_button = tk.Button(self.layout, text="Speichern", command=self.save_einzahlung)
        self.save_button.pack(pady=5)

        # Eingabefelder für Start- und Enddatum (Anzeige-Optionen)
        self.von_datum_label = tk.Label(self.layout, text="Startdatum (YYYY-MM-DD):")
        self.von_datum_label.pack()
        self.von_datum_input = tk.Entry(self.layout)
        self.von_datum_input.insert(0, datetime.today().strftime('%Y-%m-%d'))  # Default auf das heutige Datum
        self.von_datum_input.pack()

        self.bis_datum_label = tk.Label(self.layout, text="Enddatum (YYYY-MM-DD):")
        self.bis_datum_label.pack()
        self.bis_datum_input = tk.Entry(self.layout)
        self.bis_datum_input.insert(0, datetime.today().strftime('%Y-%m-%d'))  # Default auf das heutige Datum
        self.bis_datum_input.pack()

        # Button zum Einzahlungen anzeigen
        self.update_button = tk.Button(self.layout, text="Einzahlungen im Zeitraum anzeigen", command=self.open_einzahlungen_fenster)
        self.update_button.pack(pady=5)

    def save_einzahlung(self):
        datum = self.datum_input.get()  # Hole das Datum der Einzahlung
        einzahlung_input = self.einzahlung_input.get()

        try:
            # Datum validieren
            date_obj = datetime.strptime(datum, "%Y-%m-%d")  # Stelle sicher, dass das Datum im richtigen Format ist

            # Betrag validieren
            einzahlung = float(einzahlung_input)
            if einzahlung <= 0:
                raise ValueError("Der Betrag muss positiv sein.")

            # Einzahlung speichern
            insert_einzahlung(datum, einzahlung)

            # Felder leeren
            self.datum_input.delete(0, tk.END)
            self.einzahlung_input.delete(0, tk.END)

            # Einzahlungen neu laden
            self.open_einzahlungen_fenster()

        except ValueError as e:
            messagebox.showerror("Ungültige Eingabe",
                                 f"Bitte geben Sie ein korrektes Datum und einen Betrag ein. Fehler: {e}")

    def open_einzahlungen_fenster(self):
        einzahlungen_fenster = tk.Toplevel(self)
        einzahlungen_fenster.title("Einzahlungen im Zeitraum")
        einzahlungen_fenster.geometry("600x400")

        # Hole Start- und Enddatum für den Zeitraum
        von_datum_str = self.von_datum_input.get()
        bis_datum_str = self.bis_datum_input.get()

        try:
            von_date_obj = datetime.strptime(von_datum_str, "%Y-%m-%d")
            bis_date_obj = datetime.strptime(bis_datum_str, "%Y-%m-%d")

            von_datum = von_date_obj.date()
            bis_datum = bis_date_obj.date()

            # Frame für das Fenster
            frame = tk.Frame(einzahlungen_fenster)
            frame.pack(padx=20, pady=20)

            # Label für Löschbestätigung
            self.delete_message_label = tk.Label(frame, text="", fg="green")
            self.delete_message_label.pack()

            # Treeview für die Einzahlungen
            table = ttk.Treeview(frame, columns=("ID", "Datum", "Betrag"), show="headings")
            table.heading("ID", text="ID")
            table.heading("Datum", text="Datum")
            table.heading("Betrag", text="Betrag (€)")
            table.pack(pady=10, fill=tk.BOTH, expand=True)

            # Hole die Einzahlungen im angegebenen Zeitraum aus der Datenbank
            einzahlungen = get_einzahlungen_zwischen_daten(von_datum, bis_datum)

            for rowid, datum, einzahlung in einzahlungen:
                table.insert("", "end", values=(rowid, datum, einzahlung))

            # Funktion, um einen Datensatz zu löschen
            def delete_einzahlung():
                selected_item = table.selection()
                if selected_item:
                    rowid = table.item(selected_item[0])["values"][0]  # Hole den rowid der selektierten Zeile
                    if delete_einzahlung_from_db(rowid):  # Lösche den Datensatz in der DB
                        table.delete(selected_item)  # Entferne die Zeile aus der Anzeige
                        self.delete_message_label.config(text="Löschvorgang erfolgreich", fg="green")
                    else:
                        self.delete_message_label.config(text="Fehler beim Löschen des Datensatzes", fg="red")
                else:
                    self.delete_message_label.config(text="Bitte wählen Sie einen Datensatz zum Löschen aus", fg="red")

            # Button zum Löschen der ausgewählten Einzahlung
            delete_button = tk.Button(frame, text="Löschen", command=delete_einzahlung)
            delete_button.pack(pady=5)

            # Button zum Schließen des Fensters
            close_button = tk.Button(frame, text="Fenster schließen", command=einzahlungen_fenster.destroy)
            close_button.pack(pady=5)

        except ValueError:
            messagebox.showerror("Ungültige Eingabe", "Bitte geben Sie gültige Daten im Format (YYYY-MM-DD) ein.")


# Main-Funktion zum Starten der App
def main():
    # Versuchen, eine Verbindung zur Datenbank herzustellen
    conn = get_db_connection()
    if conn is None:
        return  # Wenn keine Verbindung möglich ist, das Programm beenden

    # Sicherstellen, dass die Tabelle 'tbl_einzahlungen' existiert
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_einzahlungen (
            datum DATE,
            einzahlungen INTEGER
        )
    ''')
    conn.commit()
    conn.close()

    # GUI starten
    app = EinzahlungenApp()
    app.mainloop()


if __name__ == '__main__':
    main()
