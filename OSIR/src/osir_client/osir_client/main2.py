<<<<<<< HEAD
=======
import pprint
>>>>>>> f9f01e99634329d85149028840be42e94cd75666
import requests
from typing import Optional, List, Dict, Any

class BaseSubClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

<<<<<<< HEAD
    def _handle_api_response(self, response: requests.Response) -> Any:
        """Extrait la donnée utile de l'enveloppe OsirIpcResponse."""
        response.raise_for_status()
        data = response.json()
=======
    def _handle_api_response(self, response: requests.Response) -> Dict:
        """Extrait la donnée utile de l'enveloppe OsirIpcResponse (clé 'response')."""
        response.raise_for_status()
        data = response.json()
        # Si l'API renvoie l'enveloppe standard {status, response, version}
>>>>>>> f9f01e99634329d85149028840be42e94cd75666
        if isinstance(data, dict) and "response" in data:
            return data["response"]
        return data

    def _get(self, endpoint: str, params: Optional[Dict] = None):
        return self._handle_api_response(requests.get(f"{self.base_url}{endpoint}", params=params))

    def _post(self, endpoint: str, json_data: Optional[Dict] = None):
        return self._handle_api_response(requests.post(f"{self.base_url}{endpoint}", json=json_data))

# --- Clients liés à un contexte (Bound) ---

class BoundHandlerClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name

    def list_active(self) -> Dict:
        """Récupère les handlers associés à cette case via /api/handler (POST)."""
        return self._post("/api/handler", json_data={"case_name": self.case_name})

class BoundModuleClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name

    def run(self, module_name: str) -> str:
        """Exécute un module et retourne le handler_id."""
        res = self._post("/api/module/run", json_data={
            "module_name": module_name, 
            "case_name": self.case_name
        })
        return res.get("handler_id")

class BoundProfileClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name

    def run(self, profile_name: str) -> Dict:
        """Exécute un profil et retourne la réponse IPC."""
        return self._post("/api/profile/run", json_data={
            "profile_name": profile_name, 
            "case_name": self.case_name
        })

class CaseContext:
    def __init__(self, base_url: str, case_name: str, data: Dict):
        self.base_url = base_url
        self.name = case_name
        self.info = data
        self.modules = BoundModuleClient(base_url, case_name)
        self.profiles = BoundProfileClient(base_url, case_name)
        self.handlers = BoundHandlerClient(base_url, case_name)

    def __repr__(self):
        return f"<CaseContext name='{self.name}'>"

# --- Sections Racines ---

class ModuleClient(BaseSubClient):
    def list(self) -> Dict:
        return self._get("/api/module")

    def exists(self, module_path: str) -> Dict:
        return self._get(f"/api/module/exists/{module_path}")

class ProfileClient(BaseSubClient):
    def list(self) -> List[str]:
        return self._get("/api/profile")

    def exists(self, profile_name: str) -> Dict:
        return self._get(f"/api/profile/exists/{profile_name}")

class CaseClient(BaseSubClient):
    def list(self) -> List[str]:
        return self._get("/api/case")

    def create(self, name: str) -> CaseContext:
        data = self._post("/api/case", json_data={"case_name": name})
        return CaseContext(self.base_url, name, data)

    def get(self, name: str) -> CaseContext:
        return CaseContext(self.base_url, name, {})

class LogClient(BaseSubClient):
    def get_task_logs(self, task_id: str) -> Dict:
        return self._get("/api/logs/task", params={"task_id": task_id})

    def stream(self):
        return requests.get(f"{self.base_url}/api/logs/stream", stream=True)

# --- Client Global ---

class OsirClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.cases = CaseClient(self.base_url)
        self.modules = ModuleClient(self.base_url)
        self.profiles = ProfileClient(self.base_url)
        self.logs = LogClient(self.base_url)

    def is_active(self) -> bool:
        try:
            return self._get("/api/active") is not None
        except:
            return False

    def get_version(self) -> str:
        return self._get("/api/version")

    def get_handler_status(self, handler_id: str) -> Dict:
        """Récupère le statut détaillé d'un handler via /api/handler/status (POST)."""
        return self._post("/api/handler/status", json_data={"handler_id": handler_id})

    def _get(self, endpoint: str):
        return BaseSubClient(self.base_url)._get(endpoint)

    def _post(self, endpoint: str, json_data: Dict):
        return BaseSubClient(self.base_url)._post(endpoint, json_data)
    

