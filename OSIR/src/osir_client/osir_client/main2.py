import pprint
import requests
from typing import Optional, List, Dict, Any

class BaseSubClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _handle_api_response(self, response: requests.Response) -> Dict:
        """Extrait la donnée utile de l'enveloppe OsirIpcResponse (clé 'response')."""
        response.raise_for_status()
        data = response.json()
        # Si l'API renvoie l'enveloppe standard {status, response, version}
        if isinstance(data, dict) and "response" in data:
            return data["response"]
        return data

    def _get(self, endpoint: str, params: Optional[Dict] = None):
        return self._handle_api_response(requests.get(f"{self.base_url}{endpoint}", params=params))

    def _post(self, endpoint: str, json_data: Optional[Dict] = None):
        return self._handle_api_response(requests.post(f"{self.base_url}{endpoint}", json=json_data))

# --- Contexte d'une affaire (Case) ---

class CaseContext:
    def __init__(self, base_url: str, case_name: str, data: Dict):
        self.base_url = base_url
        self.name = case_name
        self.data = data
        # Accès chaînés liés au nom de la case
        self.modules = BoundModuleClient(base_url, case_name)
        self.profiles = BoundProfileClient(base_url, case_name)
        self.handlers = BoundHandlerClient(base_url, case_name)
    def __repr__(self):
        return f"<CaseContext name='{self.name}'>"
    
# --- Clients liés à un contexte (Bound) ---
class BoundHandlerClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name
        self.handlers = []
    
    def retrieved_handlers(self):
        pass

    def list(self):
        return self.handlers

class BoundModuleClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name

    def run(self, module_path: str) -> Dict:
        """Exécute un module sur la case actuelle."""
        return self._get(f"/api/module/run/{module_path}", params={"case_name": self.case_name})

class BoundProfileClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name

    def run(self, profile_name: str) -> Dict:
        """Exécute un profil sur la case actuelle."""
        return self._get(f"/api/profile/run/{profile_name}", params={"case_name": self.case_name})

# --- Sections Racines ---

class ModuleClient(BaseSubClient):
    def list(self) -> Dict:
        return self._get("/api/module")

    def exists(self, module_path: str) -> Dict:
        return self._get(f"/api/module/exists/{module_path}")

class CaseClient(BaseSubClient):
    def create(self, name: str) -> CaseContext:
        data = self._post("/api/case", json_data={"name": name})
        return CaseContext(self.base_url, name, data)

    def get(self, name: str) -> CaseContext:
        return CaseContext(self.base_url, name, {})

class LogClient(BaseSubClient):
    def get_task_logs(self, task_id: str) -> Dict:
        """Récupère les logs d'une tâche précise."""
        return self._get("/api/logs/task", params={"task_id": task_id})

    def stream(self):
        """Retourne le flux de logs (requête brute pour itération)."""
        return requests.get(f"{self.base_url}/api/logs/stream", stream=True)

# --- Client Global ---

class OsirClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        url = base_url.rstrip("/")
        self.cases = CaseClient(url)
        self.modules = ModuleClient(url)
        self.logs = LogClient(url)
        self._url = url

    def is_active(self) -> bool:
        return requests.get(f"{self._url}/api/active").status_code == 200

    def get_version(self) -> str:
        return self.cases._get("/api/version")

    def get_status(self, handler_id: str) -> Dict:
        """Récupère le statut d'un handler (ex: progression d'une tâche)."""
        return self.cases._get("/api/status/handler", params={"handler_id": handler_id})
    

client = OsirClient("http://127.0.0.1:8502")
client.cases.get('test_1')
# 1. On lance un module sur une case
# case = client.cases.create("Analyse_S01")
# execution_info = case.modules.run("system.inventory")

# # 2. Supposons que l'exécution retourne un task_id ou un handler_id
# # On peut suivre l'avancement via les logs ou le status
# if "task_id" in execution_info:
#     logs = client.logs.get_task_logs(execution_info["task_id"])
#     print(f"Logs de la tâche : {logs}")

# if "handler_id" in execution_info:
#     status = client.get_status(execution_info["handler_id"])
#     print(f"Statut : {status}")

# # 3. Accès aux modules structurés
# tree = client.modules.list_tree()
# print(f"Structure des modules : {tree.keys()}")