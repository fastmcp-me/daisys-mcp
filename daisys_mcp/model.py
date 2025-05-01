from pydantic import BaseModel


class McpVoice(BaseModel):
    voice_id: str
    name: str
    gender: str
    model: str
    description: str | None
