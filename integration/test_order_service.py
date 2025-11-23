"""
Pruebas de integración para el Order Service.
"""
import pytest
from utils.api_utils import make_request, set_current_service
from utils.helpers import generate_user_data, generate_cart_data, generate_order_data


@pytest.mark.integration
class TestOrderService:
    """Pruebas para el Order Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        set_current_service("order-service")

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
    def create_test_cart(self, create_test_user):
        """Fixture para crear un carrito de prueba."""
        set_current_service("order-service")
        user = create_test_user
        cart_data = generate_cart_data(user["id"])
        
        response = make_request("POST", "/api/carts", data=cart_data)
        assert response.status_code in [200, 201], f"Error al crear carrito: {response.text}"

        created_cart = response.json()
        cart_id = created_cart.get("cartId")

        yield {"id": cart_id, "data": created_cart, "user": user}

        set_current_service("order-service")
        make_request("DELETE", f"/api/carts/{cart_id}")

    @pytest.fixture
    def create_test_order(self, create_test_cart):
        """Fixture para crear una orden de prueba."""
        set_current_service("order-service")
        cart = create_test_cart
        order_data = generate_order_data(cart["id"])

        response = make_request("POST", "/api/orders", data=order_data)
        assert response.status_code in [200, 201], f"Error al crear orden: {response.text}"

        created_order = response.json()
        order_id = created_order.get("orderId")

        yield {"id": order_id, "data": created_order, "cart": cart}

        set_current_service("order-service")
        make_request("DELETE", f"/api/orders/{order_id}")

    def test_1_create_order(self, create_test_cart):
        """Test 1: CREATE - Create a new order"""
        set_current_service("order-service")
        cart = create_test_cart
        order_data = generate_order_data(cart["id"])
        
        response = make_request("POST", "/api/orders", data=order_data)

        assert response.status_code in [200, 201]
        result = response.json()
        assert result["orderId"] is not None
        assert result["orderDesc"] == order_data["orderDesc"]

        make_request("DELETE", f'/api/orders/{result["orderId"]}')

    def test_2_get_all_orders(self):
        """Test 2: GET ALL - Get all orders"""
        set_current_service("order-service")
        response = make_request("GET", "/api/orders")

        assert response.status_code == 200
        result = response.json()
        if isinstance(result, dict) and "collection" in result:
            assert isinstance(result["collection"], list)
        elif isinstance(result, list):
            assert len(result) >= 0
        else:
            assert False, f"Formato de respuesta inesperado: {type(result)}"

    def test_3_get_order_by_id(self, create_test_order):
        """Test 3: GET BY ID - Get order by ID"""
        set_current_service("order-service")
        order = create_test_order
        response = make_request("GET", f'/api/orders/{order["id"]}')

        assert response.status_code == 200
        result = response.json()
        assert result["orderId"] == order["id"]
        assert result["orderDesc"] == order["data"]["orderDesc"]

    def test_4_update_order(self, create_test_order):
        """Test 4: UPDATE - Update order"""
        set_current_service("order-service")
        order = create_test_order
        updated_data = order["data"].copy()
        updated_data["orderDesc"] = "Updated Order Description"
        updated_data["orderFee"] = 999.99

        response = make_request("PUT", f'/api/orders/{order["id"]}', data=updated_data)

        assert response.status_code == 200
        result = response.json()
        assert result["orderDesc"] == "Updated Order Description"
        assert result["orderFee"] == 999.99

    def test_5_delete_order(self, create_test_cart):
        """Test 5: DELETE - Delete order"""
        set_current_service("order-service")
        cart = create_test_cart
        order_data = generate_order_data(cart["id"])
        create_response = make_request("POST", "/api/orders", data=order_data)
        assert create_response.status_code in [200, 201]
        order_id = create_response.json()["orderId"]

        delete_response = make_request("DELETE", f"/api/orders/{order_id}")
        assert delete_response.status_code in [200, 204]

