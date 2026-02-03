# 🌳 Zurich Trees Analysis

Eine reproduzierbare Data-Science-Pipeline zur Analyse des Baumkatasters der Stadt Zürich.
Dieses Projekt analysiert die spatiotemporale Verteilung (Pflanzjahre & Standorte) der Bäume und generiert einen **interaktiven HTML-Report**.

### 🔗 [Hier klicken für die Live-Demo (Interaktiver Report)](https://le99na.github.io/zh-trees-analysis/)
*(Der Report wird automatisch via CI/CD bei jedem Update neu generiert)*

## 🚀 Features

* **Interaktive Visualisierung:** Nutzung von Plotly für zoom- und filterbare Karten (HTML).
* **Robustes Data Engineering:** Hybrid-Ansatz für den Datenimport (Live-Download mit Fallback).
* **Reproduzierbarkeit:** Vollständig containerisiert mit Docker.
* **Qualitätssicherung:** Unit-Testing mit `pytest`.
* **CI:** Automatisierte Build- & Test-Pipeline via **GitHub Actions**.
* **Continuous Deployment (CD):** Vollautomatisches Publishing des Reports auf **GitHub Pages**.
* **Code Quality:** Unit-Testing mit `pytest`.

## 🛠 Installation & Ausführung

Falls Sie den Container lokal bauen und laufen lassen möchten (statt die Live-Demo anzusehen):

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

Ergebnis: Öffnen Sie nach dem Durchlauf die Datei output/index.html in Ihrem Browser. Sie können in der Legende auf Epochen klicken, um diese ein- oder auszublenden.

## ⚙️ CI/CD Pipeline

Dieses Projekt nutzt GitHub Actions für eine vollautomatisierte Pipeline:

1. Continuous Integration (CI): Bei jedem Push wird der Docker-Container gebaut und die Unit-Tests (tests/) werden ausgeführt.

2. Continuous Deployment (CD): Wenn die Tests erfolgreich sind, generiert der Container den Report und pusht ihn automatisch in den gh-pages Branch.

3. Hosting: GitHub Pages serviert die generierte HTML-Datei als öffentliche Webseite.

## 📂 Projektstruktur

├── .github/workflows/  # CI/CD configuration <br>
├── data/               # Locale Fallback-Data (CSV) <br>
├── output/             # Generated Reports <br>
├── src/                # Quellcode <br>
├── tests/              # Unit Tests <br>
├── Dockerfile          # Container Definition <br>
├── requirements.txt    # Python Dependencies <br>
└── README.md           # Documentation <br>


