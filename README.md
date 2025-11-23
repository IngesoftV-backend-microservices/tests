# Tests E2E e Integración - E-Commerce Microservices

Este directorio contiene las pruebas end-to-end (E2E) y de integración para el proyecto de microservicios E-Commerce.

## Estructura del Proyecto

```
tests/
├── e2e/                    # Pruebas end-to-end
│   ├── test_e2e_user_service.py
│   ├── test_e2e_order_service.py
│   ├── test_e2e_payment_service.py
│   ├── test_e2e_shipping_service.py
│   ├── test_e2e_favourite_service.py
│   └── test_e2e_proxy_service.py
├── integration/            # Pruebas de integración
│   ├── test_user_service.py
│   ├── test_product_service.py
│   ├── test_order_service.py
│   ├── test_payment_service.py
│   ├── test_shipping_service.py
│   ├── test_favourite_service.py
│   ├── test_proxy_service.py
│   ├── test_api_gateway_service.py
│   ├── test_cloud_config_service.py
│   └── test_service_discovery_service.py
├── performance/            # Pruebas de rendimiento y carga
│   ├── locust_base.py
│   ├── locust_user_service.py
│   ├── locust_product_service.py
│   ├── locust_order_service.py
│   ├── locust_payment_service.py
│   ├── locust_api_gateway.py
│   └── locustfile.py
├── security/               # Pruebas de seguridad
│   ├── zap_config.py
│   ├── zap_scanner.py
│   ├── run_security_tests.sh
│   └── start_zap.sh
├── utils/                  # Utilidades y helpers
│   ├── api_utils.py
│   ├── helpers.py
│   └── http_client.py
├── conftest.py            # Configuración de pytest y fixtures
├── pytest.ini             # Configuración de pytest
├── requirements.txt       # Dependencias de Python
└── README.md              # Este archivo
```

## Requisitos Previos

1. **Python 3.8+** instalado
2. **Servicios corriendo**: Todos los microservicios deben estar ejecutándose
3. **Docker y Docker Compose**: Para levantar los servicios

## Instalación

1. **Crear un entorno virtual** (recomendado):
```bash
cd tests
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con las URLs de tus servicios si es necesario
```

## Ejecutar Tests

### Resumen Rápido

| Tipo de Test | Comando Base | Ubicación Reportes |
|-------------|--------------|-------------------|
| **Integración** | `integration/run-tests.sh` | `reports/integration/` |
| **E2E** | `e2e/run-tests.sh` | `reports/e2e/` |
| **Rendimiento** | `performance/run_load_tests.sh` | `reports/load_tests/` |
| **Seguridad** | `security/run_security_tests.sh` | `reports/security/` |

## Tipos de Tests

### Tests E2E (End-to-End)
Prueban flujos completos de usuario a través de múltiples servicios:

- **test_e2e_user_service.py**: Flujos completos del servicio de usuarios
- **test_e2e_product_service.py**: Flujos completos del servicio de productos
- **test_e2e_order_service.py**: Flujos completos del servicio de órdenes
- **test_e2e_payment_service.py**: Flujos completos del servicio de pagos
- **test_e2e_shipping_service.py**: Flujos completos del servicio de envíos
- **test_e2e_favourite_service.py**: Flujos completos del servicio de favoritos
- **test_e2e_proxy_service.py**: Flujos completos del servicio proxy

**Reportes:** Los reportes HTML se generan en `reports/e2e/report.html`.

### Tests de Integración
Prueban la funcionalidad de cada servicio individualmente:

- **test_user_service.py**: CRUD de usuarios, direcciones y credenciales
- **test_product_service.py**: CRUD de productos y categorías
- **test_order_service.py**: CRUD de órdenes y carritos
- **test_payment_service.py**: CRUD de pagos
- **test_shipping_service.py**: CRUD de items de orden (shippings)
- **test_favourite_service.py**: CRUD de favoritos
- **test_proxy_service.py**: Funcionalidad del servicio proxy
- **test_api_gateway_service.py**: Funcionalidad del API Gateway
- **test_cloud_config_service.py**: Funcionalidad del servicio de configuración
- **test_service_discovery_service.py**: Funcionalidad del servicio de descubrimiento

**Reportes:** Los reportes HTML se generan en `reports/integration/report.html`.

