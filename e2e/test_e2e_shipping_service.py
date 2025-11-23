"""
Pruebas E2E para el Shipping Service a través del API Gateway.
"""
import pytest
from utils.api_utils import make_e2e_request
from utils.helpers import (
    generate_user_data, generate_category_data, generate_product_data,
    generate_cart_data, generate_order_data, generate_shipping_data
)


@pytest.mark.e2e
class TestE2EShippingService:
    """Pruebas E2E para el Shipping Service - 5 tests"""

    def test_e2e_complete_shipping_workflow(self, jwt_token):
        """E2E Test 1: Flujo completo de shipping"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        product_data = generate_product_data(category_id)
        product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
        assert product_response.status_code in [200, 201]
        product_id = product_response.json()["productId"]
        
        try:
            cart_data = generate_cart_data(user_id)
            cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
            assert cart_response.status_code in [200, 201]
            cart_id = cart_response.json()["cartId"]
            
            order_data = generate_order_data(cart_id)
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order_id = order_response.json()["orderId"]
            
            shipping_data = generate_shipping_data(order_id, product_id)
            shipping_response = make_e2e_request("POST", "/api/shippings", data=shipping_data, service_name="shipping", jwt_token=jwt_token)
            assert shipping_response.status_code in [200, 201]
            
            get_shipping_response = make_e2e_request("GET", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            assert get_shipping_response.status_code == 200
            shipping = get_shipping_response.json()
            assert shipping["orderId"] == order_id
            assert shipping["productId"] == product_id
        finally:
            if 'order_id' in locals() and 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            if 'category_id' in locals():
                make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_shipping_list_and_retrieval(self, jwt_token):
        """E2E Test 2: Listado y recuperación de shippings"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        created_shippings = []
        
        try:
            for _ in range(3):
                product_data = generate_product_data(category_id)
                product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
                assert product_response.status_code in [200, 201]
                product_id = product_response.json()["productId"]
                
                cart_data = generate_cart_data(user_id)
                cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
                assert cart_response.status_code in [200, 201]
                cart_id = cart_response.json()["cartId"]
                
                order_data = generate_order_data(cart_id)
                order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
                assert order_response.status_code in [200, 201]
                order_id = order_response.json()["orderId"]
                
                shipping_data = generate_shipping_data(order_id, product_id)
                shipping_response = make_e2e_request("POST", "/api/shippings", data=shipping_data, service_name="shipping", jwt_token=jwt_token)
                assert shipping_response.status_code in [200, 201]
                shipping = shipping_response.json()
                created_shippings.append({
                    "orderId": shipping["orderId"],
                    "productId": shipping["productId"]
                })
            
            all_shippings_response = make_e2e_request("GET", "/api/shippings", service_name="shipping", jwt_token=jwt_token)
            assert all_shippings_response.status_code == 200
            shippings_data = all_shippings_response.json()
            shippings_list = shippings_data.get("collection", []) if isinstance(shippings_data, dict) else shippings_data
            
            for shipping_info in created_shippings:
                found = any(
                    s.get("orderId") == shipping_info["orderId"] and s.get("productId") == shipping_info["productId"]
                    for s in shippings_list
                )
                assert found, f"Shipping {shipping_info} not found in list"
        finally:
            for shipping_info in created_shippings:
                make_e2e_request("DELETE", f"/api/shippings/{shipping_info['orderId']}/{shipping_info['productId']}", service_name="shipping", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_shipping_update_workflow(self, jwt_token):
        """E2E Test 3: Flujo completo de actualización de shipping"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        product_data = generate_product_data(category_id)
        product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
        assert product_response.status_code in [200, 201]
        product_id = product_response.json()["productId"]
        
        try:
            cart_data = generate_cart_data(user_id)
            cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
            assert cart_response.status_code in [200, 201]
            cart_id = cart_response.json()["cartId"]
            
            order_data = generate_order_data(cart_id)
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order_id = order_response.json()["orderId"]
            
            shipping_data = generate_shipping_data(order_id, product_id)
            shipping_response = make_e2e_request("POST", "/api/shippings", data=shipping_data, service_name="shipping", jwt_token=jwt_token)
            assert shipping_response.status_code in [200, 201]
            
            get_response = make_e2e_request("GET", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            assert get_response.status_code == 200
            full_shipping = get_response.json()
            
            full_shipping["orderedQuantity"] = 5
            update_response = make_e2e_request("PUT", "/api/shippings", data=full_shipping, service_name="shipping", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            verify_response = make_e2e_request("GET", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            assert verify_response.json()["orderedQuantity"] == 5
        finally:
            if 'order_id' in locals() and 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            if 'category_id' in locals():
                make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_shipping_retrieval_by_composite_key(self, jwt_token):
        """E2E Test 4: Recuperación de shipping por clave compuesta"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        product_data = generate_product_data(category_id)
        product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
        assert product_response.status_code in [200, 201]
        product_id = product_response.json()["productId"]
        
        try:
            cart_data = generate_cart_data(user_id)
            cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
            assert cart_response.status_code in [200, 201]
            cart_id = cart_response.json()["cartId"]
            
            order_data = generate_order_data(cart_id)
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order_id = order_response.json()["orderId"]
            
            shipping_data = generate_shipping_data(order_id, product_id, quantity=3)
            shipping_response = make_e2e_request("POST", "/api/shippings", data=shipping_data, service_name="shipping", jwt_token=jwt_token)
            assert shipping_response.status_code in [200, 201]
            
            get_response = make_e2e_request("GET", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            assert get_response.status_code == 200
            retrieved_shipping = get_response.json()
            assert retrieved_shipping["orderId"] == order_id
            assert retrieved_shipping["productId"] == product_id
            assert retrieved_shipping["orderedQuantity"] == 3
        finally:
            if 'order_id' in locals() and 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            if 'category_id' in locals():
                make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_shipping_lifecycle_complete(self, jwt_token):
        """E2E Test 5: Ciclo de vida completo de shipping"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        user_data = generate_user_data()
        user_response = make_e2e_request("POST", "/api/users", data=user_data, service_name="user", jwt_token=jwt_token)
        assert user_response.status_code in [200, 201]
        user_id = user_response.json()["userId"]
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        product_data = generate_product_data(category_id)
        product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
        assert product_response.status_code in [200, 201]
        product_id = product_response.json()["productId"]
        
        try:
            cart_data = generate_cart_data(user_id)
            cart_response = make_e2e_request("POST", "/api/carts", data=cart_data, service_name="order", jwt_token=jwt_token)
            assert cart_response.status_code in [200, 201]
            cart_id = cart_response.json()["cartId"]
            
            order_data = generate_order_data(cart_id)
            order_response = make_e2e_request("POST", "/api/orders", data=order_data, service_name="order", jwt_token=jwt_token)
            assert order_response.status_code in [200, 201]
            order_id = order_response.json()["orderId"]
            
            shipping_data = generate_shipping_data(order_id, product_id)
            shipping_response = make_e2e_request("POST", "/api/shippings", data=shipping_data, service_name="shipping", jwt_token=jwt_token)
            assert shipping_response.status_code in [200, 201]
            
            get_response = make_e2e_request("GET", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            assert get_response.status_code == 200
            retrieved_shipping = get_response.json()
            assert retrieved_shipping["orderId"] == order_id
            assert retrieved_shipping["productId"] == product_id
            
            retrieved_shipping["orderedQuantity"] = 10
            update_response = make_e2e_request("PUT", "/api/shippings", data=retrieved_shipping, service_name="shipping", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            get_updated_response = make_e2e_request("GET", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            assert get_updated_response.json()["orderedQuantity"] == 10
            
            delete_response = make_e2e_request("DELETE", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            assert delete_response.status_code in [200, 204]
            
            get_after_delete = make_e2e_request("GET", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
            assert get_after_delete.status_code == 404
        finally:
            if 'order_id' in locals() and 'product_id' in locals():
                try:
                    make_e2e_request("DELETE", f"/api/shippings/{order_id}/{product_id}", service_name="shipping", jwt_token=jwt_token)
                except:
                    pass
            if 'order_id' in locals():
                make_e2e_request("DELETE", f"/api/orders/{order_id}", service_name="order", jwt_token=jwt_token)
            if 'cart_id' in locals():
                make_e2e_request("DELETE", f"/api/carts/{cart_id}", service_name="order", jwt_token=jwt_token)
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            if 'category_id' in locals():
                make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
