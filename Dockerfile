# 1. Basis-Image: Wir starten mit einem schlanken Python-System (Debian-basiert)
# "slim" ist Best Practice: Kleiner, sicherer, schnellerer Download.
FROM python:3.9-slim

# 2. Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# 3. Umgebungsvariablen für Python setzen
# PYTHONDONTWRITEBYTECODE: Verhindert .pyc Dateien (unnötig im Container)
# PYTHONUNBUFFERED: Zwingt Python, Prints sofort auszugeben (wichtig für Logs!)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Abhängigkeiten installieren (Caching-Trick!)
# Wir kopieren ERST nur die requirements.txt.
# Warum? Wenn du nur deinen Code änderst, aber nicht die Libraries,
# überspringt Docker diesen Schritt beim nächsten Mal. Das spart Zeit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Den restlichen Code kopieren
# Kopiert alles (.) von deinem lokalen Ordner in den Container (.)
COPY . .

# 6. Der Befehl, der beim Start ausgeführt wird
CMD ["python", "src/analysis.py"]
