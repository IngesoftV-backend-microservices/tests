"""
Utilidades para hacer peticiones HTTP en los tests.
"""
import os
import requests
from typing import Dict, Any, Optional
from utils.helpers import build_integration_url, SERVICE_CONTEXT_PATHS


# Variable global para el servicio actual
_current_service: Optional[str] = None


def set_current_service(service_name: str) -> None:
    """Configurar el servicio actual para las pruebas."""
    global _current_service
    _current_service = service_name


def _normalize_service_name(service_name: str) -> str:
    """Normalizar nombre de servicio (user-service -> user, proxy-client -> proxy-client)"""
    if service_name.endswith("-service"):
        return service_name[:-8]
    # proxy-client no se normaliza
    if service_name == "proxy-client":
        return "proxy-client"
    return service_name


def get_base_url(service_name: Optional[str] = None) -> str:
    """Obtener la URL base del servicio."""
    service_name = service_name or _current_service
    if not service_name:
        raise ValueError("No service specified. Call set_current_service() first.")
    
    if "-" not in service_name:
        service_name = f"{service_name}-service"
    
    # Mapeo de nombres de servicio a URLs
    # BASE_HOST can be set dynamically (e.g., LoadBalancer IP in CI/CD)
    base_host = os.getenv("BASE_HOST", "localhost")
    service_urls = {
        "user-service": f"http://{base_host}:8700",
        "product-service": f"http://{base_host}:8500",
        "order-service": f"http://{base_host}:8300",
        "payment-service": f"http://{base_host}:8400",
        "shipping-service": f"http://{base_host}:8600",
        "favourite-service": f"http://{base_host}:8800",
        "api-gateway": f"http://{base_host}:8080",
        "cloud-config": f"http://{base_host}:9296",
        "service-discovery": f"http://{base_host}:8761",
        "proxy-client": f"http://{base_host}:8900",
    }
    
    return service_urls.get(service_name, "http://localhost:8080")


def make_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    service_name: Optional[str] = None
) -> requests.Response:
    """
    Hacer una petición HTTP simplificada.
    
    Args:
        method: Método HTTP (GET, POST, PUT, DELETE, PATCH)
        endpoint: Endpoint relativo (ej: "/api/users")
        data: Datos para enviar en el body (opcional)
        service_name: Nombre del servicio (opcional, usa el actual si no se especifica)
    
    Returns:
        Response object de requests
    """
    service_name = service_name or _current_service
    if not service_name:
        raise ValueError("No service specified. Call set_current_service() first.")
    
    base_url = get_base_url(service_name)
    
    normalized_name = _normalize_service_name(service_name)
    
    # Construir URL completa con context path
    if normalized_name in SERVICE_CONTEXT_PATHS:
        # build_integration_url devuelve solo el path (ej: "/user-service/api/users")
        context_path_endpoint = build_integration_url(normalized_name, endpoint)
        full_url = f"{base_url}{context_path_endpoint}"
    else:
        # Para servicios sin context path (gateway, config, etc.)
        full_url = f"{base_url}{endpoint}"
    
    # Headers por defecto
    headers = {"Content-Type": "application/json"}
    
    # Hacer la petición según el método
    method = method.upper()
    if method == "GET":
        response = requests.get(full_url, headers=headers)
    elif method == "POST":
        response = requests.post(full_url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(full_url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(full_url, headers=headers)
    elif method == "PATCH":
        response = requests.patch(full_url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    return response


def make_e2e_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    service_name: Optional[str] = None,
    jwt_token: Optional[str] = None
) -> requests.Response:
    """
    Hacer una petición HTTP a través del API Gateway (para tests E2E).
    
    Args:
        method: Método HTTP (GET, POST, PUT, DELETE, PATCH)
        endpoint: Endpoint relativo (ej: "/api/users" o "/app/api/authenticate")
        data: Datos para enviar en el body (opcional)
        service_name: Nombre del servicio (ej: "user", "product", "order")
        jwt_token: Token JWT para autenticación (opcional)
    
    Returns:
        Response object de requests
    """
    # API Gateway está en el puerto 8080
    # BASE_HOST can be set dynamically (e.g., LoadBalancer IP in CI/CD)
    base_host = os.getenv("BASE_HOST", "localhost")
    base_url = f"http://{base_host}:8080"
    
    # Si el endpoint ya tiene un prefijo (ej: "/app/"), usarlo directamente
    # Si no, construir endpoint con el prefijo del servicio
    if service_name and not endpoint.startswith("/app/"):
        if service_name.endswith("-service"):
            service_name = service_name[:-8]
        # El API Gateway enruta /service-name/** a los servicios
        endpoint = f"/{service_name}-service{endpoint}"
    
    full_url = f"{base_url}{endpoint}"
    
    # Headers
    headers = {"Content-Type": "application/json"}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    
    # Hacer la petición según el método
    method = method.upper()
    if method == "GET":
        response = requests.get(full_url, headers=headers)
    elif method == "POST":
        response = requests.post(full_url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(full_url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(full_url, headers=headers)
    elif method == "PATCH":
        response = requests.patch(full_url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    return response

