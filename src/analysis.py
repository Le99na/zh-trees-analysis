# src/analysis.py

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from io import StringIO
import re


# --- EIGENE FUNKTIONEN (UNIT TESTABLE) ---

def parse_geometry(geometry_string):
    """
    Extrahiert X und Y aus einem String wie 'POINT (2683450 1250100)'
    Gibt (None, None) zurück, wenn das Format nicht passt.
    """
    if pd.isna(geometry_string):
        return None, None

    # Regex sucht nach: POINT (Zahl Zahl)
    match = re.search(r'POINT \(([\d\.]+) ([\d\.]+)\)', str(geometry_string))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None


def get_epoch(year):
    """Ordnet ein Jahr einer Epoche zu."""
    if pd.isna(year):
        return "Unbekannt"
    if year < 1960:
        return "Altbestand (< 1960)"
    elif 1960 <= year < 1990:
        return "Wachstum (1960-1990)"
    else:
        return "Modern (> 1990)"


# --- HAUPTPROGRAMM ---

def main():
    # 1. Konfiguration
    DATA_URL = "https://data.stadt-zuerich.ch/dataset/geo_baumkataster/download/gsz.baumkataster_baumstandorte.csv"
    LOCAL_DATA_PATH = os.path.join("data", "gsz.baumkataster_baumstandorte.csv")
    OUTPUT_DIR = "output"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    print(f"Konfiguration: Suche Daten unter {LOCAL_DATA_PATH} oder online...")

    # 2. Daten laden
    df = None

    # Versuch A: Live Download
    try:
        print(f"Versuche Download von {DATA_URL}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DATA_URL, headers=headers, timeout=30)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            print("Download erfolgreich!")
            df.to_csv(LOCAL_DATA_PATH, index=False)
        else:
            print(f"Server Status: {response.status_code}")
    except Exception as e:
        print(f"Download fehlgeschlagen: {e}")

    # Versuch B: Lokal
    if df is None:
        if os.path.exists(LOCAL_DATA_PATH):
            df = pd.read_csv(LOCAL_DATA_PATH, sep=None, engine='python')
            print(f"Lokale Datei geladen: {LOCAL_DATA_PATH}")
        else:
            print("KRITISCHER FEHLER: Keine Daten gefunden.")
            exit(1)

    # 3. Bereinigen mit unseren neuen Funktionen
    print("Starte Datenbereinigung...")

    # Neue Logik anwenden
    if 'geometry' in df.columns:
        print("Wende parse_geometry an...")
        # Wir wenden die Funktion auf jede Zeile an
        coords = df['geometry'].apply(parse_geometry)
        # Das Ergebnis (Tupel) aufteilen in zwei Spalten
        df[['x_coord', 'y_coord']] = pd.DataFrame(coords.tolist(), index=df.index)
    elif 'g_long' in df.columns and 'g_lat' in df.columns:
        df['x_coord'] = df['g_long']
        df['y_coord'] = df['g_lat']

    current_year = datetime.now().year

    df_clean = df[
        (df['pflanzjahr'].notna()) &
        (df['pflanzjahr'] > 1800) &
        (df['pflanzjahr'] <= current_year) &
        (df['x_coord'].notna()) &
        (df['y_coord'].notna())
        ].copy()

    df_clean['epoche'] = df_clean['pflanzjahr'].apply(get_epoch)

    print(f"Daten bereinigt. Verbleibende Bäume: {len(df_clean)}")

    # 4. Visualisieren
    print("Erstelle Grafik...")
    sns.set_theme(style="whitegrid")

    g = sns.relplot(
        data=df_clean,
        x="x_coord", y="y_coord",
        col="epoche", hue="epoche",
        kind="scatter", palette="viridis",
        alpha=0.6, s=10, height=5, aspect=1
    )
    g.fig.suptitle("Spatiotemporale Verteilung der Bäume in Zürich", y=1.03)

    output_path = os.path.join(OUTPUT_DIR, "baum_analyse_plot.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')

    # 5. HTML Report
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"""
        <html><body>
        <h1>🌳 Analyse des Zürcher Baumkatasters</h1>
        <img src="baum_analyse_plot.png" width="100%">
        <p>Generiert am: {datetime.now().strftime('%d.%m.%Y')}</p>
        </body></html>
        """)

    print(f"Fertig! Ergebnisse in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()