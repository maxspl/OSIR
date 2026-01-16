from typing import Optional, List, Dict, Any, Type, TypeVar
import requests
from pydantic import BaseModel

# On importe tout le contenu du fichier généré (supposé nommé models.py)
import models

T = TypeVar('T', bound=BaseModel)


class BaseSubClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _handle_api_response(self, response: requests.Response, model: Type[T]) -> T:
        """Parse la réponse avec le modèle Pydantic approprié."""
        response.raise_for_status()
        # On parse l'intégralité du JSON (l'enveloppe OsirIpcResponse incluse)
        return model.model_validate(response.json())

    def _get(self, endpoint: str, model: Type[T], params: Optional[Dict] = None) -> T:
        res = requests.get(f"{self.base_url}{endpoint}", params=params)
        return self._handle_api_response(res, model)

    def _post(self, endpoint: str, model: Type[T], json_data: Optional[Dict] = None) -> T:
        res = requests.post(f"{self.base_url}{endpoint}", json=json_data)
        return self._handle_api_response(res, model)

# --- Clients liés à un contexte (Bound) ---


class BoundHandlerClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name

    def list_active(self) -> List[models.GetHandlerStatusResponseInfo]:
        """Récupère les handlers associés à cette case."""
        res = self._post("/api/handler", models.ApiHandlerGetHandlerStatusResponse2,
                         json_data={"case_name": self.case_name})
        return res.response.handlers


class BoundModuleClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name

    def run(self, module_name: str) -> models.UUID:
        """Exécute un module et retourne le handler_id."""
        res = self._post("/api/module/run", models.RunModuleResponse, json_data={
            "module_name": module_name,
            "case_name": self.case_name
        })
        return res.response.handler_id


class BoundProfileClient(BaseSubClient):
    def __init__(self, base_url: str, case_name: str):
        super().__init__(base_url)
        self.case_name = case_name

    def run(self, profile_name: str) -> models.OsirIpcResponse:
        """Exécute un profil et retourne la réponse IPC."""
        # Le schéma indique une réponse générique OsirIpcResponse pour le run profile
        return self._post("/api/profile/run", models.OsirIpcResponse, json_data={
            "profile_name": profile_name,
            "case_name": self.case_name
        })


class CaseContext:
    def __init__(self, base_url: str, case_name: str, core_data: models.CreateCaseResponseCore):
        self.base_url = base_url
        self.name = case_name
        # C'est maintenant un objet avec .case_uuid, .case_path...
        self.info = core_data
        self.modules = BoundModuleClient(base_url, case_name)
        self.profiles = BoundProfileClient(base_url, case_name)
        self.handlers = BoundHandlerClient(base_url, case_name)

    def __repr__(self):
        return f"<CaseContext name='{self.name}' uuid='{self.info.case_uuid}'>"

# --- Sections Racines ---


class ModuleClient(BaseSubClient):
    def list(self) -> Dict[str, Any]:
        res = self._get("/api/module", models.GetModuleResponse)
        return res.response.modules

    def exists(self, module_path: str) -> models.GetModuleExistsResponseCore:
        res = self._get(
            f"/api/module/exists/{module_path}", models.GetModuleExistsResponse)
        return res.response


class ProfileClient(BaseSubClient):
    def list(self) -> List[str]:
        res = self._get("/api/profile", models.GetProfileResponse)
        return res.response.profiles

    def exists(self, profile_name: str) -> models.GetProfileExistsResponseCore:
        res = self._get(
            f"/api/profile/exists/{profile_name}", models.GetProfileExistsResponse)
        return res.response


class CaseClient(BaseSubClient):
    def list(self) -> List[str]:
        res = self._get("/api/case", models.GetCaseResponse)
        return res.response.cases

    def create(self, name: str) -> CaseContext:
        res = self._post("/api/case", models.CreateCaseResponse,
                         json_data={"case_name": name})
        return CaseContext(self.base_url, name, res.response)

    def get(self, name: str) -> CaseContext:
        # Note: Idéalement, il faudrait un endpoint GET /api/case/{name} pour remplir le context
        return CaseContext(self.base_url, name, models.CreateCaseResponseCore.model_construct(case_name=name))


class OsirClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.cases = CaseClient(self.base_url)
        self.modules = ModuleClient(self.base_url)
        self.profiles = ProfileClient(self.base_url)

    def get_handler_status(self, handler_id: str) -> models.ApiHandlerGetHandlerStatusResponseCore:
        res = BaseSubClient(self.base_url)._post(
            "/api/handler/status",
            models.ApiHandlerGetHandlerStatusResponse,
            json_data={"handler_id": handler_id}
        )
        return res.response

    def get_version(self) -> float:
        res = BaseSubClient(self.base_url)._get(
            "/api/version", models.OsirIpcResponse)
        return res.version


client = OsirClient("http://127.0.0.1:8502")
handler_id = client.cases.get('test_1')
print(handler_id)
# client.cases.get('test_1').modules.run("bodyfile")
# handler_id = client.cases.get("test_1").modules.run("bodyfile")
# # handler_id = client.cases.get('test_1').modules.run('bodyfile')
# print(handler_id)
# # print(f"Module lancé. ID de suivi : {handler_id}")

# 3. Suivi de la progression (POST /api/handler/status)

# print(f"Status: {status['processing_status']}")
# print(f"Tâches générées: {status['task_ids']}")

# # # 4. Récupération des logs si une tâche est présente
# if status['task_ids']:
#     logs = client.logs.get_task_logs('b41dc368-e015-4d46-b2d3-c3751260fadf')
#     print(logs)

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
