"""
Pruebas de rendimiento para Payment Service.
"""
from locust import task, between
from performance.locust_base import BaseLocustUser
from utils.helpers import generate_payment_data
import random


class PaymentServiceUser(BaseLocustUser):
    """Usuario virtual para pruebas de rendimiento del Payment Service."""
    
    host = "http://localhost:8080"
    weight = 1
    
    def ensure_order_exists(self):
        """Asegurar que existe una orden en estado ORDERED."""
        if not self.created_resources["order_ids"]:
            from utils.helpers import generate_user_data, generate_cart_data, generate_order_data
            
            user_data = generate_user_data()
            headers = self.get_headers()
            user_response = self.client.post(
                "/user-service/api/users",
                json=user_data,
                headers=headers,
                name="Create User For Payment"
            )
            
            user_id = None
            if user_response.status_code in [200, 201]:
                user_id = user_response.json().get("userId")
                if user_id:
                    self.created_resources["user_ids"].append(user_id)
            elif user_response.status_code == 409:
                get_users = self.client.get(
                    "/user-service/api/users",
                    headers=headers,
                    name="Get Users For Payment After Conflict"
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
            
            if not user_id:
                return None
            
            cart_data = generate_cart_data(user_id)
            cart_response = self.client.post(
                "/order-service/api/carts",
                json=cart_data,
                headers=headers,
                name="Create Cart For Payment"
            )
            
            if cart_response.status_code in [200, 201]:
                cart_id = cart_response.json().get("cartId")
                if cart_id:
                    self.created_resources["cart_ids"].append(cart_id)
                    
                    order_data = generate_order_data(cart_id)
                    order_response = self.client.post(
                        "/order-service/api/orders",
                        json=order_data,
                        headers=headers,
                        name="Create Order For Payment"
                    )
                    
                    if order_response.status_code in [200, 201]:
                        order_id = order_response.json().get("orderId")
                        if order_id:
                            self.client.patch(
                                f"/order-service/api/orders/{order_id}/status",
                                headers=headers,
                                name="Update Order Status"
                            )
                            self.created_resources["order_ids"].append(order_id)
    
    @task(2)
    def create_payment(self):
        """Crear pago."""
        from utils.helpers import generate_user_data, generate_cart_data, generate_order_data
        
        headers = self.get_headers()
        user_data = generate_user_data()
        user_response = self.client.post(
            "/user-service/api/users",
            json=user_data,
            headers=headers,
            name="Create User For Payment",
            catch_response=True
        )
        
        if user_response.status_code not in [200, 201]:
            return
        
        user_id = user_response.json().get("userId")
        if not user_id:
            return
        
        cart_data = generate_cart_data(user_id)
        cart_response = self.client.post(
            "/order-service/api/carts",
            json=cart_data,
            headers=headers,
            name="Create Cart For Payment",
            catch_response=True
        )
        
        if cart_response.status_code not in [200, 201]:
            return
        
        cart_id = cart_response.json().get("cartId")
        if not cart_id:
            return
        
        order_data = generate_order_data(cart_id)
        order_response = self.client.post(
            "/order-service/api/orders",
            json=order_data,
            headers=headers,
            name="Create Order For Payment",
            catch_response=True
        )
        
        if order_response.status_code not in [200, 201]:
            return
        
        order_id = order_response.json().get("orderId")
        if not order_id:
            return
        
        status_response = self.client.patch(
            f"/order-service/api/orders/{order_id}/status",
            headers=headers,
            name="Update Order Status To Ordered",
            catch_response=True
        )
        
        payment_data = generate_payment_data(order_id)
        
        with self.client.post(
            "/payment-service/api/payments",
            json=payment_data,
            headers=headers,
            name="Create Payment",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "paymentId" in data:
                    self.created_resources["payment_ids"].append(data["paymentId"])
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(5)
    def get_all_payments(self):
        """Obtener todos los pagos."""
        headers = self.get_headers()
        self.client.get(
            "/payment-service/api/payments",
            headers=headers,
            name="Get All Payments",
            catch_response=True
        )
    
    @task(4)
    def get_payment_by_id(self):
        """Obtener pago por ID."""
        if not self.created_resources["payment_ids"]:
            return
        
        payment_id = random.choice(self.created_resources["payment_ids"])
        headers = self.get_headers()
        self.client.get(
            f"/payment-service/api/payments/{payment_id}",
            headers=headers,
            name="Get Payment By ID",
            catch_response=True
        )
    
    @task(2)
    def update_payment_status(self):
        """Actualizar estado de pago."""
        if not self.created_resources["payment_ids"]:
            return
        
        payment_id = random.choice(self.created_resources["payment_ids"])
        headers = self.get_headers()
        
        self.client.patch(
            f"/payment-service/api/payments/{payment_id}",
            headers=headers,
            name="Update Payment Status",
            catch_response=True
        )

