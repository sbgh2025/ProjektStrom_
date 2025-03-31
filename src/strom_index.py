import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# Setze das Arbeitsverzeichnis auf den Ordner, in dem sich strom_index.py befindet
script_dir = os.path.dirname(os.path.abspath(__file__))  # Speichert das Verzeichnis von strom_index.py

# Funktion zum Ausführen eines Python-Skripts
def run_script(script_name):
    try:
        # Setze den vollständigen Pfad zum Skript, das ausgeführt werden soll
        script_path = os.path.join(script_dir, script_name)
        
        # subprocess.run wird verwendet, um das Python-Skript auszuführen
        subprocess.run(["python3", script_path], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Fehler", f"Das Skript {script_name} konnte nicht ausgeführt werden.")
    except FileNotFoundError:
        messagebox.showerror("Fehler", f"Das Skript {script_name} wurde nicht gefunden.")

# Tkinter GUI-Klasse
class IndexApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Fenster konfigurieren
        self.title("Index für Python-Programme")
        self.geometry("400x400")

        # Layout
        self.layout = tk.Frame(self)
        self.layout.pack(padx=20, pady=20)

        # Überschrift
        self.title_label = tk.Label(self.layout, text="Wählen Sie ein Programm aus:", font=("Arial", 14))
        self.title_label.pack(pady=10)

        # Button für Programm 2 (Beispiel)
        self.button2 = tk.Button(self.layout, text="Berechnungsdaten",command=lambda: run_script("strom_berech_data.py"), bg="lightblue", font=("Arial", 12))


        self.button2.pack(pady=10, fill=tk.X)



        # Button für Programm 1 (Beispiel)
        self.button1 = tk.Button(self.layout, text="Einzahlungen", command=lambda: run_script("strom_einzahlungen.py"), bg="lightblue", font=("Arial", 12))
        self.button1.pack(pady=10, fill=tk.X)



        # Button für Programm 3 (Beispiel)
        self.button3 = tk.Button(self.layout, text="Zählerstände", command=lambda: run_script("strom_zaehlerstand.py"), bg="lightblue", font=("Arial", 12))
        self.button3.pack(pady=10, fill=tk.X)

        # Button für Programm 4 (Beispiel)
        self.button4 = tk.Button(self.layout, text="Berechnung", command=lambda: run_script("strom_berechnung.py"), bg="lightblue", font=("Arial", 12))
        self.button4.pack(pady=10, fill=tk.X)


        # Button für Programm 6 (Beispiel)
        self.button6 = tk.Button(self.layout, text="Datenbank", command=lambda: run_script("strom_db.py"), bg="lightblue", font=("Arial", 12))
        self.button6.pack(pady=10, fill=tk.X)

if __name__ == "__main__":
    app = IndexApp()
    app.mainloop()


