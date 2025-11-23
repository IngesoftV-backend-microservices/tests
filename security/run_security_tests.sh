#!/bin/bash

# Script para ejecutar pruebas de seguridad con OWASP ZAP

set +e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$(dirname "$SCRIPT_DIR")"
cd "$TESTS_DIR"

# Cargar variables de entorno desde .env si existe
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

BASE_HOST="${BASE_HOST:-localhost}"
ZAP_HOST="${ZAP_HOST:-localhost}"
ZAP_PORT="${ZAP_PORT:-8090}"
TARGET_SERVICE="${TARGET_SERVICE:-all}"
SCAN_TYPE="${SCAN_TYPE:-both}"
REPORTS_DIR="${REPORTS_DIR:-reports/security}"

echo -e "${GREEN}=== Pruebas de Seguridad con OWASP ZAP ===${NC}"
echo -e "ZAP Host: ${ZAP_HOST}:${ZAP_PORT}"
echo -e "Target Service: ${TARGET_SERVICE}"
echo -e "Scan Type: ${SCAN_TYPE}"
echo ""

if [ ! -d "venv" ]; then
    echo -e "${RED}Error: No se encontró el entorno virtual. Ejecuta primero: python3 -m venv venv${NC}"
    exit 1
fi

source venv/bin/activate

if ! python -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}Instalando dependencias...${NC}"
    pip install requests
fi

echo -e "${YELLOW}Verificando que ZAP esté corriendo...${NC}"
if ! curl -s "http://${ZAP_HOST}:${ZAP_PORT}/JSON/core/view/version/" > /dev/null 2>&1; then
    echo -e "${RED}Error: ZAP no está corriendo en ${ZAP_HOST}:${ZAP_PORT}${NC}"
    echo -e "${YELLOW}Inicia ZAP con uno de estos comandos:${NC}"
    echo "  ./security/start_zap.sh"
    echo "  docker run -d -p 8080:8080 --name zap-container zaproxy/zap-stable zap.sh -daemon -host 0.0.0.0 -port 8080"
    exit 1
fi

echo -e "${GREEN}ZAP está corriendo${NC}"
echo ""

mkdir -p "$REPORTS_DIR"

REPORT_PREFIX="${REPORTS_DIR}/security_scan"

echo -e "${BLUE}Ejecutando escaneo de seguridad...${NC}"
python3 << PYEOF
import sys
import os
sys.path.insert(0, os.path.dirname("${TESTS_DIR}"))

from security.zap_scanner import ZAPScanner
from security.zap_config import SERVICE_URLS, API_ENDPOINTS, MIN_ALERT_LEVEL
import json

zap = ZAPScanner()

if not zap.check_connection():
    print("Error: No se pudo conectar con ZAP")
    sys.exit(1)

print("Conectado a ZAP exitosamente")

session_name = "security_scan"
if not zap.start_session(session_name):
    print("Error: No se pudo iniciar sesión en ZAP")
    sys.exit(1)

target_service = "${TARGET_SERVICE}"
scan_type = "${SCAN_TYPE}"

if target_service.lower() == "all":
    services_to_scan = SERVICE_URLS
    print(f"Escaneando todos los servicios ({len(services_to_scan)} servicios)...")
else:
    if target_service not in SERVICE_URLS:
        print(f"Error: Servicio '{target_service}' no encontrado")
        print(f"Servicios disponibles: {', '.join(SERVICE_URLS.keys())}")
        sys.exit(1)
    services_to_scan = {target_service: SERVICE_URLS[target_service]}
    print(f"Escaneando servicio: {target_service}")

all_alerts = []
for service_name, service_url in services_to_scan.items():
    print(f"\n{'='*60}")
    print(f"Escaneando: {service_name} ({service_url})")
    print(f"{'='*60}")
    
    known_endpoints = API_ENDPOINTS.get(service_name, [])
    if known_endpoints:
        print(f"Endpoints conocidos: {len(known_endpoints)}")
    
    results = zap.scan_url(service_url, scan_type, known_endpoints)
    all_alerts.extend(results.get("alerts", []))

alerts = all_alerts
print(f"\n{'='*60}")
print(f"Resumen de alertas encontradas: {len(alerts)}")
print(f"{'='*60}")

high_alerts = [a for a in alerts if a.get("risk") in ["High", "Critical"]]
medium_alerts = [a for a in alerts if a.get("risk") == "Medium"]
low_alerts = [a for a in alerts if a.get("risk") == "Low"]

print(f"  - High/Critical: {len(high_alerts)}")
print(f"  - Medium: {len(medium_alerts)}")
print(f"  - Low: {len(low_alerts)}")

html_report = "${REPORT_PREFIX}.html"
json_report = "${REPORT_PREFIX}.json"

if zap.generate_report(html_report, "HTML"):
    print(f"\nReporte HTML generado: {html_report}")

if zap.generate_report(json_report, "JSON"):
    print(f"Reporte JSON generado: {json_report}")

with open("${REPORT_PREFIX}_alerts.json", "w") as f:
    json.dump(alerts, f, indent=2)

print(f"\nAlertas guardadas en: ${REPORT_PREFIX}_alerts.json")

if high_alerts:
    print("\n⚠️  Se encontraron alertas de alta prioridad!")
    sys.exit(1)
else:
    print("\n✓ Escaneo completado")
    sys.exit(0)
PYEOF

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Pruebas de seguridad completadas${NC}"
    echo -e "Reportes disponibles en: ${REPORTS_DIR}"
else
    echo -e "${RED}✗ Se encontraron vulnerabilidades de alta prioridad${NC}"
    exit 1
fi

