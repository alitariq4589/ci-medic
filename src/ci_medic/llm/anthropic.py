import httpx


class AnthropicProvider:
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-latest", base_url: str = "https://api.anthropic.com"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def complete(self, system: str, user: str) -> str:
        response = httpx.post(
            f"{self.base_url}/v1/messages",
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": self.model, "messages": [{"role": "user", "content": user}], "system": system},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]
