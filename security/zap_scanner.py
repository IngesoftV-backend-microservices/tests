"""
Scanner de seguridad usando OWASP ZAP API.
"""
import time
import json
import requests
from typing import Dict, List, Optional

from security.zap_config import SERVICE_URLS, API_ENDPOINTS, AUTH_CONTEXTS, MIN_ALERT_LEVEL


class ZAPScanner:
    """Clase para interactuar con OWASP ZAP API."""
    
    def __init__(self, zap_host: Optional[str] = None, zap_port: Optional[int] = None):
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        self.zap_host = zap_host or os.getenv("ZAP_HOST", "127.0.0.1")
        self.zap_port = zap_port or int(os.getenv("ZAP_PORT", "8090"))
        self.zap_url = f"http://{self.zap_host}:{self.zap_port}"
        self.api_key = os.getenv("ZAP_API_KEY")
        self.session_id = None
        
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Hacer petición a la API de ZAP."""
        url = f"{self.zap_url}{endpoint}"
        if params is None:
            params = {}
        if self.api_key:
            params["apikey"] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            try:
                return response.json()
            except json.JSONDecodeError:
                error_text = response.text[:500]
                raise Exception(f"ZAP devolvió respuesta no-JSON (Status {response.status_code}): {error_text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al conectar con ZAP: {e}")
    
    def _request_post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Hacer petición POST a la API de ZAP."""
        url = f"{self.zap_url}{endpoint}"
        params = {}
        if self.api_key:
            params["apikey"] = self.api_key
        
        try:
            response = requests.post(url, params=params, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al conectar con ZAP: {e}")
    
    def check_connection(self) -> bool:
        """Verificar conexión con ZAP."""
        try:
            result = self._request("/JSON/core/view/version/")
            return "version" in result
        except Exception as e:
            print(f"Error verificando conexión con ZAP: {e}")
            return False
    
    def start_session(self, session_name: str) -> bool:
        """Iniciar una nueva sesión de escaneo."""
        try:
            result = self._request("/JSON/core/action/newSession/", {
                "name": session_name,
                "overwrite": "true"
            })
            return result.get("Result") == "OK"
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            return False
    
    def inject_urls(self, urls: List[str]) -> None:
        """Inyectar URLs en ZAP haciendo requests a través del proxy."""
        zap_proxy = f"http://127.0.0.1:{self.zap_port}"
        for url in urls:
            try:
                requests.get(url, proxies={"http": zap_proxy, "https": zap_proxy}, timeout=5)
            except:
                pass
    
    def spider_scan(self, target_url: str, max_children: int = 10) -> Optional[str]:
        """Iniciar escaneo spider (crawling)."""
        try:
            result = self._request("/JSON/spider/action/scan/", {
                "url": target_url,
                "maxChildren": max_children,
                "recurse": "true"
            })
            return result.get("scan")
        except Exception as e:
            print(f"Error al iniciar spider scan: {e}")
            return None
    
    def active_scan(self, target_url: str, spider_scan_id: Optional[str] = None) -> Optional[str]:
        """Iniciar escaneo activo."""
        try:
            urls = []
            if spider_scan_id:
                try:
                    spider_results = self._request("/JSON/spider/view/results/", {
                        "scanId": spider_scan_id
                    })
                    urls = spider_results.get("results", [])
                except:
                    pass
            
            if not urls:
                try:
                    urls_result = self._request("/JSON/core/view/urls/")
                    urls = urls_result.get("urls", [])
                except:
                    pass
            
            scan_url = target_url
            if urls:
                for url in urls:
                    if target_url in url or url.startswith(target_url):
                        scan_url = url
                        break
            
            try:
                policies = self._request("/JSON/ascan/view/policies/")
                for policy in policies.get("policies", []):
                    policy_id = policy.get("id")
                    if policy_id:
                        self._request("/JSON/ascan/action/setPolicyAttackStrength/", {
                            "id": policy_id,
                            "attackStrength": "HIGH"
                        })
                        self._request("/JSON/ascan/action/setPolicyAlertThreshold/", {
                            "id": policy_id,
                            "alertThreshold": "LOW"
                        })
            except:
                pass
            
            result = self._request("/JSON/ascan/action/scan/", {
                "url": scan_url,
                "recurse": "True",
                "inScopeOnly": "False"
            })
            return result.get("scan")
        except Exception as e:
            print(f"Error al iniciar active scan: {e}")
            return None
    
    def wait_for_scan(self, scan_id: str, scan_type: str = "spider", timeout: int = 300) -> bool:
        """Esperar a que termine un escaneo."""
        endpoint_map = {
            "spider": "/JSON/spider/view/status/",
            "active": "/JSON/ascan/view/status/"
        }
        
        endpoint = endpoint_map.get(scan_type, endpoint_map["spider"])
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = self._request(endpoint, {"scanId": scan_id})
                status = int(result.get("status", 100))
                
                if status == 100:
                    return True
                
                time.sleep(2)
            except Exception as e:
                print(f"Error al verificar estado: {e}")
                return False
        
        return False
    
    def get_alerts(self, base_url: Optional[str] = None, risk_level: Optional[str] = None) -> List[Dict]:
        """Obtener alertas de seguridad."""
        params = {}
        if base_url:
            params["baseurl"] = base_url
        if risk_level:
            params["riskId"] = self._risk_level_to_id(risk_level)
        
        try:
            result = self._request("/JSON/core/view/alerts/", params)
            alerts = result.get("alerts", [])
            
            if risk_level:
                alerts = [a for a in alerts if a.get("risk") == risk_level]
            
            return alerts
        except Exception as e:
            print(f"Error al obtener alertas: {e}")
            return []
    
    def _risk_level_to_id(self, risk_level: str) -> int:
        """Convertir nivel de riesgo a ID."""
        risk_map = {
            "Informational": 0,
            "Low": 1,
            "Medium": 2,
            "High": 3,
            "Critical": 4
        }
        return risk_map.get(risk_level, 0)
    
    def generate_report(self, output_path: str, report_format: str = "HTML") -> bool:
        """Generar reporte de seguridad."""
        try:
            if report_format.upper() == "HTML":
                url = f"{self.zap_url}/OTHER/core/other/htmlreport/"
                params = {}
                if self.api_key:
                    params["apikey"] = self.api_key
                
                response = requests.get(url, params=params, timeout=60)
                response.raise_for_status()
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
            
            elif report_format.upper() == "JSON":
                result = self._request("/JSON/core/view/alertsSummary/")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
            
            elif report_format.upper() == "XML":
                url = f"{self.zap_url}/OTHER/core/other/xmlreport/"
                params = {}
                if self.api_key:
                    params["apikey"] = self.api_key
                
                response = requests.get(url, params=params, timeout=60)
                response.raise_for_status()
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
            else:
                return False
            
            return True
        except Exception as e:
            print(f"Error al generar reporte: {e}")
            return False
    
    def scan_url(self, target_url: str, scan_type: str = "both", known_endpoints: Optional[List[str]] = None) -> Dict:
        """Escanear una URL completa (spider + active scan)."""
        results = {
            "url": target_url,
            "spider_scan": None,
            "active_scan": None,
            "alerts": [],
            "status": "failed"
        }
        
        # Inyectar endpoints conocidos antes del spider scan
        if known_endpoints:
            print(f"Inyectando {len(known_endpoints)} endpoints conocidos en ZAP...")
            full_urls = [f"{target_url.rstrip('/')}{endpoint}" for endpoint in known_endpoints]
            self.inject_urls(full_urls)
            time.sleep(2)
        
        spider_scan_id = None
        if scan_type in ["spider", "both"]:
            print(f"Iniciando spider scan para {target_url}...")
            scan_id = self.spider_scan(target_url, max_children=100)
            if scan_id:
                results["spider_scan"] = scan_id
                spider_scan_id = scan_id
                if self.wait_for_scan(scan_id, "spider"):
                    print(f"Spider scan completado para {target_url}")
                    time.sleep(5)
                    
                    try:
                        spider_results = self._request("/JSON/spider/view/results/", {
                            "scanId": scan_id
                        })
                        urls = spider_results.get("results", [])
                        for url in urls:
                            try:
                                self.inject_urls([url])
                            except:
                                pass
                        time.sleep(3)
                    except:
                        pass
                else:
                    print(f"Spider scan timeout para {target_url}")
        
        if scan_type in ["active", "both"]:
            print(f"Iniciando active scan para {target_url}...")
            
            urls_to_scan = []
            try:
                urls_result = self._request("/JSON/core/view/urls/")
                all_urls = urls_result.get("urls", [])
                urls_to_scan = [url for url in all_urls if target_url.rstrip('/') in url]
            except:
                pass
            
            if not urls_to_scan:
                urls_to_scan = [target_url]
            
            print(f"Escaneando {len(urls_to_scan)} URLs...")
            
            scan_ids = []
            for url in urls_to_scan[:20]:
                try:
                    scan_id = self.active_scan(url, spider_scan_id)
                    if scan_id:
                        scan_ids.append(scan_id)
                except:
                    pass
            
            if scan_ids:
                results["active_scan"] = scan_ids[0]
                print(f"Active scans iniciados: {len(scan_ids)}")
                
                for i, scan_id in enumerate(scan_ids):
                    if self.wait_for_scan(scan_id, "active", timeout=600):
                        print(f"Active scan {i+1}/{len(scan_ids)} completado")
                    else:
                        print(f"Active scan {i+1}/{len(scan_ids)} timeout")
            else:
                scan_id = self.active_scan(target_url, spider_scan_id)
                if scan_id:
                    results["active_scan"] = scan_id
                    if self.wait_for_scan(scan_id, "active", timeout=600):
                        print(f"Active scan completado para {target_url}")
                    else:
                        print(f"Active scan timeout para {target_url}")
                else:
                    print(f"Advertencia: No se pudo iniciar active scan para {target_url}")
        
        time.sleep(5)
        results["alerts"] = self.get_alerts(target_url)
        results["status"] = "completed"
        
        return results

