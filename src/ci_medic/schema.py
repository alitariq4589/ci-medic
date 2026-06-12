from typing import Literal
from pydantic import BaseModel, Field

class Verdict(BaseModel):
    category: Literal['code', 'flake', 'infra', 'dependency', 'config']
    confidence: float = Field(ge=0, le=1)
    root_cause: str
    evidence: list[str]
    suggested_fix: str
    retry_recommended: bool
    fingerprint: str = ''