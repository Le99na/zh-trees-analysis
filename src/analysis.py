# src/analysis.py

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from io import StringIO

# 1. Konfiguration
# Wir laden die Daten live. Das garantiert, dass wir immer den aktuellen Stand haben.
DATA_URL = "https://data.stadt-zuerich.ch/dataset/geo_baumkataster/download/gsz.baumkataster.csv"
LOCAL_DATA_PATH = os.path.join("data", "gsz.baumkataster_baumstandorte.csv") # Pfad zur lokalen Datei
OUTPUT_DIR = "output"

# Sicherstellen, dass der Output-Ordner existiert (wichtig für Docker!)
os.makedirs(OUTPUT_DIR, exist_ok=True)
# Auch den Data-Ordner sicherstellen, falls wir später cachen wollen
os.makedirs("data", exist_ok=True)

print(f"Versuche Daten zu laden...")

# 2. Daten laden (Resiliente Logik)
df = None

# Versuch A: Live Download
try:
    print(f"Versuche Download von {DATA_URL}...")
    # Wir faken einen Browser-User-Agent, damit der Server uns nicht sofort blockt
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(DATA_URL, headers=headers)

    if response.status_code == 200:
        # Erfolgreich geladen -> In Pandas lesen
        df = pd.read_csv(StringIO(response.text))
        print("Download erfolgreich!")

        # Optional: Wir speichern es lokal als Backup für das nächste Mal
        df.to_csv(LOCAL_DATA_PATH, index=False)
    else:
        print(f"Server antwortete mit Status Code: {response.status_code}")

except Exception as e:
    print(f"Download fehlgeschlagen: {e}")

# Versuch B: Lokaler Fallback
if df is None:
    print("Versuche lokale Datei zu laden...")
    if os.path.exists(LOCAL_DATA_PATH):
        df = pd.read_csv(LOCAL_DATA_PATH)
        print(f"Lokale Datei geladen: {LOCAL_DATA_PATH}")
    else:
        print("KRITISCHER FEHLER: Keine Daten verfügbar (weder Online noch Lokal).")
        print("Bitte lade die Datei manuell herunter und speichere sie in 'data/baumkataster.csv'.")
        exit(1)

# 3. Bereinigen & Feature Engineering (Der Fix!)
print("Starte Datenbereinigung...")

# WICHTIG: Koordinaten aus 'geometry' Spalte extrahieren
# Format ist: "POINT (2683450 1250100)"
if 'geometry' in df.columns:
    print("Extrahiere Koordinaten aus 'geometry' Spalte...")
    # Regex sucht nach zwei Zahlen getrennt durch Leerraum in Klammern
    coords = df['geometry'].str.extract(r'POINT \(([\d\.]+) ([\d\.]+)\)')
    df['x_coord'] = coords[0].astype(float) # Ost-West (ehemals g_long)
    df['y_coord'] = coords[1].astype(float) # Nord-Süd (ehemals g_lat)
elif 'g_long' in df.columns and 'g_lat' in df.columns:
    df['x_coord'] = df['g_long']
    df['y_coord'] = df['g_lat']
else:
    print("Fehler: Keine Koordinatenspalten gefunden (weder 'geometry' noch 'g_lat/g_long')")
    print("Spalten im Datensatz:", df.columns.tolist())
    exit(1)

# Wir filtern ungültige Jahre und fehlende Koordinaten raus.
current_year = datetime.now().year

# Vorher: Anzahl Zeilen
print(f"Rohdaten Zeilen: {len(df)}")

df_clean = df[
    (df['pflanzjahr'].notna()) &                # Kein leeres Jahr
    (df['pflanzjahr'] > 1800) &                 # Plausibel
    (df['pflanzjahr'] <= current_year) &        # Keine Zukunftsbäume
    (df['x_coord'].notna()) &                     # Koordinaten müssen da sein
    (df['y_coord'].notna())
].copy()

# Hier erstellen wir die "Spatiotemporale" Logik (Epochen)
def get_epoch(year):
    if year < 1960:
        return "Altbestand (< 1960)"
    elif 1960 <= year < 1990:
        return "Wachstum (1960-1990)"
    else:
        return "Modern (> 1990)"

df_clean['epoche'] = df_clean['pflanzjahr'].apply(get_epoch)

print(f"Daten bereinigt. Verbleibende Bäume: {len(df_clean)}")

# 4. Visualisieren (Visualize)
# Wir nutzen Seaborn für einen Scatterplot mit Facets (Subplots pro Epoche)
print("Erstelle Grafik...")

sns.set_theme(style="whitegrid") # Sauberer Look

# FacetGrid: Erstellt für jede 'epoche' ein eigenes kleines Bild nebeneinander
g = sns.relplot(
    data=df_clean,
    x="x_coord",
    y="y_coord",
    col="epoche",          # Spalte die Bilder nach Epoche auf
    hue="epoche",          # Färbe sie auch ein
    kind="scatter",
    palette="viridis",     # Professionelle Farbskala
    alpha=0.6,             # Transparenz gegen Overplotting
    s=10,                  # Punktgröße
    height=5,
    aspect=1
)

# Titel und Labels anpassen
g.fig.suptitle("Spatiotemporale Verteilung der Bäume in Zürich", y=1.03, fontsize=16)
g.set_axis_labels("Längengrad", "Breitengrad")

# 5. Speichern (Output)
output_path = os.path.join(OUTPUT_DIR, "baum_analyse_plot.png")
plt.savefig(output_path, dpi=150, bbox_inches='tight')

# 5. HTML Report
print("Generiere HTML...")
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Baum-Analyse Zürich</title>
    <style>
        body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>🌳 Analyse des Zürcher Baumkatasters</h1>
    <p>Datenquelle: OGD Stadt Zürich (Geoportal)</p>
    <h2>Spatiotemporale Verteilung</h2>
    <img src="baum_analyse_plot.png" alt="Baum Plot">
    <p>Generiert am: {datetime.now().strftime('%d.%m.%Y')}</p>
</body>
</html>
"""

html_path = os.path.join(OUTPUT_DIR, "index.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)



print(f"Analyse erfolgreich! Grafik gespeichert unter: {output_path}")