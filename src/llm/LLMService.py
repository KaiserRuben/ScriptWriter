import json
import logging
from typing import Union, Dict, Generator, List

from langchain_core.outputs import GenerationChunk

from src.llm.LLMServiceFactory import LLMServiceFactory

logger = logging.getLogger(__name__)
def _process_response(response: Union[str, Dict, Generator],
                      stream: bool,
                      use_chat: bool) -> Union[str, Dict, Generator[str, None, None]]:
    if not stream:
        return response  # This could be str or Dict depending on the provider's implementation

    def chunk_generator() -> Generator[str, None, None]:
        for chunk in response:
            content = _extract_content(chunk, use_chat)
            if content:
                yield content

    return chunk_generator()


def _extract_content(chunk, use_chat: bool) -> GenerationChunk:
    if hasattr(chunk, 'text'):
        return chunk
    elif hasattr(chunk, 'data'):
        return GenerationChunk(text=chunk.data)
    elif isinstance(chunk, dict):
        if use_chat and 'message' in chunk and 'content' in chunk['message']:
            return  GenerationChunk(text=chunk['message']['content'])
        elif not use_chat and 'response' in chunk:
            return  GenerationChunk(text=chunk['response'])
    return  GenerationChunk(text=str(chunk))


class LLMService:
    def __init__(self, provider_name: str = None, default_model: str = None):
        if provider_name is None:
            provider_name = "ollama"
        if default_model is None:
            default_model = "gemma2:27b"
        self.provider = LLMServiceFactory.get_provider(provider_name)
        self.default_model = default_model

    def generate(self,
                 prompt: str,
                 model: str = None,
                 stream: bool = False,
                 format: str = None,
                 **kwargs) -> Union[str, Dict, Generator[str, None, None]]:
        model = model or self.default_model
        response = self.provider.generate(model, prompt, stream, format, **kwargs)

        if format == "json":
            if isinstance(response, dict):
                return response
            try:
                return json.loads(response) # type: ignore
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON\n\tMessage: {response}\n\tError:{str(e)}")

        return _process_response(response, stream, use_chat=False)

    def chat(self,
             messages: List[Dict],
             model: str = None,
             stream: bool = True,
             format: str = None,
             **kwargs) -> Union[str, Dict, Generator[str, None, None]]:
        model = model or self.default_model
        response = self.provider.chat(model, messages, stream, format, **kwargs)
        return _process_response(response, stream, use_chat=True)

    def name(self):
        return f"{self.provider.name()} - {self.default_model} (default)"

    # Example usage:
    # service = AIService(provider_name="replicate", default_model="meta/llama-2-70b")
    #
    # # Generate
    # result = service.generate("Tell me a joke about programming")
    # print(result)
    #
    # # Chat
    # messages = [
    #     {"role": "user", "content": "What's the capital of France?"},
    #     {"role": "assistant", "content": "The capital of France is Paris."},
    #     {"role": "user", "content": "And what's its population?"}
    # ]
    # result = service.chat(messages)
    # print(result)
