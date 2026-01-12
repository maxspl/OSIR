from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Vertical, Horizontal

# On simule la donnée reçue
RAW_DATA = {
    "version": 1,
    "status": 200,
    "message": "Handler retrieved",
    "response": {
        "handlers": [
            # ... vos données JSON ici ...
            {"handler_id": "c43febc4...", "modules": ["bodyfile"], "processing_status": "processing_started", "task_ids": []},
            {"handler_id": "7e17cb4f...", "modules": ["bodyfile"], "processing_status": "processing_done", "task_ids": ["cf4c7a2d..."]},
            {"handler_id": "2a143bde...", "modules": ["extract_uac", "audit"], "processing_status": "processing_done", "task_ids": ["10458ae2...", "988f0804..."]}
        ]
    }
}

class HandlerManager(App):
    CSS = """
    DataTable {
        height: 60%;
        border: solid green;
    }
    #details {
        height: 40%;
        border: solid orange;
        padding: 1;
        overflow-y: scroll;
    }
    """
    BINDINGS = [("q", "quit", "Quitter")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Static(id="details", content="Sélectionnez un handler pour voir les détails (modules/tasks)")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        # Ajout des colonnes
        table.add_columns("ID (court)", "Status", "Modules Count", "Tasks Count")
        
        # Extraction et remplissage
        handlers = RAW_DATA.get("response", {}).get("handlers", [])
        for h in handlers:
            table.add_row(
                str(h["handler_id"])[:8], # On coupe l'UUID pour la lisibilité
                h["processing_status"],
                str(len(h["modules"])),
                str(len(h["task_ids"])),
                key=h["handler_id"] # On garde l'ID complet en clé
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Affiche les détails complets quand on clique sur une ligne"""
        handler_id = event.row_key.value
        handlers = RAW_DATA.get("response", {}).get("handlers", [])
        
        # Trouver les données correspondantes
        selected = next((h for h in handlers if h["handler_id"] == handler_id), None)
        
        if selected:
            detail_view = self.query_one("#details", Static)
            modules_list = ", ".join(selected["modules"])
            tasks_list = "\n".join(selected["task_ids"]) if selected["task_ids"] else "Aucune"
            
            detail_view.update(
                f"[b]ID Complet:[/b] {selected['handler_id']}\n"
                f"[b]Modules:[/b] {modules_list}\n"
                f"[b]Tasks IDs:[/b]\n{tasks_list}"
            )

if __name__ == "__main__":
    app = HandlerManager()
    app.run()