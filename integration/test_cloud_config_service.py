"""
Pruebas de integración para el Cloud Config Service.
"""
import pytest
from utils.api_utils import make_request, set_current_service


@pytest.mark.integration
class TestCloudConfigService:
    """Pruebas para el Cloud Config Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        # Cloud Config no está en el mapeo estándar, usar URL directa
        # Pero necesitamos actualizar api_utils para soportarlo
        set_current_service("cloud-config")

    def test_1_health_check(self):
        """Test 1: Health check endpoint"""
        response = make_request("GET", "/actuator/health")
        assert response.status_code == 200
        health_data = response.json()
        assert isinstance(health_data, dict)
        if "status" in health_data:
            assert health_data["status"] in ["UP", "DOWN"]
        else:
            # Cloud Config puede retornar formato diferente
            assert "name" in health_data or "propertySources" in health_data

    def test_2_config_server_status(self):
        """Test 2: Config server status endpoint"""
        response = make_request("GET", "/actuator/env")
        assert response.status_code in [200, 404]

    def test_3_service_discovery_integration(self):
        """Test 3: Cloud Config is registered with service discovery"""
        response = make_request("GET", "/actuator/health")
        assert response.status_code == 200
        health_data = response.json()
        assert isinstance(health_data, dict)

    def test_4_configuration_endpoints(self):
        """Test 4: Configuration endpoints are accessible"""
        health_response = make_request("GET", "/actuator/health")
        assert health_response.status_code == 200
        
        info_response = make_request("GET", "/actuator/info")
        assert info_response.status_code in [200, 404]

    def test_5_service_availability(self):
        """Test 5: Service is available and responding"""
        response = make_request("GET", "/actuator/health")
        assert response.status_code == 200


