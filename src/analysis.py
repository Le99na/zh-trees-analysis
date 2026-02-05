import os
import pandas as pd
import requests
import re
import plotly.express as px


# --- Helper Functions ---

def parse_geometry(data):
    """
    Parses geometry data polymorphically.
    Handles both GeoJSON lists (live data) and WKT strings (CSV fallback).

    Args:
        data: Either a list [x, y] or a string "POINT (x y)"
    Returns:
        tuple: (x_coord, y_coord) as floats, or (None, None) if invalid.
    """
    # Case A: GeoJSON format (List of coordinates)
    # Example: [2683245.5, 1247890.1]
    if isinstance(data, list) and len(data) >= 2:
        return float(data[0]), float(data[1])

    # Case B: CSV format (Well-Known Text String)
    # Example: "POINT (2683245.5 1247890.1)"
    if isinstance(data, str):
        match = re.search(r'POINT \(([\d\.]+) ([\d\.]+)\)', data)
        if match:
            return float(match.group(1)), float(match.group(2))

    # Case C: Invalid or missing data
    return None, None


def get_epoch(year):
    """
    Categorizes the planting year into historical epochs.
    """
    if pd.isna(year):
        return "Unknown"

    try:
        y = float(year)
        if y < 1960:
            return "Heritage (< 1960)"
        elif 1960 <= y < 1990:
            return "Expansion (1960-1990)"
        else:
            return "Modern (> 1990)"
    except (ValueError, TypeError):
        return "Unknown"


# --- Main Execution ---

def main():
    # 1. Configuration
    # We prefer GeoJSON for live data, but keep CSV structure for compatibility
    DATA_URL = "https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Baumkataster?service=WFS&version=1.1.0&request=GetFeature&outputFormat=GeoJSON&typename=baumkataster_baumstandorte"
    LOCAL_DATA_PATH = os.path.join("data", "gsz.baumkataster_baumstandorte.csv")
    OUTPUT_DIR = "output"

    # Ensure directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    print("Starting analysis pipeline...")

    df = None

    # 2. Data Loading Strategy (Hybrid Approach)

    # Attempt 1: Live Download (GeoJSON)
    try:
        print(f"Attempting live download from WFS...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DATA_URL, headers=headers, timeout=30)

        if response.status_code == 200:
            print("Download successful. Parsing GeoJSON...")
            data_json = response.json()

            # Normalize JSON structure to flat DataFrame
            df = pd.json_normalize(data_json['features'])

            # Map GeoJSON column names to our internal schema (CSV compatibility)
            rename_map = {
                'properties.pflanzjahr': 'pflanzjahr',
                'properties.baumnamelat': 'baumnamelat',
                'properties.baumnummer': 'baumnummer',
                'geometry.coordinates': 'geometry'  # Temp column for parsing
            }
            # Only rename columns that actually exist in the response
            df = df.rename(columns=rename_map)

    except Exception as e:
        print(f"⚠️ Live download failed: {e}")
        df = None

    # Attempt 2: Local Fallback (CSV)
    if df is None:
        if os.path.exists(LOCAL_DATA_PATH):
            print("Falling back to local CSV dataset.")
            df = pd.read_csv(LOCAL_DATA_PATH, sep=None, engine='python')
        else:
            print("❌ Critical Error: No data available (neither live nor local).")
            exit(1)

    # 3. Data Processing & Cleaning

    # Process geometry (Handles both list and string inputs via polymorphic function)
    if 'geometry' in df.columns:
        print("Processing geometry...")
        # .tolist() is required to correctly unpack the tuple into two columns
        coords = df['geometry'].apply(parse_geometry).tolist()
        df[['x_coord', 'y_coord']] = pd.DataFrame(coords, index=df.index)
    else:
        print("Warning: No geometry column found.")

    # Apply filters: Valid years and valid coordinates
    df_clean = df[
        (df['pflanzjahr'] > 1800) &
        (df['pflanzjahr'] <= 2025) &
        (df['x_coord'].notna())
        ].copy()

    # Add categorical features
    df_clean['epoche'] = df_clean['pflanzjahr'].apply(get_epoch)

    # 4. Statistical Analysis
    print("Calculating statistics...")
    total_trees = len(df_clean)

    # Determine the correct column for tree names (fallback logic)
    if 'baumnamelat' in df_clean.columns:
        top_species = df_clean['baumnamelat'].mode()[0]
    elif 'baumnamedeu' in df_clean.columns:
        top_species = df_clean['baumnamedeu'].mode()[0]
    else:
        top_species = "Unknown"

    # Calculate average age (Reference year: 2026)
    avg_age = 2026 - df_clean['pflanzjahr'].mean()

    # Create a summary string for the plot title
    stats_text = (
        f"Total Trees: {total_trees} | "
        f"Top Species: {top_species} | "
        f"Ø Age: {avg_age:.1f} years"
    )
    print(f"Insights: {stats_text}")

    # 5. Visualization (Plotly)
    print("Generating interactive report...")

    fig = px.scatter(
        df_clean,
        x="x_coord",
        y="y_coord",
        color="epoche",
        title=f"Zurich Tree Cadastre Analysis<br><sup>{stats_text}</sup>",
        # Custom hover data handling
        hover_data={
            'pflanzjahr': True,
            'baumnamelat': True if 'baumnamelat' in df_clean.columns else False,
            'baumnummer': True if 'baumnummer' in df_clean.columns else False,
            'x_coord': False,  # Hide raw coordinates
            'y_coord': False
        },
        opacity=0.6,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    # Fix aspect ratio to avoid distortion of the map
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    fig.update_layout(
        template="plotly_white",
        width=1200, height=800,
        legend_title_text='Planting Epoch',
        margin=dict(t=100)  # Add space for title/subtitle
    )

    # 6. Export
    output_file = os.path.join(OUTPUT_DIR, "index.html")
    fig.write_html(output_file)
    print(f"✅ Success! Report generated at: {output_file}")


if __name__ == "__main__":
    main()
