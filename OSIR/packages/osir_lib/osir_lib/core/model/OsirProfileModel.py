from pydantic import BaseModel

class OsirProfileModel(BaseModel):
    version: str
    author: str
    description: str
    os: str
    modules: str