from pydantic import BaseModel


class OsirVrlField(BaseModel):
    name:        str
    description: str = ""
    type:        str
