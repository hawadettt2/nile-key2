from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from .enums import MissionType


class MissionRequest(BaseModel):
    mission_type: MissionType
    payload: Dict[str, Any]
