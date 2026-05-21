"""
LLM Factory: Centralized provider switching for ReviewLens agents.

Supports three backends:
  1. "gemini"     — Direct Google Gemini via langchain-google-genai (API key auth)
  2. "litellm"    — 100+ providers via LiteLLM's unified OpenAI-compatible interface
  3. "googleADC"  — Google Vertex AI via genai.Client with Application Default Credentials

Switch providers by setting LLM_PROVIDER in .env:
  LLM_PROVIDER=gemini     → Uses GOOGLE_API_KEY + GEMINI_MODEL
  LLM_PROVIDER=litellm    → Uses LITELLM_MODEL + LITELLM_API_KEY
  LLM_PROVIDER=googleADC  → Uses GCP_PROJECT + GCP_LOCATION + ADC (no API key needed)
"""
import logging
from typing import Optional, List

from core.config import settings

logger = logging.getLogger(__name__)


# ─── Google ADC Wrappers ─────────────────────────────────────────────────────

class _GoogleADCChat:
    """
    LangChain-compatible chat model wrapper around google.genai.Client (Vertex AI + ADC).
    Implements .invoke() returning an object with .content attribute (like AIMessage).
    """

    def __init__(self, model: str, project: str, location: str, temperature: float = 0.0, max_tokens: int = 4096):
        from google import genai
        from google.genai.types import HttpOptions

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
            http_options=HttpOptions(api_version="v1"),
        )

    def invoke(self, messages):
        from google.genai.types import GenerateContentConfig

        if isinstance(messages, str):
            prompt = messages
        elif isinstance(messages, list):
            parts = []
            for msg in messages:
                if hasattr(msg, "content"):
                    parts.append(msg.content)
                elif isinstance(msg, str):
                    parts.append(msg)
            prompt = "\n\n".join(parts)
        else:
            prompt = str(messages)

        config = GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        return _AIMessageCompat(response.text or "")


class _GoogleADCEmbeddings:
    """
    LangChain-compatible embeddings wrapper around google.genai.Client (Vertex AI + ADC).
    Implements embed_documents() and embed_query().
    """

    def __init__(self, model: str, project: str, location: str):
        from google import genai
        from google.genai.types import HttpOptions

        self.model = model
        self.client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
            http_options=HttpOptions(api_version="v1"),
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )
        return [emb.values for emb in response.embeddings]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


class _AIMessageCompat:
    """Minimal AIMessage-compatible object with .content attribute."""

    def __init__(self, content: str):
        self.content = content


# ─── LiteLLM Embeddings Wrapper ──────────────────────────────────────────────

class _LiteLLMEmbeddings:
    """
    LangChain-compatible embeddings wrapper around litellm.embedding().
    Implements embed_documents() and embed_query() used by all agents.
    """

    def __init__(self, model: str, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        import litellm

        kwargs = {"model": self.model, "input": texts}
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base

        response = litellm.embedding(**kwargs)
        return [item["embedding"] for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


# ─── Factory Functions ────────────────────────────────────────────────────────

def get_llm(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None,
):
    """
    Returns a LangChain-compatible chat model based on LLM_PROVIDER config.

    Args:
        temperature: Override default temperature (0.0 for deterministic extraction)
        max_tokens: Override default max output tokens
        model: Override the configured model name

    Returns:
        A chat model instance with .invoke() method returning object with .content
    """
    temp = temperature if temperature is not None else settings.LITELLM_TEMPERATURE
    tokens = max_tokens or settings.LITELLM_MAX_TOKENS

    if settings.LLM_PROVIDER == "googleADC":
        adc_model = model or settings.GOOGLE_ADC_MODEL
        logger.debug(f"[LLMFactory] Using Google ADC (Vertex AI) with model={adc_model}")
        return _GoogleADCChat(
            model=adc_model,
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
            temperature=temp,
            max_tokens=tokens,
        )

    elif settings.LLM_PROVIDER == "litellm":
        from langchain_community.chat_models import ChatLiteLLM

        litellm_model = model or settings.LITELLM_MODEL
        kwargs = {
            "model": litellm_model,
            "temperature": temp,
            "max_tokens": tokens,
        }

        if settings.LITELLM_API_KEY:
            kwargs["api_key"] = settings.LITELLM_API_KEY
        if settings.LITELLM_API_BASE:
            kwargs["api_base"] = settings.LITELLM_API_BASE

        logger.debug(f"[LLMFactory] Using LiteLLM provider with model={litellm_model}")
        return ChatLiteLLM(**kwargs)

    else:
        from langchain_google_genai import ChatGoogleGenerativeAI

        gemini_model = model or settings.GEMINI_MODEL
        logger.debug(f"[LLMFactory] Using Gemini provider with model={gemini_model}")
        return ChatGoogleGenerativeAI(
            model=gemini_model,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=temp,
            max_output_tokens=tokens,
        )


def get_embeddings(model: Optional[str] = None):
    """
    Returns a LangChain-compatible embeddings model based on LLM_PROVIDER config.

    Returns:
        An embeddings instance with embed_documents() and embed_query() methods
    """
    if settings.LLM_PROVIDER == "googleADC":
        adc_model = model or settings.GOOGLE_ADC_EMBEDDING_MODEL
        logger.debug(f"[LLMFactory] Using Google ADC embeddings with model={adc_model}")
        return _GoogleADCEmbeddings(
            model=adc_model,
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
        )

    elif settings.LLM_PROVIDER == "litellm":
        embed_model = model or settings.LITELLM_EMBEDDING_MODEL
        logger.debug(f"[LLMFactory] Using LiteLLM embeddings with model={embed_model}")
        return _LiteLLMEmbeddings(
            model=embed_model,
            api_key=settings.LITELLM_API_KEY or None,
            api_base=settings.LITELLM_API_BASE or None,
        )

    else:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        gemini_model = model or settings.GEMINI_EMBEDDING_MODEL
        logger.debug(f"[LLMFactory] Using Gemini embeddings with model={gemini_model}")
        return GoogleGenerativeAIEmbeddings(
            model=gemini_model,
            google_api_key=settings.GOOGLE_API_KEY,
        )
