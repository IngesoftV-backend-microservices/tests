"""
Pruebas E2E para el Order Service a través del API Gateway.
"""
import pytest
from utils.api_utils import make_e2e_request
from utils.helpers import generate_user_data, generate_cart_data, generate_order_data


@pytest.mark.e2e
class TestE2EOrderService:
    """Pruebas E2E para el Order Service - 5 tests"""

    def test_e2e_complete_cart_lifecycle(self, jwt_token):
        """E2E Test 1: Ciclo de vida completo de un carrito"""
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
            
            get_cart_response = make_e2e_request("GET", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            if get_cart_response.status_code == 200:
                retrieved_cart = get_cart_response.json()
                assert retrieved_cart["cartId"] == cart_id
                assert retrieved_cart.get("userId") == user_id
            
            all_carts_response = make_e2e_request("GET", "/api/carts", service_name="order", jwt_token=jwt_token)
            assert all_carts_response.status_code == 200
            carts_data = all_carts_response.json()
            carts_list = carts_data.get("collection", []) if isinstance(carts_data, dict) else carts_data
            cart_ids = [c.get("cartId") for c in carts_list if isinstance(c, dict)]
            assert isinstance(cart_ids, list)
            
            if cart_id in cart_ids:
                cart_in_list = next((c for c in carts_list if c.get("cartId") == cart_id), None)
                if cart_in_list:
                    assert cart_in_list.get("userId") == user_id
            
            delete_response = make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            assert delete_response.status_code in [200, 204]
        finally:
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_order_from_cart_workflow(self, jwt_token):
        """E2E Test 2: Flujo completo de orden desde carrito"""
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
            order = order_response.json()
            order_id = order["orderId"]
            
            get_order_response = make_e2e_request("GET", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            assert get_order_response.status_code == 200
            retrieved_order = get_order_response.json()
            assert retrieved_order["orderId"] == order_id
            assert retrieved_order["orderDesc"] == order_data["orderDesc"]
            
            updated_order = order.copy()
            updated_order["orderDesc"] = "Updated Order Description"
            updated_order["orderFee"] = 149.99
            update_order_response = make_e2e_request("PUT", f"/api/orders/{order_id}", data=updated_order, service_name="order", jwt_token=jwt_token)
            assert update_order_response.status_code == 200
            final_order = update_order_response.json()
            assert final_order["orderDesc"] == "Updated Order Description"
            assert final_order["orderFee"] == 149.99
        finally:
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_multiple_orders_management(self, jwt_token):
        """E2E Test 3: Gestión de múltiples órdenes"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        created_carts = []
        created_orders = []
        
        try:
            for _ in range(3):
                cart_data = generate_cart_data(user_id)
                cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
                assert cart_response.status_code in [200, 201]
                created_carts.append(cart_response.json())
            
            for cart in created_carts:
                order_data = generate_order_data(cart["cartId"])
                order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
                assert order_response.status_code in [200, 201]
                created_orders.append(order_response.json())
            
            all_orders_response = make_e2e_request("GET", "/api/orders", service_name="order", jwt_token=jwt_token)
            assert all_orders_response.status_code == 200
            orders_data = all_orders_response.json()
            orders_list = orders_data.get("collection", []) if isinstance(orders_data, dict) else orders_data
            all_order_ids = [o.get("orderId") for o in orders_list if isinstance(o, dict)]
            
            for created_order in created_orders:
                assert created_order["orderId"] in all_order_ids
                specific_order_response = make_e2e_request("GET", f"/api/orders/{created_order['orderId']}", service_name="order", jwt_token=jwt_token)
                assert specific_order_response.status_code == 200
                assert specific_order_response.json()["orderId"] == created_order["orderId"]
        finally:
            for order in created_orders:
                make_e2e_request("DELETE", f"/api/orders/{order['orderId']}", service_name="order", jwt_token=jwt_token)
            for cart in created_carts:
                make_e2e_request("DELETE", f"/api/carts/{cart['cartId']}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_order_fee_calculations(self, jwt_token):
        """E2E Test 4: Cálculos y gestión de tarifas de órdenes"""
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
            order_data["orderFee"] = 100.00
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order = order_response.json()
            order_id = order["orderId"]
            assert order["orderFee"] == 100.00
            
            updated_order = order.copy()
            updated_order["orderFee"] = 150.00
            update_response = make_e2e_request("PUT", f"/api/orders/{order_id}", data=updated_order, service_name="order", jwt_token=jwt_token)
            assert update_response.status_code == 200
            assert update_response.json()["orderFee"] == 150.00
            
            discount_order = updated_order.copy()
            discount_order["orderFee"] = 120.00
            discount_response = make_e2e_request("PUT", f"/api/orders/{order_id}", data=discount_order, service_name="order", jwt_token=jwt_token)
            assert discount_response.status_code == 200
            assert discount_response.json()["orderFee"] == 120.00
            
            final_order = discount_order.copy()
            final_order["orderFee"] = 135.00
            final_response = make_e2e_request("PUT", f"/api/orders/{order_id}", data=final_order, service_name="order", jwt_token=jwt_token)
            assert final_response.status_code == 200
            assert final_response.json()["orderFee"] == 135.00
        finally:
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_cart_and_order_bulk_operations(self, jwt_token):
        """E2E Test 5: Operaciones en lote con carritos y órdenes"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        created_carts = []
        created_orders = []
        
        try:
            for _ in range(3):
                cart_data = generate_cart_data(user_id)
                cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
                assert cart_response.status_code in [200, 201]
                created_carts.append(cart_response.json())
            
            order_fees = [299.99, 149.99, 199.99]
            for i, cart in enumerate(created_carts):
                order_data = generate_order_data(cart["cartId"])
                order_data["orderFee"] = order_fees[i]
                order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
                assert order_response.status_code in [200, 201]
                created_orders.append(order_response.json())
            
            for i in range(1, 2):
                order = created_orders[i]
                update_data = order.copy()
                update_data["orderFee"] = order["orderFee"] + 50.00
                update_response = make_e2e_request("PUT", f"/api/orders/{order['orderId']}", data=update_data, service_name="order", jwt_token=jwt_token)
                assert update_response.status_code == 200
            
            all_orders_response = make_e2e_request("GET", "/api/orders", service_name="order", jwt_token=jwt_token)
            assert all_orders_response.status_code == 200
            orders_data = all_orders_response.json()
            orders_list = orders_data.get("collection", []) if isinstance(orders_data, dict) else orders_data
            order_ids_in_response = [o.get("orderId") for o in orders_list if isinstance(o, dict)]
            
            for created_order in created_orders:
                assert created_order["orderId"] in order_ids_in_response
                check_response = make_e2e_request("GET", f"/api/orders/{created_order['orderId']}", service_name="order", jwt_token=jwt_token)
                assert check_response.status_code == 200
                assert check_response.json()["orderId"] == created_order["orderId"]
        finally:
            for order in created_orders:
                make_e2e_request("DELETE", f"/api/orders/{order['orderId']}", service_name="order", jwt_token=jwt_token)
            for cart in created_carts:
                make_e2e_request("DELETE", f"/api/carts/{cart['cartId']}", service_name="order", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
