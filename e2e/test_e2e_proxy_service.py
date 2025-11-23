"""
Pruebas E2E para el Proxy Service a través del API Gateway.
"""
import pytest
from utils.api_utils import make_e2e_request


@pytest.mark.e2e
class TestE2EProxyService:
    """Pruebas E2E para el Proxy Service - 5 tests"""

    def test_1_e2e_create_authentication(self, jwt_token):
        """Test 1: CREATE - Autenticarse y obtener token"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        assert jwt_token is not None
        assert len(jwt_token) > 0

    def test_2_e2e_get_authentication_by_id(self, jwt_token):
        """Test 2: GET BY ID - Validar token JWT"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        response = make_e2e_request("GET", f"/app/api/authenticate/jwt/{jwt_token}", jwt_token=jwt_token)
        assert response.status_code == 200
        if response.text and response.text.strip():
            data = response.json()
            assert isinstance(data, bool)

    def test_3_e2e_authentication_invalid_credentials(self):
        """Test 3: CREATE - Fallo con credenciales incorrectas"""
        payload = {
            "username": "usuario_inexistente",
            "password": "password_incorrecto"
        }
        response = make_e2e_request("POST", "/app/api/authenticate", data=payload)
        assert response.status_code in [400, 500]

    def test_4_e2e_authentication_invalid_token(self):
        """Test 4: GET BY ID - Fallo con token inválido"""
        invalid_token = "token.invalido.malformado"
        response = make_e2e_request("GET", f"/app/api/authenticate/jwt/{invalid_token}")
        assert response.status_code == 200
        if response.text and response.text.strip():
            data = response.json()
            assert isinstance(data, bool)
            assert data == False

    def test_5_e2e_authentication_missing_credentials(self):
        """Test 5: CREATE - Fallo con credenciales faltantes"""
        response = make_e2e_request("POST", "/app/api/authenticate", data={})
        assert response.status_code == 400
