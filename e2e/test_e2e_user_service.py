"""
Pruebas E2E para el User Service a través del API Gateway.
"""
import pytest
from utils.api_utils import make_e2e_request
from utils.helpers import generate_user_data, generate_address_data


@pytest.mark.e2e
class TestE2EUserService:
    """Pruebas E2E para el User Service - 5 tests"""

    def test_e2e_complete_user_registration(self, jwt_token):
        """E2E Test 1: Registro completo de usuario"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user = user_response.json()
        user_id = user["userId"]
        
        try:
            get_user_response = make_e2e_request("GET", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
            assert get_user_response.status_code == 200
            retrieved_user = get_user_response.json()
            assert retrieved_user["userId"] == user_id
            assert retrieved_user["email"] == user_data["email"]
            
            updated_user = user.copy()
            updated_user["firstName"] = "UpdatedFirstName"
            updated_user["lastName"] = "UpdatedLastName"
            update_response = make_e2e_request("PUT", "/api/users", data=updated_user, service_name="user", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            verify_response = make_e2e_request("GET", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
            updated_user_data = verify_response.json()
            assert updated_user_data["firstName"] == "UpdatedFirstName"
            assert updated_user_data["lastName"] == "UpdatedLastName"
        finally:
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_user_with_addresses_workflow(self, jwt_token):
        """E2E Test 2: Flujo completo de usuario con direcciones"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        address_ids = []
        try:
            for _ in range(2):
                address_data = generate_address_data(user_id)
                address_response = make_e2e_request("POST", "/api/address", data=address_data, service_name="user", jwt_token=jwt_token)
                assert address_response.status_code in [200, 201]
                address_ids.append(address_response.json()["addressId"])
            
            for address_id in address_ids:
                get_address_response = make_e2e_request("GET", f"/api/address/{address_id}", service_name="user", jwt_token=jwt_token)
                assert get_address_response.status_code == 200
                address = get_address_response.json()
                assert address["addressId"] == address_id
                user_info = address.get("user") or address.get("userDto")
                if user_info:
                    assert user_info.get("userId") == user_id
        finally:
            for address_id in address_ids:
                make_e2e_request("DELETE", f"/api/address/{address_id}", service_name="user", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_user_profile_management(self, jwt_token):
        """E2E Test 3: Gestión completa de perfil de usuario"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        try:
            initial_profile = make_e2e_request("GET", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
            assert initial_profile.status_code == 200
            initial_data = initial_profile.json()
            
            updated_data = initial_data.copy()
            updated_data["firstName"] = "NewFirstName"
            updated_data["lastName"] = "NewLastName"
            updated_data["imageUrl"] = "https://example.com/new-image.jpg"
            
            update_response = make_e2e_request("PUT", "/api/users", data=updated_data, service_name="user", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            verify_response = make_e2e_request("GET", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
            verified_data = verify_response.json()
            assert verified_data["firstName"] == "NewFirstName"
            assert verified_data["lastName"] == "NewLastName"
            assert verified_data["imageUrl"] == "https://example.com/new-image.jpg"
            
            all_users_response = make_e2e_request("GET", "/api/users", service_name="user", jwt_token=jwt_token)
            assert all_users_response.status_code == 200
            users_data = all_users_response.json()
            users_list = users_data.get("collection", []) if isinstance(users_data, dict) else users_data
            user_ids = [u.get("userId") for u in users_list if isinstance(u, dict)]
            assert user_id in user_ids
        finally:
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_multiple_users_management(self, jwt_token):
        """E2E Test 4: Gestión de múltiples usuarios"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        created_users = []
        try:
            for _ in range(3):
                user_data = generate_user_data()
                user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
                assert user_response.status_code in [200, 201]
                created_users.append(user_response.json())
            
            all_users_response = make_e2e_request("GET", "/api/users", service_name="user", jwt_token=jwt_token)
            assert all_users_response.status_code == 200
            users_data = all_users_response.json()
            users_list = users_data.get("collection", []) if isinstance(users_data, dict) else users_data
            all_user_ids = [u.get("userId") for u in users_list if isinstance(u, dict)]
            
            for created_user in created_users:
                assert created_user["userId"] in all_user_ids
                get_user_response = make_e2e_request("GET", f"/api/users/{created_user['userId']}", service_name="user", jwt_token=jwt_token)
                assert get_user_response.status_code == 200
                retrieved_user = get_user_response.json()
                assert retrieved_user["userId"] == created_user["userId"]
                assert retrieved_user["email"] == created_user["email"]
        finally:
            for user in created_users:
                make_e2e_request("DELETE", f"/api/users/{user['userId']}", service_name="user", jwt_token=jwt_token)

    def test_e2e_user_lifecycle_complete(self, jwt_token):
        """E2E Test 5: Ciclo de vida completo de usuario"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        try:
            address_data = generate_address_data(user_id)
            address_response = make_e2e_request("POST", "/api/address", data=address_data, service_name="user", jwt_token=jwt_token)
            assert address_response.status_code in [200, 201]
            address_id = address_response.json()["addressId"]
            
            updated_user = user_response.json().copy()
            updated_user["firstName"] = "LifecycleTest"
            update_response = make_e2e_request("PUT", "/api/users", data=updated_user, service_name="user", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            final_user_response = make_e2e_request("GET", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
            assert final_user_response.status_code == 200
            assert final_user_response.json()["firstName"] == "LifecycleTest"
            
            delete_address_response = make_e2e_request("DELETE", f"/api/address/{address_id}", service_name="user", jwt_token=jwt_token)
            assert delete_address_response.status_code in [200, 204]
            
            delete_user_response = make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
            assert delete_user_response.status_code in [200, 204]
            
            get_after_delete = make_e2e_request("GET", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
            assert get_after_delete.status_code in [404, 400]
        except:
            if 'address_id' in locals():
                make_e2e_request("DELETE", f"/api/address/{address_id}", service_name="user", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
            raise
