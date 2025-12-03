from pydantic import BaseModel

class OsirProfileModel(BaseModel):
    version: float
    author: str
    description: str
    os: str
    modules: list[str]