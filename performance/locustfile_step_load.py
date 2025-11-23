"""
Archivo de Locust con carga escalonada (step load).
Aumenta gradualmente el número de usuarios para encontrar el punto de quiebre.
"""
from performance.locust_user_service import UserServiceUser
from performance.locust_product_service import ProductServiceUser
from performance.locust_order_service import OrderServiceUser
from performance.locust_payment_service import PaymentServiceUser
from performance.locust_api_gateway import APIGatewayUser

# Para usar step load, ejecuta:
# locust -f performance/locustfile_step_load.py --host=http://localhost:8080 --step-load
# O con parámetros específicos:
# locust -f performance/locustfile_step_load.py --host=http://localhost:8080 --step-load --step-users=10 --step-time=30s

