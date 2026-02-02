# 🌳 Zurich Trees Analysis

Eine reproduzierbare Data-Science-Pipeline zur Analyse des Baumkatasters der Stadt Zürich.
Dieses Projekt analysiert die spatiotemporale Verteilung (Pflanzjahre & Standorte) der Bäume und generiert einen **interaktiven HTML-Report**.

## 🚀 Features

* **Robustes Data Engineering:** Hybrid-Ansatz für den Datenimport (Live-Download mit Fallback auf lokale Daten bei Server-Problemen).
* **Reproduzierbarkeit:** Vollständig containerisiert mit Docker.
* **Qualitätssicherung:** Unit-Testing mit `pytest`.
* **CI/CD:** Automatisierte Build- & Test-Pipeline via GitHub Actions.
* **Automated Reporting:** Generiert Visualisierungen und eine HTML-Zusammenfassung.

## 🛠 Installation & Ausführung

Voraussetzung: [Docker](https://www.docker.com/) muss installiert sein.

### 1. Image bauen
```bash
docker build -t zh-trees-analysis .
```

### 2. Analyse starten

Der Container benötigt Zugriff auf einen lokalen data-Ordner (Input) und einen output-Ordner (Ergebnis). Führen Sie folgenden Befehl im Hauptverzeichnis des Projekts aus:

#### Linux/Mac:
```bash
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/data:/app/data" \
  zh-trees-analysis
```

#### Windows (PowerShell):
```PowerShell
docker run --rm `
  -v ${PWD}/output:/app/output `
  -v ${PWD}/data:/app/data `
  zh-trees-analysis
```

Ergebnis: Nach erfolgreichem Durchlauf finden Sie den Report (index.html) und die Grafik im Ordner output/.

## 🧪 Tests

Die Unit-Tests stellen sicher, dass die Koordinaten-Transformation (WKT Parsing) korrekt funktioniert.

```bash
# Tests manuell im Container ausführen
docker run --rm zh-trees-analysis python -m pytest tests/
```

Die Tests werden zudem bei jedem Push auf main automatisch durch die GitHub Actions Pipeline ausgeführt (siehe Reiter "Actions" auf GitHub).

## 📂 Projektstruktur
.
├── .github/workflows/  # CI/CD configuration <br>
├── data/               # Locale Fallback-Data (CSV) <br>
├── output/             # Generated Reports <br>
├── src/                # Quellcode <br>
├── tests/              # Unit Tests <br>
├── Dockerfile          # Container Definition <br>
├── requirements.txt    # Python Dependencies <br>
└── README.md           # Documentation <br>