client = OsirClient("http://127.0.0.1:8502")
# handler_id = client.cases.get('test_1').profiles.run('uac')
# client.cases.get('test_1').modules.run("bodyfile")
# handler_id = client.cases.get("test_1").modules.run("bodyfile")
# # handler_id = client.cases.get('test_1').modules.run('bodyfile')
# print(handler_id)
# # print(f"Module lancé. ID de suivi : {handler_id}")

# 3. Suivi de la progression (POST /api/handler/status)
status = client.get_handler_status('4144081b-60c4-4ff7-9a7d-13a04cdbdcd0')
print(f"Status: {status['processing_status']}")
print(f"Tâches générées: {status['task_ids']}")

# # 4. Récupération des logs si une tâche est présente
if status['task_ids']:
    logs = client.logs.get_task_logs('b41dc368-e015-4d46-b2d3-c3751260fadf')
    print(logs)

# # print(client.cases.get('test_1').handlers.list_active())
# # client.logs.get_task_logs(t_id)
# from textual.app import App, ComposeResult
# from textual.widgets import Header, Footer, DataTable, Static, TabbedContent, TabPane
# from textual.containers import Container
# from textual.timer import Timer
# import threading

# class OsirMonitor(App):
#     TITLE = "OSIR Monitor"
#     BINDINGS = [("r", "refresh", "Refresh Data"), ("q", "quit", "Quit")]

#     def __init__(self, osir_client, case_name: str):
#         super().__init__()
#         self.client = osir_client
#         self.case_name = case_name

#     def compose(self) -> ComposeResult:
#         yield Header()
#         with TabbedContent():
#             with TabPane("Handlers", id="tab_handlers"):
#                 yield DataTable(id="table_handlers")
#             with TabPane("Tasks", id="tab_tasks"):
#                 yield DataTable(id="table_tasks")
#         yield Footer()

#     def on_mount(self) -> None:
#         # Configuration des colonnes pour les Handlers
#         handler_table = self.query_one("#table_handlers", DataTable)
#         handler_table.add_columns("Handler ID", "Status", "Modules", "Task Count")
#         handler_table.cursor_type = "row"

#         # Configuration des colonnes pour les Tasks
#         task_table = self.query_one("#table_tasks", DataTable)
#         task_table.add_columns("Task ID", "Function", "Start Time", "Duration")
        
#         # Lancement de la mise à jour automatique
#         self.set_interval(600, self.refresh_data)
#         self.refresh_data()

#     def refresh_data(self) -> None:
#         """Récupère les données via le SDK et met à jour les tableaux."""
#         try:
#             case = self.client.cases.get(self.case_name)
            
#             # 1. Mise à jour des Handlers
#             # On récupère les handlers actifs de la case
#             handlers_data = case.handlers.list_active() # Retourne la liste des dicts de status
            
#             handler_table = self.query_one("#table_handlers", DataTable)
#             handler_table.clear()
            
#             all_task_ids = []
            
#             # Note : on itère sur les données brutes reçues de l'API
#             for h in handlers_data['handlers']:
#                 handler_table.add_row(
#                     str(h.get('handler_id', 'N/A')), 
#                     h.get('processing_status', 'unknown'),
#                     ", ".join(h.get('modules', [])),
#                     len(h.get('task_ids', []))
#                 )
#                 all_task_ids.extend(h.get('task_ids', []))

#             # 2. Mise à jour des Tasks (basé sur les IDs trouvés dans les handlers)
#             task_table = self.query_one("#table_tasks", DataTable)
#             task_table.clear()
            
#             for t_id in all_task_ids[:50]: # Limite aux 20 dernières pour la performance
#                 try:
#                     t_info = self.client.logs.get_task_logs(t_id)
#                     task_table.add_row(
#                         str(t_id)[:8],
#                         t_info.get('function', 'N/A'),
#                         t_info.get('start_time', 'N/A'),
#                         f"{t_info.get('duration_seconds', 0):.2f}s"
#                     )
#                 except:
#                     continue

#         except Exception as e:
#             self.notify(f"Erreur de rafraîchissement: {e}", severity="error")

#     def action_refresh(self):
#         self.refresh_data()

# # --- Comment l'utiliser avec ton client ---
# if __name__ == "__main__":
#     # Ton client existant
#     osir = OsirClient("http://127.0.0.1:8502")
    
#     # Lancement de l'interface pour la case 'test_1'
#     app = OsirMonitor(osir, "test_1")
#     app.run()
