"""
Pruebas de rendimiento para Order Service.
"""
from locust import task, between
from performance.locust_base import BaseLocustUser
from utils.helpers import generate_user_data, generate_cart_data, generate_order_data
import random


class OrderServiceUser(BaseLocustUser):
    """Usuario virtual para pruebas de rendimiento del Order Service."""
    
    host = "http://localhost:8080"
    weight = 2
    
    def ensure_user_exists(self):
        """Asegurar que existe un usuario."""
        if not self.created_resources["user_ids"]:
            user_data = generate_user_data()
            headers = self.get_headers()
            response = self.client.post(
                "/user-service/api/users",
                json=user_data,
                headers=headers,
                name="Create User For Order"
            )
            if response.status_code in [200, 201]:
                data = response.json()
                if "userId" in data:
                    self.created_resources["user_ids"].append(data["userId"])
            elif response.status_code == 409:
                get_users = self.client.get(
                    "/user-service/api/users",
                    headers=headers,
                    name="Get Users After Conflict"
                )
                if get_users.status_code == 200:
                    users_data = get_users.json()
                    if isinstance(users_data, dict) and "collection" in users_data:
                        users = users_data["collection"]
                    elif isinstance(users_data, list):
                        users = users_data
                    else:
                        users = []
                    if users and len(users) > 0:
                        user_id = users[0].get("userId")
                        if user_id:
                            self.created_resources["user_ids"].append(user_id)
    
    @task(3)
    def create_cart(self):
        """Crear carrito."""
        self.ensure_user_exists()
        if not self.created_resources["user_ids"]:
            return
        
        user_id = random.choice(self.created_resources["user_ids"])
        cart_data = generate_cart_data(user_id)
        headers = self.get_headers()
        
        with self.client.post(
            "/order-service/api/carts",
            json=cart_data,
            headers=headers,
            name="Create Cart",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "cartId" in data:
                    self.created_resources["cart_ids"].append(data["cartId"])
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(4)
    def get_all_carts(self):
        """Obtener todos los carritos."""
        headers = self.get_headers()
        self.client.get(
            "/order-service/api/carts",
            headers=headers,
            name="Get All Carts",
            catch_response=True
        )
    
    @task(3)
    def create_order(self):
        """Crear orden."""
        if not self.created_resources["cart_ids"]:
            self.create_cart()
        
        if self.created_resources["cart_ids"]:
            cart_id = random.choice(self.created_resources["cart_ids"])
            order_data = generate_order_data(cart_id)
            headers = self.get_headers()
            
            with self.client.post(
                "/order-service/api/orders",
                json=order_data,
                headers=headers,
                name="Create Order",
                catch_response=True
            ) as response:
                if response.status_code in [200, 201]:
                    data = response.json()
                    if "orderId" in data:
                        self.created_resources["order_ids"].append(data["orderId"])
                    response.success()
                else:
                    response.failure(f"Status {response.status_code}")
    
    @task(5)
    def get_all_orders(self):
        """Obtener todas las órdenes."""
        headers = self.get_headers()
        self.client.get(
            "/order-service/api/orders",
            headers=headers,
            name="Get All Orders",
            catch_response=True
        )
    
    @task(4)
    def get_order_by_id(self):
        """Obtener orden por ID."""
        if not self.created_resources["order_ids"]:
            return
        
        order_id = random.choice(self.created_resources["order_ids"])
        headers = self.get_headers()
        self.client.get(
            f"/order-service/api/orders/{order_id}",
            headers=headers,
            name="Get Order By ID",
            catch_response=True
        )
    
    @task(2)
    def update_order(self):
        """Actualizar orden."""
        if not self.created_resources["order_ids"]:
            return
        
        order_id = random.choice(self.created_resources["order_ids"])
        headers = self.get_headers()
        
        get_response = self.client.get(
            f"/order-service/api/orders/{order_id}",
            headers=headers,
            name="Get Order For Update"
        )
        
        if get_response.status_code == 200:
            order_data = get_response.json()
            order_data["orderDesc"] = "Updated Order"
            self.client.put(
                f"/order-service/api/orders/{order_id}",
                json=order_data,
                headers=headers,
                name="Update Order",
                catch_response=True
            )

