import httpx


class OllamaProvider:
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def complete(self, system: str, user: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
