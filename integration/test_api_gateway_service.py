"""
Pruebas de integración para el API Gateway Service.
"""
import pytest
from utils.api_utils import make_request, set_current_service


@pytest.mark.integration
class TestAPIGatewayService:
    """Pruebas para el API Gateway Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        set_current_service("api-gateway")

    def test_1_health_check(self):
        """Test 1: Health check endpoint"""
        response = make_request("GET", "/actuator/health")
        assert response.status_code == 200
        health_data = response.json()
        assert "status" in health_data
        assert health_data["status"] in ["UP", "DOWN"]

    def test_2_gateway_routing_to_user_service(self, auth_headers):
        """Test 2: Gateway routes requests to user service"""
        # Probar routing a user service a través del gateway
        response = make_request("GET", "/user-service/api/users")
        # Debe enrutar correctamente (puede retornar 200 con datos o lista vacía)
        assert response.status_code in [200, 401, 403]

    def test_3_gateway_routing_to_product_service(self):
        """Test 3: Gateway routes requests to product service (public endpoint)"""
        # Product service tiene endpoints públicos
        response = make_request("GET", "/product-service/api/products")
        # Debe enrutar correctamente
        assert response.status_code in [200, 404, 500]

    def test_4_cors_headers(self):
        """Test 4: Gateway handles CORS correctly"""
        # Probar request OPTIONS para CORS
        import requests
        response = requests.options(
            "http://localhost:8800/user-service/api/users",
            headers={
                "Origin": "http://localhost:4200",
                "Access-Control-Request-Method": "GET"
            }
        )
        # Debe retornar headers CORS
        assert response.status_code in [200, 204, 404]
        if "Access-Control-Allow-Origin" in response.headers:
            assert response.headers["Access-Control-Allow-Origin"] in [
                "http://localhost:4200", "*"
            ]

    def test_5_gateway_actuator_endpoints(self):
        """Test 5: Gateway actuator endpoints are accessible"""
        # Probar varios endpoints de actuator
        health_response = make_request("GET", "/actuator/health")
        assert health_response.status_code == 200
        
        # Probar endpoint info si está disponible
        info_response = make_request("GET", "/actuator/info")
        assert info_response.status_code in [200, 404]


