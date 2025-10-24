from langchain_openai import ChatOpenAI
from app.clients.base_client import BaseClient
from app.clients.constants import OPENAI_MODEL_OPTIONS


class OpenAiLLMClient(BaseClient[ChatOpenAI]):
    def __init__(
        self, api_key: str, model: OPENAI_MODEL_OPTIONS = "gpt-4o-mini", **kwargs
    ):
        super().__init__()
        self.client: ChatOpenAI = ChatOpenAI(api_key=api_key, model=model, **kwargs)

    def get_client(self) -> ChatOpenAI:
        return self.client
