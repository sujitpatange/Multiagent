from abc import ABC, abstractmethod
from common.models import Transaction, Finding
from common.llm_client import OllamaClient
from typing import List

class BaseSpoke(ABC):
    def __init__(self, name: str, model_name: str = "llama3.2"):
        self.name = name
        self.llm = OllamaClient(model=model_name)

    @abstractmethod
    def process_transaction(self, transaction: Transaction) -> Finding:
        """Process a transaction and return a finding."""
        pass

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "capabilities": self.get_capabilities()
        }

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass
