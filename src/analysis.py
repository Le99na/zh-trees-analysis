import os
import pandas as pd
import requests
from io import StringIO
import re
import plotly.express as px


# --- own functions ---

def parse_geometry(geometry_string):
    if pd.isna(geometry_string):
        return None, None
    match = re.search(r'POINT \(([\d\.]+) ([\d\.]+)\)', str(geometry_string))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None


def get_epoch(year):
    if pd.isna(year):
        return "Unbekannt"
    if year < 1960:
        return "Altbestand (< 1960)"
    elif 1960 <= year < 1990:
        return "Wachstum (1960-1990)"
    else:
        return "Modern (> 1990)"


# --- main program ---

def main():
    # 1. configuration
    DATA_URL = "https://data.stadt-zuerich.ch/dataset/geo_baumkataster/download/gsz.baumkataster_baumstandorte.csv"
    LOCAL_DATA_PATH = os.path.join("data", "gsz.baumkataster_baumstandorte.csv")
    OUTPUT_DIR = "output"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    print("Starte Analyse...")

    # 2. data loading
    df = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DATA_URL, headers=headers, timeout=30)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            df.to_csv(LOCAL_DATA_PATH, index=False)
            print("Download erfolgreich.")
    except Exception as e:
        print(f"Download-Fehler: {e}")

    if df is None:
        if os.path.exists(LOCAL_DATA_PATH):
            df = pd.read_csv(LOCAL_DATA_PATH, sep=None, engine='python')
            print("Nutze lokale Daten.")
        else:
            print("Keine Daten verfügbar.")
            exit(1)

    # 3. cleaning
    if 'geometry' in df.columns:
        coords = df['geometry'].apply(parse_geometry)
        df[['x_coord', 'y_coord']] = pd.DataFrame(coords.tolist(), index=df.index)
    elif 'g_long' in df.columns:
        df['x_coord'] = df['g_long']
        df['y_coord'] = df['g_lat']

    # filtering
    df_clean = df[
        (df['pflanzjahr'] > 1800) &
        (df['pflanzjahr'] <= 2025) &
        (df['x_coord'].notna())
        ].copy()

    df_clean['epoche'] = df_clean['pflanzjahr'].apply(get_epoch)
    print(f"Datensätze nach Bereinigung: {len(df_clean)}")

    # 4. ANALYSE (Das ist neu: Echte Zahlen berechnen!)
    print("Berechne Statistiken...")

    total_trees = len(df_clean)

    # find most prevalent tree name
    if 'baumnamelat' in df_clean.columns:
        top_species = df_clean['baumnamelat'].mode()[0]
    elif 'baumnamedeu' in df_clean.columns:
        top_species = df_clean['baumnamedeu'].mode()[0]
    else:
        top_species = "Unbekannt"

    # Durchschnittsalter berechnen (einfache Annahme: 2024 - Pflanzjahr)
    avg_age = 2024 - df_clean['pflanzjahr'].mean()

    stats_text = (
        f"Anzahl Bäume: {total_trees} | "
        f"Häufigste Art: {top_species} | "
        f"Ø Alter: {avg_age:.1f} Jahre"
    )
    print(f"Erkenntnis: {stats_text}")

    # 5. VISUALISIEREN (Plotly with new Titel)
    print("Generiere interaktiven Report...")

    fig = px.scatter(
        df_clean,
        x="x_coord",
        y="y_coord",
        color="epoche",
        # add analysis results to title:
        title=f"Zürcher Baumkataster Analyse<br><sup>{stats_text}</sup>",
        hover_data=['pflanzjahr', 'baumnummer', 'baumnamelat'],
        opacity=0.6,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(
        template="plotly_white",
        width=1200,
        height=800,
        legend_title_text='Pflanz-Epoche',
        margin=dict(t=100)  # More space for subtitle
    )
    # 5. save as HTML
    # Plotly generates the complete HTML, JavaScript inclusive!
    output_file = os.path.join(OUTPUT_DIR, "index.html")
    fig.write_html(output_file)

    print(f"Fertig! Interaktiver Report gespeichert unter: {output_file}")

if __name__ == "__main__":
    main()





