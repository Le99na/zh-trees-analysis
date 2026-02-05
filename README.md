# 🌳 Zurich Trees Analysis

Eine robuste, reproduzierbare Data-Science-Pipeline zur Analyse des Baumkatasters der Stadt Zürich. Dieses Projekt analysiert die spatiotemporale Verteilung (Pflanzjahre & Standorte) der Bäume und generiert vollautomatisiert einen **interaktiven HTML-Report**.

### 🔗 [Hier klicken für die Live-Demo (Interaktiver Report)](https://le99na.github.io/zh-trees-analysis/)
*(Der Report wird via GitHub Actions generiert und auf GitHub Pages gehostet)*

## 🚀 Key Features

* 🛡️  **Robustes Data Engineering (Hybrid Pipeline):** Die Pipeline priorisiert Live-Daten (GeoJSON via WFS-Schnittstelle) für maximale Aktualität. Sollte die API nicht erreichbar sein, greift das System automatisch auf einen **lokalen CSV-Fallback** zurück.
* 🔄 **Polymorphe Datenverarbeitung:** Ein intelligenter Parser verarbeitet sowohl GeoJSON-Listenstrukturen als auch WKT-Strings (CSV) im selben Code-Pfad.
* 📊 **Interaktive Visualisierung:** Erstellung zoom- und filterbarer Karten mittels Plotly (kein statisches Bild, sondern echte Datenexploration).
* 🐳 **Reproduzierbarkeit:** Vollständig containerisiert mit Docker. Die lokale Umgebung verhält sich exakt wie die CI-Umgebung.
* ✅ **CI/CD mit Guardrails:** Automatisierte Tests bei jedem Push, aber Deployment nur bei verifiziertem Code auf dem main-Branch.

## ⚙️ CI/CD Pipeline Strategie
Dieses Projekt nutzt eine kontext-sensitive Pipeline in GitHub Actions (.github/workflows/main.yml), um Qualitätssicherung und Deployment zu steuern:
| Phase | Trigger | Beschreibung |
| :--- | :--- | :--- |
| **1. Continuous Integration (CI)** | Push auf **JEDEN** Branch | Baut den Docker-Container und führt Unit-Tests (`pytest`) aus. Dies dient als **Gatekeeper**: Fehlerhafter Code wird sofort erkannt, bevor er gemerged wird. |
| **2. Artifact Generation** | Erfolgreiche CI | Der Container generiert den Report (`index.html`) im isolierten Environment und extrahiert ihn via Volume-Mount. |
| **3. Continuous Deployment (CD)** | Push nur auf **MAIN** | Nur wenn die Tests bestehen **UND** der Code auf dem `main`-Branch liegt, wird der Report automatisch auf **GitHub Pages** veröffentlicht. |

## 🛠 Lokale Installation & Ausführung

Sie können die gesamte Pipeline lokal in einem Docker-Container ausführen. Dies simuliert exakt den Prozess, der auch auf dem GitHub-Runner stattfindet.

Voraussetzung: [Docker](https://www.docker.com/) muss installiert sein.

### 1. Image bauen
```bash
docker build -t zh-trees-analysis .
```

### 2. Analyse starten

Der Container benötigt Zugriff auf den lokalen output-Ordner, um den HTML-Bericht dort abzulegen.

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

✅ Ergebnis: Nach dem Durchlauf finden Sie die Datei index.html in Ihrem output/-Ordner.

## 🧪 Testing

Die Unit-Tests decken insbesondere die Edge Cases des Daten-Parsings (GeoJSON vs. CSV) und die Business-Logik (Epochen-Einteilung) ab.

Tests lokal ausführen:
```bash
docker run --rm zh-trees-analysis python -m pytest tests/
```

## 📂 Projektstruktur

├── .github/workflows/  # CI/CD Konfiguration (Github Actions) <br>
├── data/               # Lokaler Fallback-Datensatz (CSV) <br>
├── output/             # Zielordner für generierte Reports <br>
├── src/
│   └── analysis.py     # ETL, Cleaning & Plotting Logik <br>
├── tests/              # Pytest Unit-Tests <br>
├── Dockerfile          # Definition der Laufzeitumgebung <br>
├── requirements.txt    # Python Abhängigkeiten <br>
└── README.md           # Dokumentation <br>
