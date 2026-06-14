import httpx, os

class OpenAICompat:
    """One provider for any OpenAI-compatible endpoint:
    OpenRouter, Ollama (/v1), llama.cpp's llama-server, OpenAI itself."""

    def __init__(self, base_url=None, model=None, api_key=None):
        self.base = (base_url
                     or os.environ.get('CI_MEDIC_BASE_URL')
                     or 'https://openrouter.ai/api/v1').rstrip('/')
        self.model = model or os.environ.get('CI_MEDIC_MODEL')
        self.key = api_key or os.environ.get('CI_MEDIC_API_KEY', 'none')

    def complete(self, system: str, user: str) -> str:
        r = httpx.post(
            f'{self.base}/chat/completions',
            headers={'Authorization': f'Bearer {self.key}',
                     'Content-Type': 'application/json'},
            json={
                'model': self.model,
                'temperature': 0,
                'messages': [
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': user},
                ],
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()['choices'][0]['message']['content']