### Pruebas de Rendimiento
Las pruebas de rendimiento y carga se ejecutan usando [Locust](https://locust.io/) y simulan múltiples usuarios virtuales realizando peticiones HTTP a los servicios.

**Ejecución:**

Por defecto, el script ejecuta automáticamente pruebas con 10, 50 y 100 usuarios:

```bash
cd performance
./run_load_tests.sh
```

Esto ejecutará:
1. Prueba con 10 usuarios (60 segundos)
2. Prueba con 50 usuarios (60 segundos)
3. Prueba con 100 usuarios (60 segundos)

**Personalización:**

Cambiar niveles de usuarios:
```bash
USER_LEVELS="20 50 100 200" ./run_load_tests.sh
```

Cambiar duración:
```bash
DURATION=120 ./run_load_tests.sh
```

Modo interactivo:
```bash
MODE=interactive ./run_load_tests.sh
```

Modo simple (una prueba):
```bash
MODE=single USERS=50 ./run_load_tests.sh
```

**Variables de Entorno:**
- `HOST`: URL del API Gateway (default: `http://localhost:8080`)
- `MODE`: Modo de ejecución - `single`, `interactive`, `multiple` (default: `multiple`)
- `USERS`: Número de usuarios (solo modo single, default: `10`)
- `SPAWN_RATE`: Usuarios por segundo (default: `5`)
- `DURATION`: Duración de cada prueba en segundos (default: `60`)
- `USER_LEVELS`: Niveles de usuarios separados por espacios (default: `10 50 100`)

**Servicios Probados:**
- **User Service** (Peso: 3): Crear usuarios, obtener usuarios, actualizar usuarios, direcciones
- **Product Service** (Peso: 3): Crear categorías, productos, obtener productos
- **Order Service** (Peso: 2): Crear carritos, órdenes, obtener órdenes
- **Payment Service** (Peso: 1): Crear pagos, obtener pagos
- **API Gateway** (Peso: 4): Endpoints principales a través del gateway

**Reportes:** Los reportes HTML se generan en `reports/load_tests/` e incluyen gráficos de tiempo de respuesta, estadísticas de throughput (peticiones por segundo), tasa de errores y percentiles (p50, p95, p99).

### Pruebas de Seguridad
Las pruebas de seguridad se ejecutan usando [OWASP ZAP](https://www.zaproxy.org/) para detectar vulnerabilidades comunes en APIs REST.

**Requisitos Previos:**

Iniciar OWASP ZAP:
```bash
./security/start_zap.sh
```

**Ejecución:**

Escaneo de todos los servicios (por defecto):
```bash
./security/run_security_tests.sh
```

Escaneo de un servicio específico:
```bash
TARGET_SERVICE="api-gateway" ./security/run_security_tests.sh
TARGET_SERVICE="user-service" ./security/run_security_tests.sh
TARGET_SERVICE="product-service" ./security/run_security_tests.sh
```

Servicios disponibles:
- `api-gateway` (puerto 8080)
- `user-service` (puerto 8700)
- `product-service` (puerto 8500)
- `order-service` (puerto 8300)
- `payment-service` (puerto 8400)
- `shipping-service` (puerto 8600)
- `favourite-service` (puerto 8800)
- `proxy-client` (puerto 8900)
- `all` (todos los servicios)

Solo spider scan (descubrimiento de URLs):
```bash
SCAN_TYPE="spider" ./security/run_security_tests.sh
```

Solo active scan (detección de vulnerabilidades):
```bash
SCAN_TYPE="active" ./security/run_security_tests.sh
```

ZAP en otro host/puerto:
```bash
ZAP_HOST="192.168.1.100" ZAP_PORT="8090" ./security/run_security_tests.sh
```

**Variables de Entorno:**

Configuración de ZAP:
- `ZAP_HOST`: Host donde corre ZAP (default: `localhost`)
- `ZAP_PORT`: Puerto de ZAP (default: `8090`)
- `ZAP_API_KEY`: API Key de ZAP (opcional)

Configuración de Escaneo:
- `TARGET_SERVICE`: Servicio a escanear - nombre del servicio o `all` (default: `all`)
- `SCAN_TYPE`: Tipo de escaneo - `spider`, `active`, `both` (default: `both`)
- `REPORTS_DIR`: Directorio para reportes (default: `reports/security`)

**Tipos de Escaneo:**
- **Spider Scan**: Explora la aplicación siguiendo enlaces para descubrir URLs
- **Active Scan**: Ejecuta ataques automatizados para encontrar vulnerabilidades:
  - SQL Injection
  - XSS (Cross-Site Scripting)
  - CSRF (Cross-Site Request Forgery)
  - Insecure Direct Object References
  - Security Misconfiguration
  - Y más...

**Reportes:** Los reportes se generan en `reports/security/` con nombres fijos: `security_scan.html` (reporte HTML completo), `security_scan.json` (resumen JSON) y `security_scan_alerts.json` (alertas detalladas).

**Interpretación de Resultados:**
- **Critical/High**: Vulnerabilidades críticas que deben corregirse inmediatamente
- **Medium**: Vulnerabilidades que deberían corregirse
- **Low**: Problemas menores o informativos
- **Informational**: Información útil pero no crítico

El script retorna código de salida 1 si encuentra alertas High/Critical, permitiendo fallar el pipeline en CI/CD.

## Configuración

### Variables de Entorno (.env)

Puedes crear un archivo `.env` en la raíz de `tests/` para personalizar la configuración. Si no existe, se usarán los valores por defecto (localhost y puertos estándar).

**Crear archivo .env:**
```bash
cp .env.example .env
# Editar .env con tus valores
```

```env
# Base Host (por defecto: localhost)
BASE_HOST=localhost

# Service Ports (por defecto: los puertos estándar)
API_GATEWAY_PORT=8080
USER_SERVICE_PORT=8700
PRODUCT_SERVICE_PORT=8500
ORDER_SERVICE_PORT=8300
PAYMENT_SERVICE_PORT=8400
SHIPPING_SERVICE_PORT=8600
FAVOURITE_SERVICE_PORT=8800
PROXY_CLIENT_PORT=8900

# OWASP ZAP Configuration
ZAP_HOST=localhost
ZAP_PORT=8080
ZAP_API_KEY=

# Test Configuration
TEST_TIMEOUT=30
MAX_RETRIES=3
RETRY_DELAY=2

# Authentication
DEFAULT_USERNAME=admin
DEFAULT_PASSWORD=admin123
```

## Utilidades

### APIClient
Cliente HTTP con retry automático y manejo de errores:
```python
from utils.http_client import APIClient

client = APIClient("http://localhost:8700")
response = client.get("/api/users", headers=auth_headers)
```

### Helpers
Funciones auxiliares para generar datos de prueba:
```python
from utils.helpers import generate_user_data, generate_product_data

user_data = generate_user_data()
product_data = generate_product_data(category_id=1)
```
