import os
import json
import logging
import re
from typing import List, Dict, Union, Generator

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk
from openai.types.completion import Completion

from src.llm.provider.BaseProvider import BaseProvider
from dotenv import load_dotenv

load_dotenv()

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"), base_url="http://192.168.0.254:4000")
        self.logger = logging.getLogger(__name__)

    def name(self) -> str:
        return "openai"

    def _generate(self, model: str, messages: List[Dict], stream: bool = False, **kwargs) -> Union[
        Completion, Stream[ChatCompletionChunk]]:
        try:
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"Error in generate: {str(e)}")
            raise

    def generate(self, model: str, prompt: str, stream: bool = True, format: str = None, **kwargs) -> Union[
        Dict, Generator]:
        messages = [{"role": "user", "content": prompt}]
        if format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = self._generate(model, messages, stream, **kwargs)

        if stream:
            return self._stream_generate(response)
        else:
            content = response.choices[0].message.content
            try:
                try:
                    try:
                        return json.loads(content) if format == "json" else content
                    except json.JSONDecodeError as e:
                        p = re.compile('(?<!\\\\)\'')
                        content = p.sub('\"', content)
                        return json.loads(content) if format == "json" else content
                except json.JSONDecodeError as e:
                    content = content.split("\n",1)[1]
            except Exception as e:
                self.logger.error(f"Error in generate: {str(e)}")
                return content

    def chat(self, model: str, messages: List[Dict], stream: bool = True, format: str = None, **kwargs) -> Union[
        Dict, Generator]:
        if format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = self._generate(model, messages, stream, **kwargs)

        if stream:
            return self._stream_generate(response)
        else:
            content = response.choices[0].message.content
            return json.loads(content) if format == "json" else content

    def _stream_generate(self, response: Stream[ChatCompletionChunk]) -> Generator[str, None, None]:
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def create_model(self, name: str, modelfile: str, stream: bool = True) -> Union[Dict, Generator]:
        self.logger.warning("create_model is not supported by OpenAI.")
        return {"success": False, "message": "Operation not supported"}

    def list_models(self) -> List[Dict]:
        return [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        ]

    def show_model(self, name: str) -> Dict:
        models = self.list_models()
        for model in models:
            if model["id"] == name or model["name"] == name:
                return model
        return {"error": "Model not found"}

    def copy_model(self, source: str, destination: str) -> Dict:
        self.logger.warning("copy_model is not supported by OpenAI.")
        return {"success": False, "message": "Operation not supported"}

    def delete_model(self, name: str) -> Dict:
        self.logger.warning("delete_model is not supported by OpenAI.")
        return {"success": False, "message": "Operation not supported"}

    def pull_model(self, name: str, stream: bool = True) -> Union[Dict, Generator]:
        self.logger.warning("pull_model is not supported by OpenAI.")
        return {"success": False, "message": "Operation not supported"}

    def push_model(self, name: str, stream: bool = True) -> Union[Dict, Generator]:
        self.logger.warning("push_model is not supported by OpenAI.")
        return {"success": False, "message": "Operation not supported"}

    def generate_embeddings(self, model: str, input: Union[str, List[str]], **kwargs) -> Dict:
        try:
            response = self.client.embeddings.create(
                model=model,
                input=input,
                **kwargs
            )
            return {
                "embeddings": [embedding.embedding for embedding in response.data],
                "model": response.model,
                "usage": response.usage.dict()
            }
        except Exception as e:
            self.logger.error(f"Error in generate_embeddings: {str(e)}")
            raise

    def list_running_models(self) -> Dict:
        self.logger.warning("list_running_models is not applicable to OpenAI. Returning available models instead.")
        return self.list_models()

# Example usage:
# provider = OpenAIProvider()
# result = provider.generate("gpt-3.5-turbo", "Tell me a joke about programming")
# print(result)
