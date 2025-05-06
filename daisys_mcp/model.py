from pydantic import BaseModel
from typing import List, Optional, Union
import enum


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

class McpModel(BaseModel):
    name: str
    displayname: str
    flags : Optional[List]
    languages: List[str]
    genders: List[str]
    styles: List[List[str]]
    prosody_types: List[str]

class VoiceGender(str, enum.Enum):
    """Represents the gender of a voice.

    Note: upper case in Python, lower case in JSON.

    Values:
      MALE, FEMALE, NONBINARY
    """
    MALE = 'male'
    FEMALE = 'female'
    NONBINARY = 'nonbinary'

