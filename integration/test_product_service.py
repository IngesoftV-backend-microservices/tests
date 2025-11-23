"""
Pruebas de integración para el Product Service.
"""
import pytest
from utils.api_utils import make_request, set_current_service
from utils.helpers import generate_category_data, generate_product_data


@pytest.mark.integration
class TestProductService:
    """Pruebas para el Product Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        set_current_service("product-service")

    @pytest.fixture
    def create_test_category(self):
        """Fixture para crear una categoría de prueba."""
        category_data = generate_category_data()
        response = make_request("POST", "/api/categories", data=category_data)
        assert response.status_code in [200, 201], f"Error al crear categoría: {response.text}"

        created_category = response.json()
        category_id = created_category.get("categoryId")

        yield {"id": category_id, "data": created_category}

        make_request("DELETE", f"/api/categories/{category_id}")

    @pytest.fixture
    def create_test_product(self, create_test_category):
        """Fixture para crear un producto de prueba."""
        category = create_test_category
        product_data = generate_product_data(category["id"])

        response = make_request("POST", "/api/products", data=product_data)
        assert response.status_code in [200, 201], f"Error al crear producto: {response.text}"

        created_product = response.json()
        product_id = created_product.get("productId")

        yield {"id": product_id, "data": created_product, "category": category}

        make_request("DELETE", f"/api/products/{product_id}")

    def test_1_create_product(self, create_test_category):
        """Test 1: CREATE - Create a new product"""
        category = create_test_category
        product_data = generate_product_data(category["id"])
        
        response = make_request("POST", "/api/products", data=product_data)

        assert response.status_code in [200, 201]
        result = response.json()
        assert result["productId"] is not None
        assert result["productTitle"] == product_data["productTitle"]

        make_request("DELETE", f'/api/products/{result["productId"]}')

    def test_2_get_all_products(self):
        """Test 2: GET ALL - Get all products"""
        response = make_request("GET", "/api/products")

        assert response.status_code == 200
        result = response.json()
        if isinstance(result, dict) and "collection" in result:
            assert isinstance(result["collection"], list)
        elif isinstance(result, list):
            assert len(result) >= 0
        else:
            assert False, f"Formato de respuesta inesperado: {type(result)}"

    def test_3_get_product_by_id(self, create_test_product):
        """Test 3: GET BY ID - Get product by ID"""
        product = create_test_product
        response = make_request("GET", f'/api/products/{product["id"]}')

        assert response.status_code == 200
        result = response.json()
        assert result["productId"] == product["id"]
        assert result["productTitle"] == product["data"]["productTitle"]

    def test_4_update_product(self, create_test_product):
        """Test 4: UPDATE - Update product"""
        product = create_test_product
        get_response = make_request("GET", f'/api/products/{product["id"]}')
        assert get_response.status_code == 200
        updated_data = get_response.json()
        
        updated_data["productTitle"] = "Updated Product Title"
        updated_data["priceUnit"] = 999.99
        updated_data["productId"] = product["id"]

        response = make_request("PUT", f'/api/products/{product["id"]}', data=updated_data)

        assert response.status_code == 200
        result = response.json()
        assert result["productTitle"] == "Updated Product Title"
        assert result["priceUnit"] == 999.99

    def test_5_delete_product(self, create_test_category):
        """Test 5: DELETE - Delete product"""
        category = create_test_category
        product_data = generate_product_data(category["id"])
        create_response = make_request("POST", "/api/products", data=product_data)
        assert create_response.status_code in [200, 201]
        product_id = create_response.json()["productId"]

        delete_response = make_request("DELETE", f"/api/products/{product_id}")
        assert delete_response.status_code in [200, 204]


