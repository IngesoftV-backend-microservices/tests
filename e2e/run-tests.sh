#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

show_help() {
    echo "Uso: ./run-tests.sh [OPCIONES]"
    echo ""
    echo "OPCIONES:"
    echo "  -v, --verbose     - Modo verbose (más detalle)"
    echo "  -c, --coverage    - Genera reporte de cobertura"
    echo "  -h, --html        - Genera reporte HTML (activado por defecto)"
    echo "  --no-html         - No genera reporte HTML"
    echo "  -p, --parallel    - Ejecuta tests en paralelo"
    echo "  -m, --marker      - Ejecuta tests con marcador específico (ej: -m smoke)"
    echo "  -k, --keyword     - Ejecuta tests que coincidan con keyword"
    echo "  --help            - Muestra esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./run-tests.sh"
    echo "  ./run-tests.sh -v"
    echo "  ./run-tests.sh --coverage --html"
    echo "  ./run-tests.sh -m smoke"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$(dirname "$SCRIPT_DIR")"
cd "$TESTS_DIR"

if [ ! -f "pytest.ini" ]; then
    print_error "Este script debe ejecutarse desde el directorio e2e/"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    exit 1
fi

if ! python3 -m pytest --version &> /dev/null; then
    print_warning "pytest no está instalado. Intentando instalar dependencias..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_error "requirements.txt no encontrado"
        exit 1
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Creando entorno virtual..."
    python3 -m venv venv
fi

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    print_warning "No se pudo activar el entorno virtual, continuando sin él..."
fi

if ! python3 -c "import pytest" &> /dev/null; then
    print_info "Instalando dependencias..."
    pip install -r requirements.txt
fi

mkdir -p reports/e2e

VERBOSE=""
COVERAGE=""
HTML="--html=reports/e2e/report.html --self-contained-html"
PARALLEL=""
MARKER=""
KEYWORD=""
NO_HTML=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=. --cov-report=html:reports/e2e/coverage --cov-report=term-missing"
            shift
            ;;
        -h|--html)
            HTML="--html=reports/e2e/report.html --self-contained-html"
            shift
            ;;
        --no-html)
            NO_HTML="true"
            HTML=""
            shift
            ;;
        -p|--parallel)
            PARALLEL="-n auto"
            shift
            ;;
        -m|--marker)
            MARKER="-m $2"
            shift 2
            ;;
        -k|--keyword)
            KEYWORD="-k $2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

PYTEST_CMD="python3 -m pytest e2e/"

print_step "Ejecutando tests E2E"

if [ -n "$VERBOSE" ]; then
    PYTEST_CMD="$PYTEST_CMD $VERBOSE"
fi

if [ -n "$COVERAGE" ]; then
    PYTEST_CMD="$PYTEST_CMD $COVERAGE"
fi

if [ -n "$PARALLEL" ]; then
    PYTEST_CMD="$PYTEST_CMD $PARALLEL"
fi

if [ -n "$MARKER" ]; then
    PYTEST_CMD="$PYTEST_CMD $MARKER"
fi

if [ -n "$KEYWORD" ]; then
    PYTEST_CMD="$PYTEST_CMD $KEYWORD"
fi

if [ -n "$HTML" ] && [ -z "$NO_HTML" ]; then
    PYTEST_CMD="$PYTEST_CMD $HTML"
fi

echo ""
print_info "Comando a ejecutar:"
echo "  $PYTEST_CMD"
echo ""

print_info "Verificando que los servicios estén corriendo..."

if ! curl -s http://localhost:8080/actuator/health > /dev/null 2>&1; then
    print_warning "API Gateway no responde en http://localhost:8080"
    print_warning "Asegúrate de que los servicios estén corriendo antes de ejecutar tests E2E"
    read -p "¿Continuar de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Ejecuta './start-services.sh' para iniciar los servicios"
        exit 1
    fi
fi

print_step "Iniciando ejecución de tests..."
echo ""

START_TIME=$(date +%s)

if eval $PYTEST_CMD; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    print_success "¡Tests completados exitosamente!"
    print_info "Duración: ${DURATION} segundos"
    
    if [ -n "$HTML" ] && [ -z "$NO_HTML" ]; then
        print_info "Reporte HTML generado en: reports/e2e/report.html"
    fi
    
    if [ -n "$COVERAGE" ]; then
        print_info "Reporte de cobertura generado en: reports/e2e/coverage/index.html"
    fi
    
    exit 0
else
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    print_error "Algunos tests fallaron"
    print_info "Duración: ${DURATION} segundos"
    
    if [ -n "$HTML" ] && [ -z "$NO_HTML" ]; then
        print_info "Revisa el reporte HTML en: reports/e2e/report.html"
    fi
    
    exit 1
fi

