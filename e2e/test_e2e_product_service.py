"""
Pruebas E2E para el Product Service a través del API Gateway.
"""
import pytest
from utils.api_utils import make_e2e_request
from utils.helpers import generate_category_data, generate_product_data


@pytest.mark.e2e
class TestE2EProductService:
    """Pruebas E2E para el Product Service - 5 tests"""

    def test_e2e_category_and_product_workflow(self, jwt_token):
        """E2E Test 1: Flujo completo de categoría y producto"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        try:
            product_data = generate_product_data(category_id)
            product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
            assert product_response.status_code in [200, 201]
            product_id = product_response.json()["productId"]
            
            get_product_response = make_e2e_request("GET", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            assert get_product_response.status_code == 200
            assert get_product_response.json()["category"]["categoryId"] == category_id
        finally:
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)

    def test_e2e_product_catalog_browse(self, jwt_token):
        """E2E Test 2: Navegación completa del catálogo de productos"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        created_products = []
        try:
            for _ in range(3):
                product_data = generate_product_data(category_id)
                product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
                assert product_response.status_code in [200, 201]
                created_products.append(product_response.json())
            
            all_products_response = make_e2e_request("GET", "/api/products", service_name="product", jwt_token=jwt_token)
            assert all_products_response.status_code == 200
            products_data = all_products_response.json()
            products_list = products_data.get("collection", []) if isinstance(products_data, dict) else products_data
            product_ids = [p.get("productId") for p in products_list if isinstance(p, dict)]
            
            for created_product in created_products:
                assert created_product["productId"] in product_ids
        finally:
            for product in created_products:
                make_e2e_request("DELETE", f"/api/products/{product['productId']}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)

    def test_e2e_product_update_workflow(self, jwt_token):
        """E2E Test 3: Flujo completo de actualización de producto"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        try:
            product_data = generate_product_data(category_id)
            product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
            assert product_response.status_code in [200, 201]
            product_id = product_response.json()["productId"]
            
            get_response = make_e2e_request("GET", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            assert get_response.status_code == 200
            full_product = get_response.json()
            
            full_product["productTitle"] = "Updated Product Title"
            full_product["priceUnit"] = 199.99
            full_product["quantity"] = 50
            
            update_response = make_e2e_request("PUT", f"/api/products/{product_id}", data=full_product, service_name="product", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            verify_response = make_e2e_request("GET", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            updated_product = verify_response.json()
            assert updated_product["productTitle"] == "Updated Product Title"
            assert updated_product["priceUnit"] == 199.99
            assert updated_product["quantity"] == 50
        finally:
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)

    def test_e2e_category_management_workflow(self, jwt_token):
        """E2E Test 4: Flujo completo de gestión de categorías"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        try:
            get_category_response = make_e2e_request("GET", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            assert get_category_response.status_code == 200
            assert get_category_response.json()["categoryId"] == category_id
            
            updated_category = category_response.json().copy()
            updated_category["categoryTitle"] = "Updated Category Title"
            update_response = make_e2e_request("PUT", "/api/categories", data=updated_category, service_name="product", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            all_categories_response = make_e2e_request("GET", "/api/categories", service_name="product", jwt_token=jwt_token)
            assert all_categories_response.status_code == 200
            categories_data = all_categories_response.json()
            categories_list = categories_data.get("collection", []) if isinstance(categories_data, dict) else categories_data
            category_ids = [c.get("categoryId") for c in categories_list if isinstance(c, dict)]
            assert category_id in category_ids
        finally:
            make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)

    def test_e2e_product_lifecycle_complete(self, jwt_token):
        """E2E Test 5: Ciclo de vida completo de producto"""
        if not jwt_token:
            pytest.skip("JWT token not available")
        
        category_data = generate_category_data()
        category_response = make_e2e_request("POST", "/api/categories", data=category_data, service_name="product", jwt_token=jwt_token)
        assert category_response.status_code in [200, 201]
        category_id = category_response.json()["categoryId"]
        
        try:
            product_data = generate_product_data(category_id)
            product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
            assert product_response.status_code in [200, 201]
            product_id = product_response.json()["productId"]
            
            get_response = make_e2e_request("GET", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            assert get_response.status_code == 200
            assert get_response.json()["productId"] == product_id
            
            get_full_response = make_e2e_request("GET", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            full_product = get_full_response.json()
            full_product["productTitle"] = "LifecycleTest Product"
            update_response = make_e2e_request("PUT", f"/api/products/{product_id}", data=full_product, service_name="product", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            verify_response = make_e2e_request("GET", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            assert verify_response.json()["productTitle"] == "LifecycleTest Product"
            
            delete_response = make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            assert delete_response.status_code in [200, 204]
            
            get_after_delete = make_e2e_request("GET", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            assert get_after_delete.status_code in [404, 400]
        finally:
            if 'product_id' in locals():
                try:
                    make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
                except:
                    pass
            make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
