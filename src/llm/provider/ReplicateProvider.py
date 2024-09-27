import json
import logging
import os
import replicate
from typing import List, Dict, Union, Generator, Any, Iterator

from replicate.stream import ServerSentEvent

from src.llm.provider.BaseProvider import BaseProvider

logger = logging.getLogger(__name__)


class ReplicateProvider(BaseProvider):
    def __init__(self, api_token: str = None):
        self.client = replicate.Client(api_token=api_token or os.environ.get("REPLICATE_API_TOKEN"))

    def name(self) -> str:
        return f"replicate"

    def _generate(self, model: str, input_data: Dict, stream: bool = False) -> Iterator[ServerSentEvent] | Iterator[
        Any] | Any:
        try:
            if stream:
                return self.client.stream(model, input=input_data)
            else:
                return "".join(self.client.run(model, input=input_data))
        except replicate.exceptions.ModelError as e:
            logger.error(f"Model error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def generate(self, model: str, prompt: str, stream: bool = True, format: str = None, **kwargs) -> Union[
        Dict, Generator]:
        input_data = {"prompt": prompt, "max_tokens": 8138, **kwargs}
        if format == "json":
            input_data["format"] = "json"
        response = self._generate(model, input_data, stream)
        if format == "json":
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON\n\tMessage: {response}\n\tError:{str(e)}")
        return response

    def chat(self, model: str, messages: List[Dict], stream: bool = True, format: str = None, **kwargs) -> Union[
        Dict, Generator]:
        # Replicate doesn't distinguish between chat and generate, so we'll use the same method. This method is just a wrapper to align with the necessary interface.
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return self.generate(model, prompt, stream, format, **kwargs)

    def create_model(self, name: str, modelfile: str, stream: bool = True) -> Union[Dict, Generator]:
        logger.warning("create_model is not directly supported by Replicate. Using model creation API instead.")
        try:
            model = self.client.models.create(owner="replicate", name=name, visibility="public")
            return {"id": model.id, "name": model.name}
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            raise

    def list_models(self) -> List:
        # Hardcoded initial list of models
        return [
            {"id": "meta/meta-llama-3.1-405b-instruct", "name": "LLAMA3 [405B] Instruct"},
            {"id": "meta/meta-llama-3-70b-instruct", "name": "LLAMA3 [70B] Instruct"},
            {"id": "meta/meta-llama-3-8b-instruct", "name": "LLAMA3 [8B] Instruct"},
            {"id": "mistralai/mixtral-8x7b-instruct-v0.1", "name": "MistralAI Mixtral [8x7B] Instruct"},
            # Add more models as needed
        ]

    def show_model(self, name: str) -> Dict:
        try:
            model = self.client.models.get(name)
            return {"id": model.id, "name": model.name, "description": model.description}
        except Exception as e:
            logger.error(f"Error showing model: {str(e)}")
            raise

    def copy_model(self, source: str, destination: str) -> Dict:
        logger.warning("copy_model is not supported by Replicate.")
        return {"success": False, "message": "Operation not supported"}

    def delete_model(self, name: str) -> Dict:
        logger.warning("delete_model is not directly supported by Replicate API.")
        return {"success": False, "message": "Operation not supported"}

    def pull_model(self, name: str, stream: bool = True) -> Union[Dict, Generator]:
        logger.warning("pull_model is not directly supported by Replicate. Using model.get instead.")
        model = self.client.models.get(name)
        return {"id": model.id, "name": model.name}

    def push_model(self, name: str, stream: bool = True) -> Union[Dict, Generator]:
        logger.warning("push_model is not supported by Replicate.")
        return {"success": False, "message": "Operation not supported"}

    def generate_embeddings(self, model: str, input: Union[str, List[str]], **kwargs) -> Dict:
        logger.warning("generate_embeddings is not directly supported by Replicate.")
        return {"success": False, "message": "Operation not supported"}

    def list_running_models(self) -> Dict:
        logger.warning("list_running_models is not supported by Replicate. Returning available models instead.")
        return self.list_models()

# Example usage:
# provider = ReplicateProvider()
# result = provider.generate("stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b", "a cat riding a bicycle")
# print(result)
