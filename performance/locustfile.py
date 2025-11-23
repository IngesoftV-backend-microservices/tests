"""
Archivo principal de Locust para ejecutar todas las pruebas de rendimiento.
"""
from performance.locust_user_service import UserServiceUser
from performance.locust_product_service import ProductServiceUser
from performance.locust_order_service import OrderServiceUser
from performance.locust_payment_service import PaymentServiceUser
from performance.locust_api_gateway import APIGatewayUser

