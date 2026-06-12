import os
import yaml
from dataclasses import dataclass, field

@dataclass
class Config:
    provider: str = "openai-compat"
    model: str = os.environ.get("CI_MEDIC_MODEL", "")
    base_url: str = os.environ.get("CI_MEDIC_BASE_URL", "")
    char_budget: int = 12000
    ignore_jobs: list[str] = field(default_factory=list)
    extra_signals: list[str] = field(default_factory=list)

def load(path: str = ".ci-medic.yml") -> Config:
    if not os.path.exists(path):
        return Config()
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return Config(**{k: v for k, v in data.items()
                     if k in Config.__dataclass_fields__})