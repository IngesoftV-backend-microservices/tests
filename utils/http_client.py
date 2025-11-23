"""
HTTP Client utility for making API requests
"""
import requests
from typing import Dict, Optional, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:
    """HTTP client with retry logic and error handling"""
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request"""
        url = self._build_url(endpoint)
        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            json=json,
            params=params,
            timeout=self.timeout,
            **kwargs
        )
        return response
    
    def get(self, endpoint: str, headers: Optional[Dict] = None, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """GET request"""
        return self._make_request("GET", endpoint, headers=headers, params=params, **kwargs)
    
    def post(self, endpoint: str, headers: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """POST request"""
        return self._make_request("POST", endpoint, headers=headers, json=json, **kwargs)
    
    def put(self, endpoint: str, headers: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """PUT request"""
        return self._make_request("PUT", endpoint, headers=headers, json=json, **kwargs)
    
    def patch(self, endpoint: str, headers: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """PATCH request"""
        return self._make_request("PATCH", endpoint, headers=headers, json=json, **kwargs)
    
    def delete(self, endpoint: str, headers: Optional[Dict] = None, **kwargs) -> requests.Response:
        """DELETE request"""
        return self._make_request("DELETE", endpoint, headers=headers, **kwargs)
    
    def health_check(self, endpoint: str = "/actuator/health") -> bool:
        """Check if service is healthy"""
        try:
            response = self.get(endpoint)
            return response.status_code == 200
        except Exception:
            return False

