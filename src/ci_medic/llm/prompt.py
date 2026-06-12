import json

from pydantic import BaseModel, ValidationError


SYSTEM_PROMPT = """
You are ci-medic, an expert CI failure triage assistant.
Return only valid JSON matching the required verdict schema.
"""


def build_user_prompt(log_text: str) -> str:
    return f"Analyze this log and identify the likely root cause, evidence, and fix.\n\n```log\n{log_text}\n```"


def validate_json(payload: str, model_cls: type[BaseModel]) -> BaseModel:
    data = json.loads(payload)
    return model_cls.model_validate(data)


def complete_with_retry(provider, log_text: str, model_cls: type[BaseModel], retries: int = 1):
    user = build_user_prompt(log_text)
    for attempt in range(retries + 1):
        try:
            raw = provider.complete(SYSTEM_PROMPT, user)
            return validate_json(raw, model_cls)
        except (json.JSONDecodeError, ValidationError, ValueError):
            if attempt == retries:
                raise
    raise RuntimeError("Failed to generate a valid verdict")
