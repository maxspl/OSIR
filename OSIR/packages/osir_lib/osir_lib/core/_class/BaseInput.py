from pydantic import BaseModel, Field
from pathlib import Path

class BaseInput(BaseModel):
    type: str = Field(default="", description="Type de l'input (ex: file)")
    name: str = Field(default="", description="Nom du fichier ou pattern")
    path: str = Field(default="", description="Chemin complet")