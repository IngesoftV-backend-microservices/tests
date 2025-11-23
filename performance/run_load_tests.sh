#!/bin/bash

set +e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$(dirname "$SCRIPT_DIR")"
cd "$TESTS_DIR"

if [ ! -d "venv" ]; then
    echo -e "${RED}Error: No se encontró el entorno virtual. Ejecuta primero: python3 -m venv venv${NC}"
    exit 1
fi

source venv/bin/activate

if ! python -c "import locust" 2>/dev/null; then
    echo -e "${YELLOW}Instalando Locust...${NC}"
    pip install locust==2.17.0
fi

HOST="${HOST:-http://localhost:8080}"
SPAWN_RATE="${SPAWN_RATE:-5}"
DURATION="${DURATION:-60}"
MODE="${MODE:-multiple}"

if [ -n "$USER_LEVELS" ]; then
    MODE="multiple"
fi

if [ -z "$USER_LEVELS" ] && [ "$MODE" = "multiple" ]; then
    USER_LEVELS="10 50 100"
fi

echo -e "${YELLOW}Verificando que los servicios están corriendo...${NC}"
if ! curl -s "${HOST}/actuator/health" > /dev/null 2>&1; then
    echo -e "${RED}Advertencia: No se pudo conectar a ${HOST}. Asegúrate de que los servicios estén corriendo.${NC}"
    read -p "¿Continuar de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if [ "$MODE" = "single" ] || [ "$MODE" = "interactive" ]; then
    USERS="${USERS:-10}"
    HEADLESS="${HEADLESS:-false}"
    
    echo -e "${GREEN}=== Pruebas de Rendimiento con Locust ===${NC}"
    echo -e "Host: ${HOST}"
    echo -e "Usuarios: ${USERS}"
    echo -e "Tasa de spawn: ${SPAWN_RATE}/s"
    echo -e "Duración: ${DURATION}s"
    echo ""
    
    if [ "$HEADLESS" = "true" ]; then
        echo -e "${GREEN}Ejecutando pruebas en modo headless...${NC}"
        locust -f performance/locustfile.py \
            --host="${HOST}" \
            --users="${USERS}" \
            --spawn-rate="${SPAWN_RATE}" \
            --run-time="${DURATION}s" \
            --headless \
            --html=reports/performance_report.html
    else
        echo -e "${GREEN}Iniciando servidor web de Locust...${NC}"
        echo -e "Abre tu navegador en: ${GREEN}http://localhost:8089${NC}"
        locust -f performance/locustfile.py --host="${HOST}"
    fi
    
    echo -e "${GREEN}Pruebas completadas.${NC}"

elif [ "$MODE" = "multiple" ] || [ "$MODE" = "stress" ]; then
    USER_LEVELS=($USER_LEVELS)
    
    REPORTS_DIR="${REPORTS_DIR:-reports/load_tests}"
    mkdir -p "$REPORTS_DIR"
    
    echo -e "${GREEN}=== Pruebas de Carga con Múltiples Niveles ===${NC}"
    echo -e "Host: ${HOST}"
    echo -e "Tasa de spawn: ${SPAWN_RATE}/s"
    echo -e "Duración por prueba: ${DURATION}s"
    echo -e "Niveles: ${USER_LEVELS[*]}"
    echo -e "Reportes en: ${REPORTS_DIR}"
    echo ""
    
    for USERS in "${USER_LEVELS[@]}"; do
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}Ejecutando prueba con ${USERS} usuarios${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        REPORT_PREFIX="${REPORTS_DIR}/load_${USERS}users"
        
        locust -f performance/locustfile.py \
            --host="${HOST}" \
            --users="${USERS}" \
            --spawn-rate="${SPAWN_RATE}" \
            --run-time="${DURATION}s" \
            --headless \
            --html="${REPORT_PREFIX}.html" \
            --loglevel=INFO
        
        LOCUST_EXIT_CODE=$?
        
        if [ -f "${REPORT_PREFIX}.html" ]; then
            python3 << PYEOF 2>/dev/null || true
import html
import re
import json

html_file = "${REPORT_PREFIX}.html"
try:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'<div class="tasks" data-tasks="([^"]+)">'
    match = re.search(pattern, content)
    
    if match:
        json_str = html.unescape(match.group(1))
        try:
            json.loads(json_str)
            new_div = f"<div class=\"tasks\" data-tasks='{json_str}'>"
            content = re.sub(pattern, new_div, content)
        except json.JSONDecodeError:
            pass
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
except Exception:
    pass
PYEOF
            
            echo -e "${GREEN}✓ Prueba con ${USERS} usuarios completada${NC}"
            echo -e "  Reporte: ${REPORT_PREFIX}.html"
            if [ $LOCUST_EXIT_CODE -ne 0 ]; then
                echo -e "${YELLOW}  Nota: Algunos errores ocurrieron durante la prueba${NC}"
            fi
        else
            echo -e "${RED}✗ Error crítico en prueba con ${USERS} usuarios (no se generó reporte)${NC}"
        fi
        
        echo ""
        
        if [ "$USERS" != "${USER_LEVELS[-1]}" ]; then
            echo -e "${YELLOW}Esperando 10 segundos antes de la siguiente prueba...${NC}"
            sleep 10
        fi
    done
    
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Todas las pruebas completadas${NC}"
    echo -e "${GREEN}Reportes disponibles en: ${REPORTS_DIR}${NC}"
    echo ""

else
    echo -e "${RED}Error: Modo desconocido '${MODE}'. Usa 'single', 'multiple', 'interactive' o 'stress'${NC}"
    exit 1
fi

