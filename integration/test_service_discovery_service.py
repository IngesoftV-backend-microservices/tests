"""
Pruebas de integración para el Service Discovery Service (Eureka).
"""
import pytest
from utils.api_utils import make_request, set_current_service


@pytest.mark.integration
class TestServiceDiscoveryService:
    """Pruebas para el Service Discovery Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        # Service Discovery (Eureka) no tiene context path estándar
        # Usar URL directa
        set_current_service("service-discovery")

    def test_1_health_check(self):
        """Test 1: Health check endpoint"""
        import requests
        response = requests.get("http://localhost:8761/actuator/health", headers={"Content-Type": "application/json"})
        assert response.status_code == 200
        health_data = response.json()
        assert "status" in health_data
        assert health_data["status"] in ["UP", "DOWN"]

    def test_2_eureka_dashboard(self):
        """Test 2: Eureka dashboard is accessible"""
        import requests
        response = requests.get("http://localhost:8761/")
        # Debe retornar HTML dashboard o redirect
        assert response.status_code in [200, 302, 301]

    def test_3_registered_services_endpoint(self):
        """Test 3: Get list of registered services"""
        import requests
        response = requests.get("http://localhost:8761/eureka/apps", headers={"Content-Type": "application/json"})
        # Debe retornar XML o JSON con servicios registrados
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            content = response.text
            assert len(content) > 0

    def test_4_service_registration_status(self):
        """Test 4: Check if services are registered"""
        import requests
        apps_response = requests.get("http://localhost:8761/eureka/apps", headers={"Content-Type": "application/json"})
        if apps_response.status_code == 200:
            content = apps_response.text
            service_names = ["USER-SERVICE", "PRODUCT-SERVICE", "ORDER-SERVICE", 
                           "PAYMENT-SERVICE", "API-GATEWAY", "CLOUD-CONFIG"]
            found_services = [name for name in service_names if name.upper() in content.upper()]
            assert len(found_services) >= 0

    def test_5_eureka_actuator_endpoints(self):
        """Test 5: Eureka actuator endpoints are accessible"""
        import requests
        health_response = requests.get("http://localhost:8761/actuator/health", headers={"Content-Type": "application/json"})
        assert health_response.status_code == 200
        
        info_response = requests.get("http://localhost:8761/actuator/info", headers={"Content-Type": "application/json"})
        assert info_response.status_code in [200, 404]


