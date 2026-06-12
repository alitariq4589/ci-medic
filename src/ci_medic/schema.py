from pydantic import BaseModel, Field


class Verdict(BaseModel):
    category: str
    confidence: float
    root_cause: str
    evidence: list[str] = Field(default_factory=list)
    suggested_fix: str
    retry_recommended: bool
    fingerprint: str
