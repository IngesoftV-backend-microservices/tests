"""
Clase base para pruebas de rendimiento con Locust.
"""
from locust import HttpUser, between
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class BaseLocustUser(HttpUser):
    """Clase base para usuarios de Locust con utilidades comunes."""
    
    abstract = True
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jwt_token = None
        self.created_resources = {
            "user_ids": [],
            "product_ids": [],
            "category_ids": [],
            "cart_ids": [],
            "order_ids": [],
            "payment_ids": [],
            "address_ids": [],
        }
    
    def on_start(self):
        """Ejecutado al inicio de cada usuario virtual."""
        self.authenticate()
    
    def authenticate(self):
        """Autenticar y obtener token JWT."""
        try:
            auth_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = self.client.post("/app/api/authenticate", json=auth_data, name="Authenticate")
            if response.status_code in [200, 201]:
                data = response.json()
                if isinstance(data, dict) and "jwtToken" in data:
                    self.jwt_token = data["jwtToken"]
                elif isinstance(data, dict) and "token" in data:
                    self.jwt_token = data["token"]
                elif isinstance(data, str):
                    self.jwt_token = data
        except Exception:
            self.jwt_token = None
    
    def get_headers(self) -> Dict[str, str]:
        """Obtener headers con autenticación."""
        headers = {"Content-Type": "application/json"}
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers
    
    def cleanup_resources(self):
        """Limpiar recursos creados durante las pruebas."""
        headers = self.get_headers()
        
        for payment_id in self.created_resources["payment_ids"]:
            try:
                self.client.delete(f"/payment-service/api/payments/{payment_id}", headers=headers, name="Cleanup Payment")
            except:
                pass
        
        for order_id in self.created_resources["order_ids"]:
            try:
                self.client.delete(f"/order-service/api/orders/{order_id}", headers=headers, name="Cleanup Order")
            except:
                pass
        
        for cart_id in self.created_resources["cart_ids"]:
            try:
                self.client.delete(f"/order-service/api/carts/{cart_id}", headers=headers, name="Cleanup Cart")
            except:
                pass
        
        for product_id in self.created_resources["product_ids"]:
            try:
                self.client.delete(f"/product-service/api/products/{product_id}", headers=headers, name="Cleanup Product")
            except:
                pass
        
        for category_id in self.created_resources["category_ids"]:
            try:
                self.client.delete(f"/product-service/api/categories/{category_id}", headers=headers, name="Cleanup Category")
            except:
                pass
        
        for address_id in self.created_resources["address_ids"]:
            try:
                self.client.delete(f"/user-service/api/address/{address_id}", headers=headers, name="Cleanup Address")
            except:
                pass
        
        for user_id in self.created_resources["user_ids"]:
            try:
                self.client.delete(f"/user-service/api/users/{user_id}", headers=headers, name="Cleanup User")
            except:
                pass

