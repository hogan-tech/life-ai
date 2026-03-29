from pydantic import BaseModel


class Agent(BaseModel):
    name: str
    role: str
    personality: str
    goal: str
    relationships: dict[str, str] = {}
