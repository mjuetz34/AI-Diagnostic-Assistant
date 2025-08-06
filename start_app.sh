#!/bin/bash

# Farben für bessere Ausgabe
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starte AI Diagnostic Assistant...${NC}"

# Virtuelles Environment aktivieren
source venv/bin/activate

# Prüfen ob Port 8501 verfügbar ist, sonst anderen Port verwenden
PORT=8501
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; do
    echo -e "${BLUE}Port $PORT ist belegt, versuche Port $((PORT+1))${NC}"
    PORT=$((PORT+1))
done

echo -e "${GREEN}✅ Starte Anwendung auf Port $PORT${NC}"

# Streamlit starten
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --browser.gatherUsageStats=false &

# Kurz warten bis Anwendung gestartet ist
sleep 3

# Browser öffnen (falls verfügbar)
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:$PORT"
elif command -v open &> /dev/null; then
    open "http://localhost:$PORT"
elif command -v start &> /dev/null; then
    start "http://localhost:$PORT"
else
    echo -e "${GREEN}🌐 Öffnen Sie Ihren Browser und gehen Sie zu: http://localhost:$PORT${NC}"
fi

echo -e "${GREEN}✅ Anwendung läuft! Browser sollte sich automatisch öffnen.${NC}"
echo -e "${BLUE}💡 Drücken Sie Ctrl+C um die Anwendung zu beenden${NC}"

# Warten bis Benutzer die Anwendung beendet
wait 