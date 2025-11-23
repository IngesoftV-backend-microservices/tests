"""
Configuración para OWASP ZAP.
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Host base (por defecto localhost)
BASE_HOST = os.getenv("BASE_HOST", "localhost")

# URLs de los servicios a escanear
SERVICE_URLS = {
    "api-gateway": f"http://{BASE_HOST}:{os.getenv('API_GATEWAY_PORT', '8080')}",
    "user-service": f"http://{BASE_HOST}:{os.getenv('USER_SERVICE_PORT', '8700')}",
    "product-service": f"http://{BASE_HOST}:{os.getenv('PRODUCT_SERVICE_PORT', '8500')}",
    "order-service": f"http://{BASE_HOST}:{os.getenv('ORDER_SERVICE_PORT', '8300')}",
    "payment-service": f"http://{BASE_HOST}:{os.getenv('PAYMENT_SERVICE_PORT', '8400')}",
    "shipping-service": f"http://{BASE_HOST}:{os.getenv('SHIPPING_SERVICE_PORT', '8600')}",
    "favourite-service": f"http://{BASE_HOST}:{os.getenv('FAVOURITE_SERVICE_PORT', '8800')}",
    "proxy-client": f"http://{BASE_HOST}:{os.getenv('PROXY_CLIENT_PORT', '8900')}",
}

# Endpoints principales a escanear
API_ENDPOINTS = {
    "api-gateway": [
        "/actuator/health",
        "/user-service/api/users",
        "/product-service/api/products",
        "/order-service/api/orders",
        "/payment-service/api/payments",
    ],
    "user-service": [
        "/user-service/api/users",
        "/user-service/api/address",
        "/user-service/api/credentials",
    ],
    "product-service": [
        "/product-service/api/products",
        "/product-service/api/categories",
    ],
    "order-service": [
        "/order-service/api/orders",
        "/order-service/api/carts",
    ],
    "payment-service": [
        "/payment-service/api/payments",
    ],
    "shipping-service": [
        "/shipping-service/api/shippings",
    ],
    "favourite-service": [
        "/favourite-service/api/favourites",
    ],
    "proxy-client": [
        "/app/api/authenticate",
    ],
}

# Contextos de autenticación (si es necesario)
AUTH_CONTEXTS = {
    "default": {
        "login_url": f"http://{BASE_HOST}:{os.getenv('API_GATEWAY_PORT', '8080')}/app/api/authenticate",
        "username": os.getenv("DEFAULT_USERNAME", "admin"),
        "password": os.getenv("DEFAULT_PASSWORD", "admin123"),
    }
}

# Reglas de ZAP a desactivar (si causan falsos positivos)
DISABLED_RULES = []

# Nivel de alerta mínimo a reportar
MIN_ALERT_LEVEL = "Low"  # Low, Medium, High, Informational

