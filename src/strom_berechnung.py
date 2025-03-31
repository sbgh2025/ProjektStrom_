import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
import logging

# Setze das Arbeitsverzeichnis auf das Verzeichnis des Skripts
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Logging einrichten (mit lokalem Logfile im aktuellen Verzeichnis)
logging.basicConfig(filename='stromabrechnung_app.log', level=logging.DEBUG)

# Datenbankname als Konstante
DB_NAME = 'meine_datenbank.db'

# Funktion, um die Verbindung zur SQLite-Datenbank herzustellen
def get_db_connection():
    try:
        # Überprüfen, ob die Datenbankdatei existiert
        if not os.path.exists(DB_NAME):
            logging.error(f"Datenbank '{DB_NAME}' existiert nicht!")
            messagebox.showerror("Datenbank nicht gefunden", f"Die Datenbank '{DB_NAME}' existiert nicht.")
            return None
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        logging.error(f"Fehler beim Verbinden mit der Datenbank: {e}")
        messagebox.showerror("Datenbankfehler", "Fehler beim Verbinden mit der Datenbank.")
        return None

class StromabrechnungApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Stromabrechnung")
        self.geometry("500x500")

        self.init_ui()

    def init_ui(self):
        layout = tk.Frame(self)
        layout.pack(padx=20, pady=20, fill="both", expand=True)

        # Eingabefeld für Startdatum
        self.start_date_label = tk.Label(layout, text="Startdatum (YYYY-MM-DD):")
        self.start_date_label.grid(row=0, column=0, sticky="w")
        self.start_date_input = tk.Entry(layout)
        self.start_date_input.insert(0, "2024-01-01")
        self.start_date_input.grid(row=0, column=1)

        # Eingabefeld für Enddatum
        self.end_date_label = tk.Label(layout, text="Enddatum (YYYY-MM-DD):")
        self.end_date_label.grid(row=1, column=0, sticky="w")
        self.end_date_input = tk.Entry(layout)
        self.end_date_input.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.end_date_input.grid(row=1, column=1)

        # Berechnungsbutton
        self.calc_button = tk.Button(layout, text="Berechnen", command=self.berechnen)
        self.calc_button.grid(row=2, columnspan=2, pady=10)

        # Ergebnisanzeige
        self.result_label = tk.Label(layout, text="Ergebnis:")
        self.result_label.grid(row=3, columnspan=2, pady=10)

    def berechnen(self):
        start_datum_str = self.start_date_input.get()
        end_datum_str = self.end_date_input.get()

        try:
            # Datum validieren
            start_datum = datetime.strptime(start_datum_str, "%Y-%m-%d")
            end_datum = datetime.strptime(end_datum_str, "%Y-%m-%d")

            # Berechnungen durchführen
            eingabedatum = end_datum.date()

            conn = get_db_connection()
            if conn is None:
                return  # Wenn keine Verbindung zur DB möglich ist, breche ab

            cursor = conn.cursor()

            # Schritt 1: Start- und Endzählerstand aus tbl_zaehlerstand holen
            cursor.execute("""
                SELECT datum, zaehlerstand 
                FROM tbl_zaehlerstand
                WHERE datum <= ?
                ORDER BY datum
            """, (eingabedatum,))
            zaehlerstaende = cursor.fetchall()

            verbrauch = 0
            if zaehlerstaende:
                start_zaehlerstand = zaehlerstaende[0][1]
                end_zaehlerstand = zaehlerstaende[-1][1]
                verbrauch = end_zaehlerstand - start_zaehlerstand

            # Schritt 2: Einzahlungen bis zum angegebenen Datum
            cursor.execute("""
                SELECT SUM(einzahlungen)
                FROM tbl_einzahlungen
                WHERE datum <= ?
            """, (eingabedatum,))
            einzahlungen = cursor.fetchone()[0] or 0

            # Schritt 3: Preis pro kWh und monatlicher Grundpreis
            cursor.execute("""
                SELECT kwh_preis, grundpreis
                FROM tbl_berechgrundl
                WHERE datum_von <= ? AND datum_bis >= ?
                LIMIT 1
            """, (eingabedatum, eingabedatum))
            result = cursor.fetchone()

            if result:
                kwh_preis, grundpreis = result
            else:
                self.result_label.config(text="Daten für die Berechnung fehlen.")
                conn.close()
                return

            # Berechnungen durchführen
            verbrauchskosten = verbrauch * kwh_preis / 100
            grundpreis_pro_tag = grundpreis / 30
            tage_im_zeitraum = (end_datum - start_datum).days + 1  # Berechnung der Tage im Zeitraum
            grundpreis_berechnet = grundpreis_pro_tag * tage_im_zeitraum
            gesamtbetrag = verbrauchskosten + grundpreis_berechnet
            saldo = einzahlungen - gesamtbetrag

            # Schrittweise Ergebnisse ausgeben
            result_text = (
                f"1. Berechnete Tage im Zeitraum: {tage_im_zeitraum} Tage\n"  # Anzeigen der Tage
                f"2. Gesamter Verbrauch: {verbrauch} kWh\n"
                f"3. Gesamtkosten des Verbrauchs: {verbrauchskosten:.2f} EUR\n"
                f"4. Gesamtsumme Grundpreis: {grundpreis_berechnet:.2f} EUR\n"
                f"5. Gesamtsumme (Verbrauchskosten + Grundpreis): {gesamtbetrag:.2f} EUR\n"
                f"6. Gesamte Einzahlungen: {einzahlungen:.2f} EUR\n"
                f"7. Saldo (Einzahlungen - Gesamtbetrag): {saldo:.2f} EUR\n"

            )

            # Ergebnis anzeigen
            self.result_label.config(text=result_text)

            conn.close()

        except ValueError:
            messagebox.showerror("Ungültige Eingabe", "Bitte geben Sie ein gültiges Datum im Format (YYYY-MM-DD) ein.")
            logging.error(f"Fehler bei der Eingabe: Startdatum: {start_datum_str}, Enddatum: {end_datum_str}")
        except sqlite3.Error as e:
            messagebox.showerror("Datenbankfehler", "Es gab einen Fehler bei der Datenbankabfrage.")
            logging.error(f"SQLite-Fehler: {e}")
        except Exception as e:
            messagebox.showerror("Unbekannter Fehler", "Es gab einen unerwarteten Fehler.")
            logging.error(f"Unbekannter Fehler: {e}")

# Main-Funktion zum Starten der App
def main():
    # Überprüfen, ob die Datenbank existiert
    if not os.path.exists(DB_NAME):
        messagebox.showerror("Datenbank nicht gefunden", f"Die Datenbank {DB_NAME} existiert nicht.")
        logging.error(f"Datenbank '{DB_NAME}' existiert nicht!")
        return

    app = StromabrechnungApp()
    app.mainloop()

if __name__ == '__main__':
    main()
