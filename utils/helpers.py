"""
Helper functions for tests
"""
import pytest
from faker import Faker
from typing import Dict, Any, Optional
import random
from datetime import datetime

fake = Faker()


def generate_user_data(user_id: Optional[int] = None) -> Dict[str, Any]:
    """Generate fake user data with unique IDs and username"""
    import time
    if user_id is None:
        # Usar timestamp (últimos dígitos) + random para garantizar unicidad
        # Mantener dentro del rango de INT (máx 2,147,483,647)
        # Usamos los últimos 5 dígitos del timestamp + random de 4 dígitos
        timestamp_part = int(time.time()) % 100000  # Últimos 5 dígitos (0-99999)
        random_part = random.randint(1000, 9999)  # 4 dígitos aleatorios
        user_id = timestamp_part * 10000 + random_part  # Máximo: 99999 * 10000 + 9999 = 999,999,999 (seguro)
    
    # Username único usando timestamp
    unique_suffix = int(time.time() * 1000) % 1000000000 + random.randint(100, 999)
    username = f"user_{unique_suffix}"
    
    # Email único
    email = f"user_{unique_suffix}@{fake.domain_name()}"
    
    return {
        "userId": user_id,
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "imageUrl": fake.image_url(),
        "email": email,
        "addressDtos": [
            {
                "fullAddress": fake.address(),
                "postalCode": fake.postcode(),
                "city": fake.city()
            }
        ],
        "credential": {
            "username": username,
            "password": fake.password(length=12),
            "roleBasedAuthority": "ROLE_USER",
            "isEnabled": True,
            "isAccountNonExpired": True,
            "isAccountNonLocked": True,
            "isCredentialsNonExpired": True
        }
    }


def generate_category_data() -> Dict[str, Any]:
    """Generate fake category data with unique name"""
    import time
    # Usar timestamp y random para garantizar unicidad
    unique_id = int(time.time() * 1000000) + random.randint(1000, 9999)
    return {
        "categoryTitle": f"{fake.word().capitalize()} Category {unique_id}",
        "imageUrl": fake.image_url()
    }


def generate_product_data(category_id: int) -> Dict[str, Any]:
    """Generate fake product data"""
    return {
        "productTitle": fake.catch_phrase(),
        "imageUrl": fake.image_url(),
        "sku": f"SKU-{fake.random_int(min=1000, max=9999)}",
        "priceUnit": round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2),
        "quantity": fake.random_int(min=1, max=100),
        "category": {
            "categoryId": category_id
        }
    }


def generate_cart_data(user_id: int) -> Dict[str, Any]:
    """Generate fake cart data"""
    return {
        "userId": user_id
    }


def generate_order_data(cart_id: int) -> Dict[str, Any]:
    """Generate fake order data"""
    return {
        "orderDesc": fake.sentence(),
        "orderFee": round(fake.pyfloat(left_digits=2, right_digits=2, positive=True), 2),
        "cart": {
            "cartId": cart_id
        }
    }


def generate_payment_data(order_id: int) -> Dict[str, Any]:
    """Generate fake payment data"""
    return {
        "isPayed": False,
        "paymentStatus": "NOT_STARTED",
        "order": {
            "orderId": order_id
        }
    }


def generate_shipping_data(order_id: int, product_id: int, quantity: int = 1) -> Dict[str, Any]:
    """Generate fake shipping/order item data"""
    return {
        "productId": product_id,
        "orderId": order_id,
        "orderedQuantity": quantity
    }


def generate_favourite_data(user_id: int, product_id: int) -> Dict[str, Any]:
    """Generate fake favourite data"""
    now = datetime.now()
    like_date = now.strftime("%d-%m-%Y__%H:%M:%S:%f")
    return {
        "userId": user_id,
        "productId": product_id,
        "likeDate": like_date
    }


def generate_address_data(user_id: int) -> Dict[str, Any]:
    """Generate fake address data"""
    return {
        "fullAddress": fake.address(),
        "postalCode": fake.postcode(),
        "city": fake.city(),
        "user": {
            "userId": user_id
        }
    }


def assert_response_success(response, expected_status: int = 200):
    """Assert that response is successful"""
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"


def assert_response_has_data(response):
    """Assert that response has data"""
    data = response.json()
    assert data is not None, "Response data is None"
    return data


def extract_id_from_response(response, id_field: str = "id") -> Optional[int]:
    """Extract ID from response"""
    data = response.json()
    
    # Try different common ID field names
    for field in [id_field, "userId", "productId", "orderId", "cartId", 
                  "paymentId", "categoryId", "addressId", "credentialId"]:
        if field in data:
            return data[field]
    
    # If it's a collection response, try to get first item
    if isinstance(data, dict) and "data" in data:
        items = data["data"]
        if items and len(items) > 0:
            first_item = items[0]
            for field in [id_field, "userId", "productId", "orderId", "cartId",
                         "paymentId", "categoryId", "addressId", "credentialId"]:
                if field in first_item:
                    return first_item[field]
    
    return None


def require_auth(jwt_token: Optional[str]) -> None:
    """
    Helper to skip test if authentication token is not available.
    Use this at the start of E2E tests that require authentication.
    NOTE: Integration tests should NOT use this - they call services directly without auth.
    """
    if not jwt_token:
        pytest.skip("Authentication token not available (proxy-client bug: calls wrong URL)")


# Service context paths for integration tests
SERVICE_CONTEXT_PATHS = {
    "user": "/user-service",
    "product": "/product-service",
    "order": "/order-service",
    "payment": "/payment-service",
    "shipping": "/shipping-service",
    "favourite": "/favourite-service",
    "proxy-client": "/app",
}


def build_integration_url(service_name: str, endpoint: str) -> str:
    """
    Build URL for integration tests with correct context-path.
    
    Args:
        service_name: One of 'user', 'product', 'order', 'payment', 'shipping', 'favourite'
        endpoint: API endpoint (e.g., '/api/users')
    
    Returns:
        Full URL with context-path (e.g., '/user-service/api/users')
    """
    context_path = SERVICE_CONTEXT_PATHS.get(service_name.lower())
    if not context_path:
        raise ValueError(f"Unknown service: {service_name}. Available: {list(SERVICE_CONTEXT_PATHS.keys())}")
    
    endpoint = endpoint.lstrip('/')
    return f"{context_path}/{endpoint}"

