from pydantic import BaseModel


class Field(BaseModel):
    name:        str
    description: str = ""
    type:        str
