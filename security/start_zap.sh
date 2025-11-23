#!/bin/bash

# Script para iniciar OWASP ZAP usando Docker

set +e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Cargar variables de entorno desde .env si existe
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

ZAP_PORT="${ZAP_PORT:-8090}"
CONTAINER_NAME="zap-container"

echo -e "${GREEN}=== Iniciando OWASP ZAP ===${NC}"
echo -e "${YELLOW}Nota: ZAP usa el puerto ${ZAP_PORT} por defecto (para evitar conflicto con API Gateway en 8080)${NC}"
echo -e "${YELLOW}Si necesitas otro puerto, usa: ZAP_PORT=XXXX ./security/start_zap.sh${NC}"
echo ""

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}El contenedor ${CONTAINER_NAME} ya existe${NC}"
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${GREEN}ZAP ya está corriendo en el puerto ${ZAP_PORT}${NC}"
        exit 0
    else
        echo -e "${YELLOW}Iniciando contenedor existente...${NC}"
        docker start "${CONTAINER_NAME}"
        sleep 5
        echo -e "${GREEN}ZAP iniciado${NC}"
        exit 0
    fi
fi

echo -e "${YELLOW}Creando nuevo contenedor ZAP...${NC}"
echo -e "${YELLOW}Nota: ZAP escuchará en el puerto ${ZAP_PORT} dentro del contenedor${NC}"
echo -e "${YELLOW}Usando --network host para que ZAP pueda acceder a servicios en localhost${NC}"
docker run -d \
    --name "${CONTAINER_NAME}" \
    --network host \
    zaproxy/zap-stable \
    zap.sh -daemon \
    -host 0.0.0.0 \
    -port ${ZAP_PORT} \
    -config api.disablekey=true \
    -config api.addrs.addr.name=.* \
    -config api.addrs.addr.regex=true \
    -config network.httpsProxy.enabled=false

if [ $? -eq 0 ]; then
    echo -e "${GREEN}ZAP iniciado exitosamente en el puerto ${ZAP_PORT}${NC}"
    echo -e "${YELLOW}Esperando a que ZAP esté listo...${NC}"
    sleep 10
    
    for i in {1..30}; do
        if curl -s "http://localhost:${ZAP_PORT}/JSON/core/view/version/" > /dev/null 2>&1; then
            echo -e "${GREEN}ZAP está listo${NC}"
            exit 0
        fi
        sleep 2
    done
    
    echo -e "${RED}Timeout esperando a que ZAP esté listo${NC}"
    exit 1
else
    echo -e "${RED}Error al iniciar ZAP${NC}"
    exit 1
fi

