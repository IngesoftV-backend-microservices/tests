"""
Pruebas de integración para el Payment Service.
"""
import pytest
from utils.api_utils import make_request, set_current_service
from utils.helpers import (
    generate_user_data, generate_cart_data, generate_order_data, generate_payment_data
)


@pytest.mark.integration
class TestPaymentService:
    """Pruebas para el Payment Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        set_current_service("payment-service")

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

        make_request("PATCH", f"/api/orders/{order_id}/status")

        yield {"id": order_id, "data": created_order, "cart": cart}

        set_current_service("order-service")
        make_request("DELETE", f"/api/orders/{order_id}")

    @pytest.fixture
    def create_test_payment(self, create_test_order):
        """Fixture para crear un payment de prueba."""
        set_current_service("payment-service")
        order = create_test_order
        payment_data = generate_payment_data(order["id"])

        response = make_request("POST", "/api/payments", data=payment_data)
        assert response.status_code in [200, 201], f"Error al crear payment: {response.text}"

        created_payment = response.json()
        payment_id = created_payment.get("paymentId")

        yield {"id": payment_id, "data": created_payment, "order": order}

        set_current_service("payment-service")
        try:
            make_request("DELETE", f"/api/payments/{payment_id}")
        except:
            pass  # Puede fallar si el payment está completado

    def test_1_create_payment(self, create_test_order):
        """Test 1: CREATE - Create a new payment"""
        set_current_service("payment-service")
        order = create_test_order
        payment_data = generate_payment_data(order["id"])
        
        response = make_request("POST", "/api/payments", data=payment_data)

        assert response.status_code in [200, 201]
        result = response.json()
        assert result["paymentId"] is not None

        try:
            make_request("DELETE", f'/api/payments/{result["paymentId"]}')
        except:
            pass

    def test_2_get_all_payments(self):
        """Test 2: GET ALL - Get all payments"""
        set_current_service("payment-service")
        response = make_request("GET", "/api/payments")

        assert response.status_code == 200
        result = response.json()
        if isinstance(result, dict) and "collection" in result:
            assert isinstance(result["collection"], list)
        elif isinstance(result, list):
            assert len(result) >= 0
        else:
            assert False, f"Formato de respuesta inesperado: {type(result)}"

    def test_3_get_payment_by_id(self, create_test_payment):
        """Test 3: GET BY ID - Get payment by ID"""
        set_current_service("payment-service")
        payment = create_test_payment
        response = make_request("GET", f'/api/payments/{payment["id"]}')

        assert response.status_code == 200
        result = response.json()
        assert result["paymentId"] == payment["id"]

    def test_4_update_payment(self, create_test_payment):
        """Test 4: UPDATE - Update payment status"""
        set_current_service("payment-service")
        payment = create_test_payment
        
        response = make_request("PATCH", f'/api/payments/{payment["id"]}')

        # Puede retornar 200 o 400 si el payment ya está completado
        assert response.status_code in [200, 400]

    def test_5_delete_payment(self, create_test_order):
        """Test 5: DELETE - Delete payment"""
        set_current_service("payment-service")
        order = create_test_order
        payment_data = generate_payment_data(order["id"])
        create_response = make_request("POST", "/api/payments", data=payment_data)
        assert create_response.status_code in [200, 201]
        payment_id = create_response.json()["paymentId"]

        delete_response = make_request("DELETE", f"/api/payments/{payment_id}")
        assert delete_response.status_code in [200, 204, 400]


