"""
Pruebas de integración para el Favourite Service.
"""
import pytest
from urllib.parse import quote
from utils.api_utils import make_request, set_current_service
from utils.helpers import (
    generate_user_data, generate_category_data, generate_product_data, generate_favourite_data
)


@pytest.mark.integration
class TestFavouriteService:
    """Pruebas para el Favourite Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        set_current_service("favourite-service")

    @pytest.fixture
    def create_test_user(self):
        """Fixture para crear un usuario de prueba."""
        set_current_service("user-service")
        user_data = generate_user_data()
        response = make_request("POST", "/api/users", data=user_data)
        assert response.status_code in [200, 201], f"Error al crear usuario: {response.text}"

        created_user = response.json()
        user_id = created_user.get("userId")

        yield {"id": user_id, "data": created_user}

        set_current_service("user-service")
        make_request("DELETE", f"/api/users/{user_id}")

    @pytest.fixture
    def create_test_category(self):
        """Fixture para crear una categoría de prueba."""
        set_current_service("product-service")
        category_data = generate_category_data()
        response = make_request("POST", "/api/categories", data=category_data)
        assert response.status_code in [200, 201], f"Error al crear categoría: {response.text}"

        created_category = response.json()
        category_id = created_category.get("categoryId")

        yield {"id": category_id, "data": created_category}

        set_current_service("product-service")
        make_request("DELETE", f"/api/categories/{category_id}")

    @pytest.fixture
    def create_test_product(self, create_test_category):
        """Fixture para crear un producto de prueba."""
        set_current_service("product-service")
        category = create_test_category
        product_data = generate_product_data(category["id"])

        response = make_request("POST", "/api/products", data=product_data)
        assert response.status_code in [200, 201], f"Error al crear producto: {response.text}"

        created_product = response.json()
        product_id = created_product.get("productId")

        yield {"id": product_id, "data": created_product, "category": category}

        set_current_service("product-service")
        make_request("DELETE", f"/api/products/{product_id}")

    @pytest.fixture
    def create_test_favourite(self, create_test_user, create_test_product):
        """Fixture para crear un favourite de prueba."""
        set_current_service("favourite-service")
        user = create_test_user
        product = create_test_product
        favourite_data = generate_favourite_data(user["id"], product["id"])

        response = make_request("POST", "/api/favourites", data=favourite_data)
        assert response.status_code in [200, 201], f"Error al crear favourite: {response.text}"

        created_favourite = response.json()
        like_date = created_favourite.get("likeDate")
        yield {
            "user_id": user["id"],
            "product_id": product["id"],
            "like_date": like_date,
            "data": created_favourite,
            "user": user,
            "product": product
        }

        if like_date:
            set_current_service("favourite-service")
            try:
                like_date_encoded = quote(str(like_date), safe="")
                make_request("DELETE", f"/api/favourites/{user['id']}/{product['id']}/{like_date_encoded}")
            except:
                pass

    def test_1_create_favourite(self, create_test_user, create_test_product):
        """Test 1: CREATE - Create a new favourite"""
        set_current_service("favourite-service")
        user = create_test_user
        product = create_test_product
        favourite_data = generate_favourite_data(user["id"], product["id"])
        
        response = make_request("POST", "/api/favourites", data=favourite_data)

        assert response.status_code in [200, 201]
        result = response.json()
        assert result is not None

        like_date = result.get("likeDate")
        if like_date:
            set_current_service("favourite-service")
            try:
                like_date_encoded = quote(str(like_date), safe="")
                make_request("DELETE", f"/api/favourites/{user['id']}/{product['id']}/{like_date_encoded}")
            except:
                pass

    def test_2_get_all_favourites(self):
        """Test 2: GET ALL - Get all favourites"""
        set_current_service("favourite-service")
        response = make_request("GET", "/api/favourites")

        assert response.status_code == 200
        result = response.json()
        if isinstance(result, dict) and "collection" in result:
            assert isinstance(result["collection"], list)
        elif isinstance(result, list):
            assert len(result) >= 0
        else:
            assert False, f"Formato de respuesta inesperado: {type(result)}"

    def test_3_get_favourite_by_id(self, create_test_favourite):
        """Test 3: GET BY ID - Get favourite by user and product"""
        set_current_service("favourite-service")
        favourite = create_test_favourite
        
        if not favourite.get("like_date"):
            pytest.skip("No likeDate available")
        
        like_date = favourite["like_date"]
        like_date_encoded = quote(str(like_date), safe="")
        response = make_request("GET", f'/api/favourites/{favourite["user_id"]}/{favourite["product_id"]}/{like_date_encoded}')

        assert response.status_code == 200
        result = response.json()
        assert result["userId"] == favourite["user_id"]
        assert result["productId"] == favourite["product_id"]

    def test_4_update_favourite(self, create_test_favourite):
        """Test 4: UPDATE - Update favourite"""
        set_current_service("favourite-service")
        favourite = create_test_favourite
        
        if not favourite.get("like_date"):
            pytest.skip("No likeDate available")
        
        like_date = favourite["like_date"]
        like_date_encoded = quote(str(like_date), safe="")
        get_response = make_request("GET", f'/api/favourites/{favourite["user_id"]}/{favourite["product_id"]}/{like_date_encoded}')
        if get_response.status_code != 200:
            pytest.skip("Cannot get favourite for update")
        
        updated_data = get_response.json()
        response = make_request("PUT", "/api/favourites", data=updated_data)

        assert response.status_code == 200

    def test_5_delete_favourite(self, create_test_user, create_test_product):
        """Test 5: DELETE - Delete favourite"""
        set_current_service("favourite-service")
        user = create_test_user
        product = create_test_product
        favourite_data = generate_favourite_data(user["id"], product["id"])
        create_response = make_request("POST", "/api/favourites", data=favourite_data)
        assert create_response.status_code in [200, 201]
        
        created_favourite = create_response.json()
        like_date = created_favourite.get("likeDate")
        if not like_date:
            pytest.skip("No likeDate in created favourite")

        like_date_encoded = quote(str(like_date), safe="")
        delete_response = make_request("DELETE", f"/api/favourites/{user['id']}/{product['id']}/{like_date_encoded}")
        assert delete_response.status_code in [200, 204]


