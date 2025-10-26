"""Constants for AI client configurations.

This module defines all supported models, providers, and configuration options
for various AI services used in the application.
"""

from typing import Literal, Dict, List, Optional

# =============================================================================
# PROVIDER OPTIONS
# =============================================================================

# LLM Providers
LLM_PROVIDERS = Literal["openai", "google"]

# Embedding Providers
EMBEDDING_PROVIDERS = Literal["openai", "google"]

# Vector Store Providers
VECTOR_PROVIDERS = Literal["chroma"]

# =============================================================================
# MODEL OPTIONS
# =============================================================================

# OpenAI LLM Models
OPENAI_MODEL_OPTIONS = Literal[
    "gpt-5",
    "gpt-5-mini",
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-4o-turbo-preview",
]

# OpenAI Embedding Models
OPENAI_EMBEDDING_MODEL_OPTIONS = Literal[
    "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
]

# Google LLM Models (for future expansion)
GOOGLE_MODEL_OPTIONS = Literal[
    "gemini-pro",
    "gemini-pro-vision",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]

# Google Embedding Models (for future expansion)
GOOGLE_EMBEDDING_MODEL_OPTIONS = Literal[
    "text-embedding-004",
    "text-multilingual-embedding-002",
]


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def is_valid_llm_model(model: str, provider: LLM_PROVIDERS) -> bool:
    """Validate if a model is supported for the given LLM provider.

    Args:
        model: Model name to validate
        provider: LLM provider to check against

    Returns:
        True if model is valid for the provider, False otherwise
    """
    if provider == "openai":
        return model in OPENAI_MODEL_OPTIONS.__args__
    elif provider == "google":
        return model in GOOGLE_MODEL_OPTIONS.__args__
    return False


def is_valid_embedding_model(model: str, provider: EMBEDDING_PROVIDERS) -> bool:
    """Validate if a model is supported for the given embedding provider.

    Args:
        model: Model name to validate
        provider: Embedding provider to check against

    Returns:
        True if model is valid for the provider, False otherwise
    """
    if provider == "openai":
        return model in OPENAI_EMBEDDING_MODEL_OPTIONS.__args__
    elif provider == "google":
        return model in GOOGLE_EMBEDDING_MODEL_OPTIONS.__args__
    return False


# =============================================================================
# EXPORTED CONSTANTS
# =============================================================================

# Export all model options for easy importing
ALL_LLM_MODELS = OPENAI_MODEL_OPTIONS.__args__ + GOOGLE_MODEL_OPTIONS.__args__
ALL_EMBEDDING_MODELS = (
    OPENAI_EMBEDDING_MODEL_OPTIONS.__args__ + GOOGLE_EMBEDDING_MODEL_OPTIONS.__args__
)

# Export validation functions
__all__ = [
    # Model Options
    "OPENAI_MODEL_OPTIONS",
    "OPENAI_EMBEDDING_MODEL_OPTIONS",
    "GOOGLE_MODEL_OPTIONS",
    "GOOGLE_EMBEDDING_MODEL_OPTIONS",
    # Provider Options
    "LLM_PROVIDERS",
    "EMBEDDING_PROVIDERS",
    "VECTOR_PROVIDERS",
    # Validation Functions
    "is_valid_llm_model",
    "is_valid_embedding_model",
    # Combined Lists
    "ALL_LLM_MODELS",
    "ALL_EMBEDDING_MODELS",
]
