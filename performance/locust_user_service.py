"""
Pruebas de rendimiento para User Service.
"""
from locust import task, between
from performance.locust_base import BaseLocustUser
from utils.helpers import generate_user_data, generate_address_data
import random


class UserServiceUser(BaseLocustUser):
    """Usuario virtual para pruebas de rendimiento del User Service."""
    
    host = "http://localhost:8080"
    weight = 3
    
    @task(3)
    def create_user(self):
        """Crear usuario."""
        user_data = generate_user_data()
        headers = self.get_headers()
        with self.client.post(
            "/user-service/api/users",
            json=user_data,
            headers=headers,
            name="Create User",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "userId" in data:
                    self.created_resources["user_ids"].append(data["userId"])
                response.success()
            elif response.status_code == 409:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(5)
    def get_all_users(self):
        """Obtener todos los usuarios."""
        headers = self.get_headers()
        self.client.get(
            "/user-service/api/users",
            headers=headers,
            name="Get All Users",
            catch_response=True
        )
    
    @task(4)
    def get_user_by_id(self):
        """Obtener usuario por ID."""
        if not self.created_resources["user_ids"]:
            return
        
        user_id = random.choice(self.created_resources["user_ids"])
        headers = self.get_headers()
        self.client.get(
            f"/user-service/api/users/{user_id}",
            headers=headers,
            name="Get User By ID",
            catch_response=True
        )
    
    @task(2)
    def update_user(self):
        """Actualizar usuario."""
        if not self.created_resources["user_ids"]:
            return
        
        user_id = random.choice(self.created_resources["user_ids"])
        headers = self.get_headers()
        
        get_response = self.client.get(
            f"/user-service/api/users/{user_id}",
            headers=headers,
            name="Get User For Update"
        )
        
        if get_response.status_code == 200:
            user_data = get_response.json()
            user_data["firstName"] = "UpdatedName"
            self.client.put(
                "/user-service/api/users",
                json=user_data,
                headers=headers,
                name="Update User",
                catch_response=True
            )
    
    @task(2)
    def create_address(self):
        """Crear dirección para usuario."""
        if not self.created_resources["user_ids"]:
            return
        
        user_id = random.choice(self.created_resources["user_ids"])
        address_data = generate_address_data(user_id)
        headers = self.get_headers()
        
        with self.client.post(
            "/user-service/api/address",
            json=address_data,
            headers=headers,
            name="Create Address",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "addressId" in data:
                    self.created_resources["address_ids"].append(data["addressId"])
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(3)
    def get_address_by_id(self):
        """Obtener dirección por ID."""
        if not self.created_resources["address_ids"]:
            return
        
        address_id = random.choice(self.created_resources["address_ids"])
        headers = self.get_headers()
        self.client.get(
            f"/user-service/api/address/{address_id}",
            headers=headers,
            name="Get Address By ID",
            catch_response=True
        )

