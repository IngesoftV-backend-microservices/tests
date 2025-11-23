"""
Pruebas de rendimiento para Product Service.
"""
from locust import task, between
from performance.locust_base import BaseLocustUser
from utils.helpers import generate_category_data, generate_product_data
import random


class ProductServiceUser(BaseLocustUser):
    """Usuario virtual para pruebas de rendimiento del Product Service."""
    
    host = "http://localhost:8080"
    weight = 3
    
    @task(2)
    def create_category(self):
        """Crear categoría."""
        category_data = generate_category_data()
        headers = self.get_headers()
        with self.client.post(
            "/product-service/api/categories",
            json=category_data,
            headers=headers,
            name="Create Category",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "categoryId" in data:
                    self.created_resources["category_ids"].append(data["categoryId"])
                response.success()
            elif response.status_code == 409:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(3)
    def create_product(self):
        """Crear producto."""
        if not self.created_resources["category_ids"]:
            category_data = generate_category_data()
            headers = self.get_headers()
            cat_response = self.client.post(
                "/product-service/api/categories",
                json=category_data,
                headers=headers,
                name="Create Category For Product"
            )
            if cat_response.status_code in [200, 201]:
                cat_data = cat_response.json()
                if "categoryId" in cat_data:
                    self.created_resources["category_ids"].append(cat_data["categoryId"])
            elif cat_response.status_code == 409:
                get_cats = self.client.get(
                    "/product-service/api/categories",
                    headers=headers,
                    name="Get Categories After Conflict"
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
                name="Create Product",
                catch_response=True
            ) as response:
                if response.status_code in [200, 201]:
                    data = response.json()
                    if "productId" in data:
                        self.created_resources["product_ids"].append(data["productId"])
                    response.success()
                else:
                    response.failure(f"Status {response.status_code}")
    
    @task(5)
    def get_all_products(self):
        """Obtener todos los productos."""
        headers = self.get_headers()
        self.client.get(
            "/product-service/api/products",
            headers=headers,
            name="Get All Products",
            catch_response=True
        )
    
    @task(4)
    def get_product_by_id(self):
        """Obtener producto por ID."""
        if not self.created_resources["product_ids"]:
            return
        
        product_id = random.choice(self.created_resources["product_ids"])
        headers = self.get_headers()
        self.client.get(
            f"/product-service/api/products/{product_id}",
            headers=headers,
            name="Get Product By ID",
            catch_response=True
        )
    
    @task(3)
    def get_all_categories(self):
        """Obtener todas las categorías."""
        headers = self.get_headers()
        self.client.get(
            "/product-service/api/categories",
            headers=headers,
            name="Get All Categories",
            catch_response=True
        )
    
    @task(2)
    def update_product(self):
        """Actualizar producto."""
        if not self.created_resources["product_ids"]:
            return
        
        product_id = random.choice(self.created_resources["product_ids"])
        headers = self.get_headers()
        
        get_response = self.client.get(
            f"/product-service/api/products/{product_id}",
            headers=headers,
            name="Get Product For Update"
        )
        
        if get_response.status_code == 200:
            product_data = get_response.json()
            product_data["productTitle"] = "Updated Product"
            self.client.put(
                f"/product-service/api/products/{product_id}",
                json=product_data,
                headers=headers,
                name="Update Product",
                catch_response=True
            )

