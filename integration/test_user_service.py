"""
Pruebas de integración para el User Service.
Ejemplo de cómo simplificar los tests usando fixtures y utilidades.
"""
import pytest
from utils.api_utils import make_request, set_current_service
from utils.helpers import generate_user_data


@pytest.mark.integration
class TestUserService:
    """Pruebas para el User Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        set_current_service("user-service")

    @pytest.fixture
    def create_test_user(self):
        """Fixture para crear un usuario de prueba."""
        user_data = generate_user_data()
        response = make_request("POST", "/api/users", data=user_data)
        assert response.status_code in [200, 201], f"Error al crear usuario: {response.text}"

        created_user = response.json()
        user_id = created_user.get("userId")

        yield {"id": user_id, "data": created_user}

        make_request("DELETE", f"/api/users/{user_id}")

    def test_1_create_user(self):
        """Test 1: CREATE - Create a new user"""
        user_data = generate_user_data()
        response = make_request("POST", "/api/users", data=user_data)

        assert response.status_code in [200, 201]
        result = response.json()
        assert result["userId"] is not None
        assert result["firstName"] == user_data["firstName"]

        # Limpiar
        make_request("DELETE", f'/api/users/{result["userId"]}')

    def test_2_get_all_users(self):
        """Test 2: GET ALL - Get all users"""
        response = make_request("GET", "/api/users")

        assert response.status_code == 200
        result = response.json()
        if isinstance(result, dict) and "collection" in result:
            assert isinstance(result["collection"], list)
        elif isinstance(result, list):
            assert len(result) >= 0
        else:
            assert False, f"Formato de respuesta inesperado: {type(result)}"

    def test_3_get_user_by_id(self, create_test_user):
        """Test 3: GET BY ID - Get user by ID"""
        user = create_test_user
        response = make_request("GET", f'/api/users/{user["id"]}')

        assert response.status_code == 200
        result = response.json()
        assert result["userId"] == user["id"]
        assert result["firstName"] == user["data"]["firstName"]

    def test_4_update_user(self, create_test_user):
        """Test 4: UPDATE - Update user"""
        user = create_test_user
        updated_data = user["data"].copy()
        updated_data["firstName"] = "UpdatedFirstName"
        updated_data["lastName"] = "UpdatedLastName"

        response = make_request("PUT", "/api/users", data=updated_data)

        assert response.status_code == 200
        result = response.json()
        assert result["firstName"] == "UpdatedFirstName"
        assert result["lastName"] == "UpdatedLastName"

    def test_5_delete_user(self):
        """Test 5: DELETE - Delete user"""
        user_data = generate_user_data()
        create_response = make_request("POST", "/api/users", data=user_data)
        assert create_response.status_code in [200, 201]
        user_id = create_response.json()["userId"]

        delete_response = make_request("DELETE", f"/api/users/{user_id}")
        assert delete_response.status_code in [200, 204]

