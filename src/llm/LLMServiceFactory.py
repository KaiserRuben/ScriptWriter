from src.llm.provider.BaseProvider import BaseProvider
from src.llm.provider.OllamaProvider import OllamaProvider
from src.llm.provider.ReplicateProvider import ReplicateProvider
from src.llm.provider.OpenAIProvider import OpenAIProvider

class LLMServiceFactory:
    @staticmethod
    def get_provider(provider_name: str) -> BaseProvider:
        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "replicate":
            return ReplicateProvider()
        elif provider_name == "ollama":
            return OllamaProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")