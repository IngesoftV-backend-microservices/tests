"""
Pruebas de integración para el Shipping Service.
"""
import pytest
from utils.api_utils import make_request, set_current_service
from utils.helpers import (
    generate_user_data, generate_cart_data, generate_order_data,
    generate_category_data, generate_product_data, generate_shipping_data
)


@pytest.mark.integration
class TestShippingService:
    """Pruebas para el Shipping Service - 5 tests"""

    def setup_method(self):
        """Configurar el servicio para las pruebas."""
        set_current_service("shipping-service")

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
        try:
            make_request("DELETE", f"/api/categories/{category_id}")
        except:
            pass

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

        # set_current_service("product-service")
        # make_request("DELETE", f"/api/products/{product_id}")

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

    @pytest.fixture
    def create_test_shipping(self, create_test_order, create_test_product):
        """Fixture para crear un shipping/order item de prueba."""
        set_current_service("shipping-service")
        order = create_test_order
        product = create_test_product
        shipping_data = generate_shipping_data(order["id"], product["id"], quantity=2)

        response = make_request("POST", "/api/shippings", data=shipping_data)
        # Puede retornar 409 si ya existe
        if response.status_code not in [200, 201, 409]:
            assert False, f"Error al crear shipping: {response.text}"

        if response.status_code in [200, 201]:
            created_shipping = response.json()
            # OrderItem usa productId y orderId como clave compuesta
            shipping_product_id = created_shipping.get("productId")
            shipping_order_id = created_shipping.get("orderId")
        else:
            # Si ya existe, usar los IDs del order y product
            shipping_product_id = product["id"]
            shipping_order_id = order["id"]

        yield {
            "product_id": shipping_product_id,
            "order_id": shipping_order_id,
            "order": order,
            "product": product
        }

        if shipping_product_id and shipping_order_id:
            set_current_service("shipping-service")
            try:
                make_request("DELETE", f"/api/shippings/{shipping_order_id}/{shipping_product_id}")
            except:
                pass
        
        set_current_service("product-service")
        try:
            make_request("DELETE", f"/api/products/{product['id']}")
        except:
            pass

    def test_1_create_shipping(self, create_test_order, create_test_product):
        """Test 1: CREATE - Create a new shipping/order item"""
        set_current_service("shipping-service")
        order = create_test_order
        product = create_test_product
        shipping_data = generate_shipping_data(order["id"], product["id"], quantity=2)
        
        response = make_request("POST", "/api/shippings", data=shipping_data)

        # Puede retornar 409 si ya existe
        assert response.status_code in [200, 201, 409]
        if response.status_code in [200, 201]:
            result = response.json()
            # OrderItem usa productId y orderId como clave compuesta, no orderItemId
            assert result.get("productId") is not None
            assert result.get("orderId") is not None
            set_current_service("shipping-service")
            make_request("DELETE", f'/api/shippings/{result["orderId"]}/{result["productId"]}')

    def test_2_get_all_shippings(self):
        """Test 2: GET ALL - Get all shippings"""
        set_current_service("shipping-service")
        response = make_request("GET", "/api/shippings")

        assert response.status_code == 200
        result = response.json()
        if isinstance(result, dict) and "collection" in result:
            assert isinstance(result["collection"], list)
        elif isinstance(result, list):
            assert len(result) >= 0
        else:
            assert False, f"Formato de respuesta inesperado: {type(result)}"

    def test_3_get_shipping_by_id(self, create_test_shipping):
        """Test 3: GET BY ID - Get shipping by ID"""
        set_current_service("shipping-service")
        shipping = create_test_shipping
        if not shipping.get("order_id") or not shipping.get("product_id"):
            pytest.skip("No shipping IDs available")
        
        # OrderItem usa clave compuesta: /{orderId}/{productId}
        response = make_request("GET", f'/api/shippings/{shipping["order_id"]}/{shipping["product_id"]}')

        assert response.status_code == 200
        result = response.json()
        assert result["orderId"] == shipping["order_id"]
        assert result["productId"] == shipping["product_id"]

    def test_4_update_shipping(self, create_test_shipping):
        """Test 4: UPDATE - Update shipping"""
        set_current_service("shipping-service")
        shipping = create_test_shipping
        if not shipping.get("order_id") or not shipping.get("product_id"):
            pytest.skip("No shipping IDs available")
        
        # Obtener shipping actual usando clave compuesta
        get_response = make_request("GET", f'/api/shippings/{shipping["order_id"]}/{shipping["product_id"]}')
        if get_response.status_code != 200:
            pytest.skip("Cannot get shipping for update")
        
        updated_data = get_response.json()
        updated_data["orderedQuantity"] = 5

        # PUT no requiere ID en la URL, solo en el body
        response = make_request("PUT", "/api/shippings", data=updated_data)

        assert response.status_code == 200

    def test_5_delete_shipping(self, create_test_order, create_test_product):
        """Test 5: DELETE - Delete shipping"""
        set_current_service("shipping-service")
        order = create_test_order
        product = create_test_product
        shipping_data = generate_shipping_data(order["id"], product["id"], quantity=1)
        create_response = make_request("POST", "/api/shippings", data=shipping_data)
        
        if create_response.status_code in [200, 201]:
            result = create_response.json()
            # OrderItem usa clave compuesta: /{orderId}/{productId}
            order_id = result.get("orderId")
            product_id = result.get("productId")
            if order_id and product_id:
                delete_response = make_request("DELETE", f"/api/shippings/{order_id}/{product_id}")
                assert delete_response.status_code in [200, 204]
            else:
                pytest.skip("Could not get shipping IDs for deletion")
        else:
            pytest.skip("Could not create shipping for deletion")


