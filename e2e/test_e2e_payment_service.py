"""
Pruebas E2E para el Payment Service a través del API Gateway.
"""
import pytest
from utils.api_utils import make_e2e_request
from utils.helpers import generate_user_data, generate_cart_data, generate_order_data, generate_payment_data


@pytest.mark.e2e
class TestE2EPaymentService:
    """Pruebas E2E para el Payment Service - 5 tests"""

    def test_e2e_complete_payment_workflow(self, jwt_token):
        """E2E Test 1: Flujo completo de pago"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        try:
            cart_data = generate_cart_data(user_id)
            cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
            assert cart_response.status_code in [200, 201]
            cart_id = cart_response.json()["cartId"]
            
            order_data = generate_order_data(cart_id)
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order_id = order_response.json()["orderId"]
            
            make_e2e_request("PATCH", f"/api/orders/{order_id}/status", service_name="order", jwt_token=jwt_token)
            
            payment_data = generate_payment_data(order_id)
            payment_response = make_e2e_request("POST", "/api/payments", data=payment_data, service_name="payment", jwt_token=jwt_token)
            assert payment_response.status_code in [200, 201]
            payment_id = payment_response.json()["paymentId"]
            
            get_payment_response = make_e2e_request("GET", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
            assert get_payment_response.status_code == 200
            assert get_payment_response.json()["order"]["orderId"] == order_id
        finally:
            if 'payment_id' in locals():
                make_e2e_request("DELETE", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_payment_status_flow(self, jwt_token):
        """E2E Test 2: Flujo completo de estados de pago"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        try:
            cart_data = generate_cart_data(user_id)
            cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
            assert cart_response.status_code in [200, 201]
            cart_id = cart_response.json()["cartId"]
            
            order_data = generate_order_data(cart_id)
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order_id = order_response.json()["orderId"]
            
            make_e2e_request("PATCH", f"/api/orders/{order_id}/status", service_name="order", jwt_token=jwt_token)
            
            payment_data = generate_payment_data(order_id)
            payment_response = make_e2e_request("POST", "/api/payments", data=payment_data, service_name="payment", jwt_token=jwt_token)
            assert payment_response.status_code in [200, 201]
            payment_id = payment_response.json()["paymentId"]
            
            get_payment_response = make_e2e_request("GET", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
            assert get_payment_response.status_code == 200
            initial_payment = get_payment_response.json()
            assert initial_payment["isPayed"] == False
            assert initial_payment["paymentStatus"] == "NOT_STARTED"
            
            if not initial_payment.get("isPayed"):
                update_response = make_e2e_request("PATCH", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
                assert update_response.status_code in [200, 400]
        finally:
            if 'payment_id' in locals():
                make_e2e_request("DELETE", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_multiple_payments_management(self, jwt_token):
        """E2E Test 3: Gestión de múltiples pagos"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        created_orders = []
        created_payments = []
        
        try:
            for _ in range(3):
                cart_data = generate_cart_data(user_id)
                cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
                assert cart_response.status_code in [200, 201]
                cart_id = cart_response.json()["cartId"]
                
                order_data = generate_order_data(cart_id)
                order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
                assert order_response.status_code in [200, 201]
                order_id = order_response.json()["orderId"]
                
                make_e2e_request("PATCH", f"/api/orders/{order_id}/status", service_name="order", jwt_token=jwt_token)
                created_orders.append({"orderId": order_id, "cartId": cart_id})
            
            for order_info in created_orders:
                payment_data = generate_payment_data(order_info["orderId"])
                payment_response = make_e2e_request("POST", "/api/payments", data=payment_data, service_name="payment", jwt_token=jwt_token)
                assert payment_response.status_code in [200, 201]
                created_payments.append(payment_response.json())
            
            all_payments_response = make_e2e_request("GET", "/api/payments", service_name="payment", jwt_token=jwt_token)
            assert all_payments_response.status_code == 200
            payments_data = all_payments_response.json()
            payments_list = payments_data.get("collection", []) if isinstance(payments_data, dict) else payments_data
            all_payment_ids = [p.get("paymentId") for p in payments_list if isinstance(p, dict)]
            
            for created_payment in created_payments:
                assert created_payment["paymentId"] in all_payment_ids
                get_payment_response = make_e2e_request("GET", f"/api/payments/{created_payment['paymentId']}", service_name="payment", jwt_token=jwt_token)
                assert get_payment_response.status_code == 200
                assert get_payment_response.json()["paymentId"] == created_payment["paymentId"]
        finally:
            for payment in created_payments:
                make_e2e_request("DELETE", f"/api/payments/{payment['paymentId']}", service_name="payment", jwt_token=jwt_token)
            for order_info in created_orders:
                make_e2e_request("DELETE", f"/api/orders/{order_info['orderId']}", service_name="order", jwt_token=jwt_token)
                make_e2e_request("DELETE", f"/api/carts/{order_info['cartId']}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_payment_retrieval_and_verification(self, jwt_token):
        """E2E Test 4: Recuperación y verificación completa de pago"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        try:
            cart_data = generate_cart_data(user_id)
            cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
            assert cart_response.status_code in [200, 201]
            cart_id = cart_response.json()["cartId"]
            
            order_data = generate_order_data(cart_id)
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order_id = order_response.json()["orderId"]
            
            make_e2e_request("PATCH", f"/api/orders/{order_id}/status", service_name="order", jwt_token=jwt_token)
            
            payment_data = generate_payment_data(order_id)
            payment_response = make_e2e_request("POST", "/api/payments", data=payment_data, service_name="payment", jwt_token=jwt_token)
            assert payment_response.status_code in [200, 201]
            payment_id = payment_response.json()["paymentId"]
            
            get_payment_response = make_e2e_request("GET", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
            assert get_payment_response.status_code == 200
            retrieved_payment = get_payment_response.json()
            
            assert retrieved_payment["paymentId"] == payment_id
            assert "order" in retrieved_payment
            assert retrieved_payment["order"]["orderId"] == order_id
            assert "isPayed" in retrieved_payment
            assert "paymentStatus" in retrieved_payment
        finally:
            if 'payment_id' in locals():
                make_e2e_request("DELETE", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_payment_lifecycle_complete(self, jwt_token):
        """E2E Test 5: Ciclo de vida completo de pago"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        try:
            cart_data = generate_cart_data(user_id)
            cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
            assert cart_response.status_code in [200, 201]
            cart_id = cart_response.json()["cartId"]
            
            order_data = generate_order_data(cart_id)
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order_id = order_response.json()["orderId"]
            
            make_e2e_request("PATCH", f"/api/orders/{order_id}/status", service_name="order", jwt_token=jwt_token)
            
            payment_data = generate_payment_data(order_id)
            payment_response = make_e2e_request("POST", "/api/payments", data=payment_data, service_name="payment", jwt_token=jwt_token)
            assert payment_response.status_code in [200, 201]
            payment_id = payment_response.json()["paymentId"]
            
            get_payment_response = make_e2e_request("GET", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
            assert get_payment_response.status_code == 200
            retrieved_payment = get_payment_response.json()
            assert retrieved_payment["paymentId"] == payment_id
            
            if not retrieved_payment.get("isPayed") and retrieved_payment.get("paymentStatus") != "COMPLETED":
                delete_response = make_e2e_request("DELETE", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
                assert delete_response.status_code in [200, 204, 400]
        finally:
            if 'payment_id' in locals():
                try:
                    get_check = make_e2e_request("GET", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
                    if get_check.status_code == 200:
                        payment_check = get_check.json()
                        if not payment_check.get("isPayed") and payment_check.get("paymentStatus") != "COMPLETED":
                            make_e2e_request("DELETE", f"/api/payments/{payment_id}", service_name="payment", jwt_token=jwt_token)
                except:
                    pass
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
