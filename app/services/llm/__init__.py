from app.config import settings
from app.services.llm.provider import LLMProvider
from app.services.llm.openai_llm import OpenAILLMProvider
from app.services.llm.mock_llm import MockLLMProvider
from app.logging_config import logger

def get_llm_provider() -> LLMProvider:
    if settings.has_real_openai_key:
        try:
            return OpenAILLMProvider(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_LLM_MODEL
            )
        except Exception as e:
            logger.error("Failed to initialize OpenAI LLM provider: %s", e)
    return MockLLMProvider()
