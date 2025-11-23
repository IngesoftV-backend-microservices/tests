"""
Pruebas E2E para el Favourite Service a través del API Gateway.
"""
import pytest
from urllib.parse import quote
from utils.api_utils import make_e2e_request
from utils.helpers import generate_user_data, generate_category_data, generate_product_data, generate_favourite_data


@pytest.mark.e2e
class TestE2EFavouriteService:
    """Pruebas E2E para el Favourite Service - 5 tests"""

    def test_e2e_complete_favourite_workflow(self, jwt_token):
        """E2E Test 1: Flujo completo de favoritos"""
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
            favourite_data = generate_favourite_data(user_id, product_id)
            favourite_response = make_e2e_request("POST", "/api/favourites", data=favourite_data, service_name="favourite", jwt_token=jwt_token)
            assert favourite_response.status_code in [200, 201]
            favourite = favourite_response.json()
            like_date = favourite.get("likeDate")
            
            assert favourite["userId"] == user_id
            assert favourite["productId"] == product_id
            assert like_date is not None
        finally:
            if 'like_date' in locals() and like_date:
                encoded_like_date = quote(like_date, safe="")
                make_e2e_request("DELETE", f"/api/favourites/{user_id}/{product_id}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            if 'category_id' in locals():
                make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_favourite_list_and_browse(self, jwt_token):
        """E2E Test 2: Listado y navegación de favoritos"""
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
        
        created_favourites = []
        
        try:
            for _ in range(3):
                product_data = generate_product_data(category_id)
                product_response = make_e2e_request("POST", "/api/products", data=product_data, service_name="product", jwt_token=jwt_token)
                assert product_response.status_code in [200, 201]
                product_id = product_response.json()["productId"]
                
                favourite_data = generate_favourite_data(user_id, product_id)
                favourite_response = make_e2e_request("POST", "/api/favourites", data=favourite_data, service_name="favourite", jwt_token=jwt_token)
                assert favourite_response.status_code in [200, 201]
                favourite = favourite_response.json()
                created_favourites.append({
                    "userId": user_id,
                    "productId": product_id,
                    "likeDate": favourite.get("likeDate")
                })
            
            all_favourites_response = make_e2e_request("GET", "/api/favourites", service_name="favourite", jwt_token=jwt_token)
            assert all_favourites_response.status_code == 200
            favourites_data = all_favourites_response.json()
            favourites_list = favourites_data.get("collection", []) if isinstance(favourites_data, dict) else favourites_data
            
            for created_fav in created_favourites:
                found = any(
                    fav.get("userId") == created_fav["userId"] and fav.get("productId") == created_fav["productId"]
                    for fav in favourites_list
                )
                assert found, f"Favourite {created_fav} not found in list"
        finally:
            for fav in created_favourites:
                if fav.get("likeDate"):
                    encoded_like_date = quote(fav["likeDate"], safe="")
                    make_e2e_request("DELETE", f"/api/favourites/{fav['userId']}/{fav['productId']}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_favourite_retrieval_by_composite_key(self, jwt_token):
        """E2E Test 3: Recuperación de favorito por clave compuesta"""
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
            favourite_data = generate_favourite_data(user_id, product_id)
            favourite_response = make_e2e_request("POST", "/api/favourites", data=favourite_data, service_name="favourite", jwt_token=jwt_token)
            assert favourite_response.status_code in [200, 201]
            like_date = favourite_response.json().get("likeDate")
            assert like_date is not None
            
            encoded_like_date = quote(like_date, safe="")
            get_response = make_e2e_request("GET", f"/api/favourites/{user_id}/{product_id}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
            assert get_response.status_code == 200
            retrieved_favourite = get_response.json()
            assert retrieved_favourite["userId"] == user_id
            assert retrieved_favourite["productId"] == product_id
        finally:
            if 'like_date' in locals() and like_date:
                encoded_like_date = quote(like_date, safe="")
                make_e2e_request("DELETE", f"/api/favourites/{user_id}/{product_id}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            if 'category_id' in locals():
                make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_favourite_update_workflow(self, jwt_token):
        """E2E Test 4: Flujo completo de actualización de favorito"""
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
            favourite_data = generate_favourite_data(user_id, product_id)
            favourite_response = make_e2e_request("POST", "/api/favourites", data=favourite_data, service_name="favourite", jwt_token=jwt_token)
            assert favourite_response.status_code in [200, 201]
            like_date = favourite_response.json().get("likeDate")
            assert like_date is not None
            
            encoded_like_date = quote(like_date, safe="")
            get_response = make_e2e_request("GET", f"/api/favourites/{user_id}/{product_id}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
            assert get_response.status_code == 200
            full_favourite = get_response.json()
            
            update_response = make_e2e_request("PUT", "/api/favourites", data=full_favourite, service_name="favourite", jwt_token=jwt_token)
            assert update_response.status_code == 200
        finally:
            if 'like_date' in locals() and like_date:
                encoded_like_date = quote(like_date, safe="")
                make_e2e_request("DELETE", f"/api/favourites/{user_id}/{product_id}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            if 'category_id' in locals():
                make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)

    def test_e2e_favourite_lifecycle_complete(self, jwt_token):
        """E2E Test 5: Ciclo de vida completo de favorito"""
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
            favourite_data = generate_favourite_data(user_id, product_id)
            favourite_response = make_e2e_request("POST", "/api/favourites", data=favourite_data, service_name="favourite", jwt_token=jwt_token)
            assert favourite_response.status_code in [200, 201]
            like_date = favourite_response.json().get("likeDate")
            assert like_date is not None
            
            encoded_like_date = quote(like_date, safe="")
            get_response = make_e2e_request("GET", f"/api/favourites/{user_id}/{product_id}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
            assert get_response.status_code == 200
            retrieved_favourite = get_response.json()
            assert retrieved_favourite["userId"] == user_id
            assert retrieved_favourite["productId"] == product_id
            
            update_response = make_e2e_request("PUT", "/api/favourites", data=retrieved_favourite, service_name="favourite", jwt_token=jwt_token)
            assert update_response.status_code == 200
            
            delete_response = make_e2e_request("DELETE", f"/api/favourites/{user_id}/{product_id}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
            assert delete_response.status_code in [200, 204]
        finally:
            if 'like_date' in locals() and like_date:
                try:
                    encoded_like_date = quote(like_date, safe="")
                    make_e2e_request("DELETE", f"/api/favourites/{user_id}/{product_id}/{encoded_like_date}", service_name="favourite", jwt_token=jwt_token)
                except:
                    pass
            if 'product_id' in locals():
                make_e2e_request("DELETE", f"/api/products/{product_id}", service_name="product", jwt_token=jwt_token)
            if 'category_id' in locals():
                make_e2e_request("DELETE", f"/api/categories/{category_id}", service_name="product", jwt_token=jwt_token)
            make_e2e_request("DELETE", f"/api/users/{user_id}", service_name="user", jwt_token=jwt_token)
