# llm/base.py
from typing import Protocol
class Provider(Protocol):
    def complete(self, system: str, user: str) -> str: ...

# llm/openai_compat.py  (covers OpenAI, OpenRouter, Ollama, llama-server)
import httpx, os
class OpenAICompat:
    def __init__(self, base_url=None, model=None, api_key=None):
        self.base = base_url or os.environ.get('CI_MEDIC_BASE_URL',
                                               'https://openrouter.ai/api/v1')
        self.model = model or os.environ.get('CI_MEDIC_MODEL')
        self.key = api_key or os.environ.get('CI_MEDIC_API_KEY', 'none')
    def complete(self, system, user) -> str:
        r = httpx.post(f'{self.base}/chat/completions',
            headers={'Authorization': f'Bearer {self.key}'},
            json={'model': self.model, 'temperature': 0,
                  'messages': [{'role': 'system', 'content': system},
                               {'role': 'user', 'content': user}]},
            timeout=120)
        r.raise_for_status()
        return r.json()['choices'][0]['message']['content']