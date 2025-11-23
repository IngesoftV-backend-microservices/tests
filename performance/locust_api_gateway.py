"""
Pruebas de rendimiento para API Gateway (endpoints principales).
"""
from locust import task, between
from performance.locust_base import BaseLocustUser
from utils.helpers import generate_user_data, generate_category_data, generate_product_data
import random


class APIGatewayUser(BaseLocustUser):
    """Usuario virtual para pruebas de rendimiento del API Gateway."""
    
    host = "http://localhost:8080"
    weight = 4
    
    @task(5)
    def get_all_users(self):
        """Obtener todos los usuarios a través del API Gateway."""
        headers = self.get_headers()
        self.client.get(
            "/user-service/api/users",
            headers=headers,
            name="API Gateway - Get All Users",
            catch_response=True
        )
    
    @task(4)
    def get_all_products(self):
        """Obtener todos los productos a través del API Gateway."""
        headers = self.get_headers()
        self.client.get(
            "/product-service/api/products",
            headers=headers,
            name="API Gateway - Get All Products",
            catch_response=True
        )
    
    @task(3)
    def get_all_orders(self):
        """Obtener todas las órdenes a través del API Gateway."""
        headers = self.get_headers()
        self.client.get(
            "/order-service/api/orders",
            headers=headers,
            name="API Gateway - Get All Orders",
            catch_response=True
        )
    
    @task(2)
    def create_user(self):
        """Crear usuario a través del API Gateway."""
        user_data = generate_user_data()
        headers = self.get_headers()
        with self.client.post(
            "/user-service/api/users",
            json=user_data,
            headers=headers,
            name="API Gateway - Create User",
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
    
    @task(2)
    def create_product(self):
        """Crear producto a través del API Gateway."""
        if not self.created_resources["category_ids"]:
            category_data = generate_category_data()
            headers = self.get_headers()
            cat_response = self.client.post(
                "/product-service/api/categories",
                json=category_data,
                headers=headers,
                name="API Gateway - Create Category"
            )
            if cat_response.status_code in [200, 201]:
                cat_data = cat_response.json()
                if "categoryId" in cat_data:
                    self.created_resources["category_ids"].append(cat_data["categoryId"])
            elif cat_response.status_code == 409:
                get_cats = self.client.get(
                    "/product-service/api/categories",
                    headers=headers,
                    name="API Gateway - Get Categories After Conflict"
                )
                if get_cats.status_code == 200:
                    cats_data = get_cats.json()
                    if isinstance(cats_data, dict) and "collection" in cats_data:
                        cats = cats_data["collection"]
                    elif isinstance(cats_data, list):
                        cats = cats_data
                    else:
                        cats = []
                    if cats and len(cats) > 0:
                        cat_id = cats[0].get("categoryId")
                        if cat_id:
                            self.created_resources["category_ids"].append(cat_id)
        
        if self.created_resources["category_ids"]:
            category_id = random.choice(self.created_resources["category_ids"])
            product_data = generate_product_data(category_id)
            headers = self.get_headers()
            
            with self.client.post(
                "/product-service/api/products",
                json=product_data,
                headers=headers,
                name="API Gateway - Create Product",
                catch_response=True
            ) as response:
                if response.status_code in [200, 201]:
                    data = response.json()
                    if "productId" in data:
                        self.created_resources["product_ids"].append(data["productId"])
                    response.success()
                else:
                    response.failure(f"Status {response.status_code}")

