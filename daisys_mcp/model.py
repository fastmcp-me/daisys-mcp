from pydantic import BaseModel


class Status:
    WAITING = "waiting"
    STARTED = "started"
    READY = "ready"
    ERROR = "error"
    TIMEOUT = "timeout"


class McpVoice(BaseModel):
    voice_id: str
    name: str
    gender: str
    model: str
    description: str | None
