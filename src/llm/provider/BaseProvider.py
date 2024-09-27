from abc import ABC, abstractmethod
from typing import List, Dict, Union, Generator

class BaseProvider(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def generate(self, model: str, prompt: str, stream: bool = True, format: str = None, **kwargs) -> Union[Dict, Generator]:
        pass

    @abstractmethod
    def chat(self, model: str, messages: List[Dict], stream: bool = True, format: str = None, **kwargs) -> Union[Dict, Generator]:
        pass

    @abstractmethod
    def create_model(self, name: str, modelfile: str, stream: bool = True) -> Union[Dict, Generator]:
        pass

    @abstractmethod
    def list_models(self) -> Dict:
        pass

    @abstractmethod
    def show_model(self, name: str) -> Dict:
        pass

    @abstractmethod
    def copy_model(self, source: str, destination: str) -> Dict:
        pass

    @abstractmethod
    def delete_model(self, name: str) -> Dict:
        pass

    @abstractmethod
    def pull_model(self, name: str, stream: bool = True) -> Union[Dict, Generator]:
        pass

    @abstractmethod
    def push_model(self, name: str, stream: bool = True) -> Union[Dict, Generator]:
        pass

    @abstractmethod
    def generate_embeddings(self, model: str, input: Union[str, List[str]], **kwargs) -> Dict:
        pass

    @abstractmethod
    def list_running_models(self) -> Dict:
        pass