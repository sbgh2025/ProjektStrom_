import sqlite3
import tkinter as tk
from tkinter import messagebox

class StromabrechnungApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Datenbank erstellen und befüllen")
        self.geometry("400x300")

        self.init_ui()

    def init_ui(self):
        # Layout für Buttons und Textanzeigen
        layout = tk.Frame(self)
        layout.pack(padx=20, pady=20, fill="both", expand=True)

        # Button zum Erstellen der Datenbank und Tabellen
        self.create_db_button = tk.Button(layout, text="Datenbank erstellen", command=self.create_db)
        self.create_db_button.grid(row=0, columnspan=2, pady=10)

        # Button zum Einfügen von Beispiel-Daten
        self.insert_data_button = tk.Button(layout, text="Beispiel-Daten einfügen", command=self.insert_sample_data)
        self.insert_data_button.grid(row=1, columnspan=2, pady=10)

        # Anzeige für Statusnachrichten
        self.status_label = tk.Label(layout, text="Warten auf Eingaben...", justify="left")
        self.status_label.grid(row=2, columnspan=2, pady=10)

    def create_db(self):
        try:
            # Verbindung zur SQLite-Datenbank herstellen
            conn = sqlite3.connect('meine_datenbank.db')

            # Ein Cursor-Objekt erstellen
            cursor = conn.cursor()

            # Tabellen erstellen, falls sie noch nicht existieren
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tbl_zaehlerstand (
                    datum DATE,
                    zaehlerstand INTEGER
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tbl_einzahlungen (
                    datum DATE,
                    einzahlungen INTEGER
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tbl_berechgrundl (
                    datum_von DATE,
                    datum_bis DATE,
                    grundpreis REAL,
                    kwh_preis REAL
                )
            ''')

            # Änderungen speichern
            conn.commit()

            # Verbindung zur Datenbank schließen
            conn.close()

            # Erfolgsmeldung anzeigen
            self.status_label.config(text="Datenbank und Tabellen wurden erfolgreich erstellt.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der Datenbank: {str(e)}")

    def insert_sample_data(self):
        try:
            # Verbindung zur SQLite-Datenbank herstellen
            conn = sqlite3.connect('meine_datenbank.db')
            cursor = conn.cursor()

            # Beispiel-Daten für tbl_berechnungsgrundl
            cursor.execute('''
                INSERT INTO tbl_berechgrundl (datum_von, datum_bis, grundpreis, kwh_preis)
                VALUES ('2024-01-01', '2024-12-31', 10.00, 10)
            ''')

            # Beispiel-Daten für tbl_zaehlerstand
            cursor.execute('''
                INSERT INTO tbl_zaehlerstand (datum, zaehlerstand)
                VALUES ('2024-01-01', 100),
                       ('2024-02-02', 200),
                       ('2024-02-15', 300),
                       ('2024-02-26', 400)
            ''')

            # Beispiel-Daten für tbl_einzahlungen
            cursor.execute('''
                INSERT INTO tbl_einzahlungen (datum, einzahlungen)
                VALUES ('2024-01-01', 30),
                       ('2024-01-03', 30)
            ''')

            # Änderungen speichern
            conn.commit()

            # Verbindung zur Datenbank schließen
            conn.close()

            # Erfolgsmeldung anzeigen
            self.status_label.config(text="Beispiel-Daten wurden erfolgreich eingefügt.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Einfügen der Daten: {str(e)}")

# Main-Funktion zum Starten der App
def main():
    app = StromabrechnungApp()
    app.mainloop()

if __name__ == '__main__':
    main()
