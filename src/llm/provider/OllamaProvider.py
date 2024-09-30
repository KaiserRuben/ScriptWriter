import requests
import json
from typing import List, Dict, Union, Generator

from src.llm.provider.BaseProvider import BaseProvider


class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def name(self) -> str:
        return "ollama"

    def _make_request(self, endpoint: str, data: Dict, stream: bool = False) -> Union[Dict, Generator]:
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        if stream:
            response = requests.post(url, json=data, headers=headers, stream=True)
            return self._stream_response(response)
        else:
            response = requests.post(url, json=data, headers=headers)
            return response.json()

    def _stream_response(self, response: requests.Response) -> Generator:
        for line in response.iter_lines():
            if line:
                yield json.loads(line)

    def generate(self, model: str, prompt: str, stream: bool = True, format: str = None, **kwargs) -> Union[
        Dict, Generator]:
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options":{
                "num_predict": -1,
                      },
            **kwargs
        }
        if format == "json":
            data["format"] = "json"
        response = self._make_request("/api/generate", data, stream)
        return response.get("response") if isinstance(response, dict) else response

    def chat(self, model: str, messages: List[Dict], stream: bool = True, format: str = None, **kwargs) -> Union[
        Dict, Generator]:
        data = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        if format == "json":
            data["format"] = "json"
        return self._make_request("/api/chat", data, stream)
    def create_model(self, name: str, modelfile: str, stream: bool = True) -> Union[Dict, Generator]:
        data = {
            "name": name,
            "modelfile": modelfile,
            "stream": stream
        }
        return self._make_request("/api/create", data, stream)

    def list_models(self) -> List:
        return requests.get(f"{self.base_url}/api/tags").json().get("models")

    def show_model(self, name: str) -> Dict:
        data = {"name": name}
        return self._make_request("/api/show", data)

    def copy_model(self, source: str, destination: str) -> Dict:
        data = {
            "source": source,
            "destination": destination
        }
        return self._make_request("/api/copy", data)

    def delete_model(self, name: str) -> Dict:
        return requests.delete(f"{self.base_url}/api/delete", json={"name": name}).json()

    def pull_model(self, name: str, stream: bool = True) -> Union[Dict, Generator]:
        data = {
            "name": name,
            "stream": stream
        }
        return self._make_request("/api/pull", data, stream)

    def push_model(self, name: str, stream: bool = True) -> Union[Dict, Generator]:
        data = {
            "name": name,
            "stream": stream
        }
        return self._make_request("/api/push", data, stream)

    def generate_embeddings(self, model: str, input: Union[str, List[str]], **kwargs) -> Dict:
        data = {
            "model": model,
            "input": input,
            **kwargs
        }
        return self._make_request("/api/embed", data)

    def list_running_models(self) -> Dict:
        return requests.get(f"{self.base_url}/api/ps").json()

# Example usage:
# ollama = OllamaProvider()
#
# # Generate (streaming, normal format)
# for response in ollama.generate("llama3", "Tell me a joke"):
#     print(response)
#
# # Generate (non-streaming, JSON format)
# response = ollama.generate("llama3", "Tell me a joke in JSON format", stream=False, format="json")
# print(response)
#
# # Chat (streaming, normal format)
# messages = [{"role": "user", "content": "Hi, how are you?"}]
# for response in ollama.chat("llama3", messages):
#     print(response)
#
# # Chat (non-streaming, JSON format)
# messages = [{"role": "user", "content": "Give me a JSON object with your name and mood"}]
# response = ollama.chat("llama3", messages, stream=False, format="json")
# print(response)