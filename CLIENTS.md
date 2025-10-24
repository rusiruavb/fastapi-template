# Client Architecture Documentation

## Overview

The `app/clients/` module implements a robust, type-safe client architecture for integrating with external AI services. It follows industry best practices including the Factory Pattern, Dependency Injection, Abstract Base Classes, and comprehensive error handling.

## Architecture Design Patterns

### 1. Abstract Base Class Pattern

The foundation of our client architecture is the `BaseClient` abstract base class:

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

class BaseClient(ABC, Generic[T]):
    """Base interface for clients."""

    def __init__(self):
        self.client: T = None

    @abstractmethod
    def get_client(self) -> T:
        pass
```

**Benefits:**

- **Type Safety**: Uses Generic[T] for compile-time type checking
- **Consistency**: Ensures all clients implement the same interface
- **Extensibility**: Easy to add new client types
- **Polymorphism**: Clients can be used interchangeably

### 2. Factory Pattern

The `ClientFactory` class centralizes client creation logic:

```python
class ClientFactory:
    """Client factory for creating clients."""

    @staticmethod
    def get_openai_llm_client(
        model: Optional[OPENAI_MODEL_OPTIONS] = "gpt-4o-mini", **kwargs
    ) -> ChatOpenAI:
        try:
            if settings.openai_api_key is None:
                raise ValueError("OpenAI API key is not set")

            return OpenAiLLMClient(
                api_key=settings.openai_api_key, model=model, **kwargs
            ).get_client()
        except Exception as e:
            raise ValueError(f"Error creating OpenAI LLM client: {e}")
```

**Benefits:**

- **Centralized Creation**: Single point for client instantiation
- **Error Handling**: Comprehensive validation and error messages
- **Configuration Management**: Handles API keys and settings
- **Consistency**: Uniform interface across all client types

### 3. Dependency Injection Pattern

FastAPI's dependency injection system is used for clean separation of concerns:

```python
# In app/api/deps.py
async def get_openai_embedding_client(
    model: Optional[OPENAI_EMBEDDING_MODEL_OPTIONS] = "text-embedding-3-large",
) -> OpenAIEmbeddings:
    return ClientFactory.get_openai_embedding_client(model=model)

async def get_openai_llm_client(
    model: Optional[OPENAI_MODEL_OPTIONS] = "gpt-4o-mini",
) -> ChatOpenAI:
    return ClientFactory.get_openai_llm_client(model=model)
```

**Benefits:**

- **Testability**: Easy to mock dependencies in tests
- **Flexibility**: Can swap implementations without code changes
- **Configuration**: Model parameters can be configured per request
- **Lifecycle Management**: FastAPI handles dependency lifecycle

## Client Implementations

### 1. OpenAI LLM Client

```python
class OpenAiLLMClient(BaseClient[ChatOpenAI]):
    def __init__(
        self, api_key: str, model: OPENAI_MODEL_OPTIONS = "gpt-4o-mini", **kwargs
    ):
        super().__init__()
        self.client: ChatOpenAI = ChatOpenAI(api_key=api_key, model=model, **kwargs)

    def get_client(self) -> ChatOpenAI:
        return self.client
```

### 2. OpenAI Embedding Client

```python
class OpenAIEmbeddingClient(BaseClient[OpenAIEmbeddings]):
    """OpenAI embedding client."""

    def __init__(
        self,
        api_key: str,
        model: OPENAI_EMBEDDING_MODEL_OPTIONS = "text-embedding-3-large",
        **kwargs,
    ):
        super().__init__()
        self.client: OpenAIEmbeddings = OpenAIEmbeddings(
            api_key=api_key, model=model, **kwargs
        )

    def get_client(self) -> OpenAIEmbeddings:
        return self.client
```

### 3. Chroma Vector Client

```python
class ChromaClient(BaseClient[Chroma]):
    """Chroma vector store client."""

    def __init__(
        self,
        embeddings: Any,
        collection_name: Optional[str] = "documents",
        persist_directory: Optional[str] = "vector_store",
        **kwargs,
    ):
        super().__init__()
        self.client: Chroma = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
            **kwargs,
        )

    def get_client(self) -> Chroma:
        return self.client
```

## Type Safety and Constants

The module uses Literal types for compile-time validation:

```python
OPENAI_EMBEDDING_MODEL_OPTIONS = Literal[
    "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
]

OPENAI_MODEL_OPTIONS = Literal[
    "gpt-5",
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4o-turbo",
    "gpt-4o-turbo-preview",
    "gpt-4o-turbo-preview-2025-05-14",
    "gpt-4o-turbo-preview-2025-05-14-2",
]

EMBEDDING_PROVIDERS = Literal["openai", "google"]
VECTOR_PROVIDERS = Literal["chroma", "pinecone"]
LLM_PROVIDERS = Literal["openai"]
```

**Benefits:**

- **Compile-time Validation**: IDE catches invalid model names
- **Documentation**: Clear list of supported options
- **Refactoring Safety**: Renaming models updates all references

## Usage Examples

### 1. API Endpoint Usage

```python
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.api.deps import get_openai_embedding_client, get_openai_llm_client
from app.services.chunk_service import ChunkService
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("/upload")
async def upload_documents(
    files: Annotated[
        list[UploadFile], File(description="Knowledge base document files")
    ],
):
    # Validate file types
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Get clients through dependency injection
    embeddings = await get_openai_embedding_client(model="text-embedding-3-large")
    llm = await get_openai_llm_client(model="gpt-4o-mini")

    # Create services with injected clients
    document_service = DocumentService(llm=llm)
    chunk_service = ChunkService(embeddings=embeddings, llm=llm)

    # Process documents
    text = await document_service.extract_pdf(files)
    chunks = await chunk_service.semantic_chunk(text)

    return Response(content=json.dumps(chunks), media_type="application/json")
```

### 2. Service Layer Usage

```python
class ChunkService:
    def __init__(
        self,
        embeddings: OpenAIEmbeddings | GoogleGenerativeAIEmbeddings,
        llm: ChatOpenAI,
    ):
        self.embeddings = embeddings
        self.llm = llm

    async def semantic_chunk(
        self,
        text: str,
        breakpoint_threshold_type: BreakpointThresholdType = "interquartile",
    ) -> List[Document]:
        semantic_chunker = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type=breakpoint_threshold_type,
        )
        documents = semantic_chunker.create_documents([text])
        return documents

    async def agentic_chunk(self, text: str) -> List[Document]:
        agentic_chunker = AgenticChunker(llm=self.llm)
        propositions = agentic_chunker.get_propositions(text)
        agentic_chunker.add_propositions(propositions)
        chunks = agentic_chunker.get_chunks(get_type=GetType.LIST_OF_STRING)
        documents = [Document(page_content=chunk) for chunk in chunks]
        return documents
```

### 3. Direct Factory Usage (Not Recommended)

```python
# Direct usage - avoid in production code
from app.clients import ClientFactory

# Create clients directly
llm_client = ClientFactory.get_openai_llm_client(model="gpt-4o-mini")
embedding_client = ClientFactory.get_openai_embedding_client(model="text-embedding-3-large")
vector_client = ClientFactory.get_chroma_vector_client(embeddings=embedding_client)
```

## Error Handling

The client architecture includes comprehensive error handling:

```python
@staticmethod
def get_openai_llm_client(
    model: Optional[OPENAI_MODEL_OPTIONS] = "gpt-4o-mini", **kwargs
) -> ChatOpenAI:
    try:
        # Validate API key
        if settings.openai_api_key is None:
            raise ValueError("OpenAI API key is not set")

        # Create client
        return OpenAiLLMClient(
            api_key=settings.openai_api_key, model=model, **kwargs
        ).get_client()
    except Exception as e:
        # Provide descriptive error message
        raise ValueError(f"Error creating OpenAI LLM client: {e}")
```

**Error Handling Features:**

- **API Key Validation**: Checks for missing API keys
- **Descriptive Messages**: Clear error messages for debugging
- **Exception Wrapping**: Converts all exceptions to ValueError for consistency
- **Graceful Failures**: Prevents silent failures

## Best Practices

### 1. Always Use Dependency Injection

✅ **Good:**

```python
async def endpoint(embeddings: OpenAIEmbeddings = Depends(get_openai_embedding_client)):
    # Use embeddings
```

❌ **Bad:**

```python
async def endpoint():
    embeddings = ClientFactory.get_openai_embedding_client()  # Direct instantiation
```

### 2. Configure Models Through Dependencies

✅ **Good:**

```python
async def get_openai_llm_client(
    model: Optional[OPENAI_MODEL_OPTIONS] = "gpt-4o-mini",
) -> ChatOpenAI:
    return ClientFactory.get_openai_llm_client(model=model)
```

❌ **Bad:**

```python
# Hardcoded model in service
class SomeService:
    def __init__(self):
        self.llm = ClientFactory.get_openai_llm_client(model="gpt-4o-mini")
```

### 3. Use Type Hints

✅ **Good:**

```python
def process_text(self, embeddings: OpenAIEmbeddings, llm: ChatOpenAI) -> List[Document]:
    # Implementation
```

❌ **Bad:**

```python
def process_text(self, embeddings, llm):  # No type hints
    # Implementation
```

### 4. Handle Errors Gracefully

✅ **Good:**

```python
try:
    client = ClientFactory.get_openai_llm_client()
except ValueError as e:
    logger.error(f"Failed to create LLM client: {e}")
    raise HTTPException(status_code=500, detail="Service unavailable")
```

❌ **Bad:**

```python
client = ClientFactory.get_openai_llm_client()  # No error handling
```

## Testing

### 1. Mocking Dependencies

```python
from unittest.mock import Mock, patch
from app.api.deps import get_openai_llm_client

@patch('app.clients.ClientFactory.get_openai_llm_client')
async def test_endpoint(mock_factory):
    # Setup mock
    mock_client = Mock()
    mock_factory.return_value = mock_client

    # Test endpoint
    embeddings = await get_openai_llm_client()
    assert embeddings == mock_client
```

### 2. Testing Services

```python
from unittest.mock import Mock
from app.services.chunk_service import ChunkService

def test_chunk_service():
    # Create mock clients
    mock_embeddings = Mock()
    mock_llm = Mock()

    # Create service with mocks
    service = ChunkService(embeddings=mock_embeddings, llm=mock_llm)

    # Test methods
    result = service.semantic_chunk("test text")
    assert result is not None
```

## Extending the Architecture: Adding New Clients

This section provides comprehensive guidance on adding new clients while maintaining design patterns and best practices.

### Step-by-Step Guide: Adding a New Client Provider

Let's walk through adding Google's Gemini as a new LLM provider:

#### Step 1: Update Constants

First, add the new provider and model options to `constants.py`:

```python
# app/clients/constants.py
from typing import Literal

# Existing constants...
OPENAI_MODEL_OPTIONS = Literal[
    "gpt-5",
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4o-turbo",
    "gpt-4o-turbo-preview",
    "gpt-4o-turbo-preview-2025-05-14",
    "gpt-4o-turbo-preview-2025-05-14-2",
]

# Add new Google model options
GOOGLE_MODEL_OPTIONS = Literal[
    "gemini-pro",
    "gemini-pro-vision",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]

# Update provider constants
LLM_PROVIDERS = Literal["openai", "google"]  # Add "google"
EMBEDDING_PROVIDERS = Literal["openai", "google"]
VECTOR_PROVIDERS = Literal["chroma", "pinecone"]
```

#### Step 2: Create the Client Implementation

Create a new file `app/clients/llm/google_llm_client.py`:

```python
# app/clients/llm/google_llm_client.py
from langchain_google_genai import ChatGoogleGenerativeAI
from app.clients.base_client import BaseClient
from app.clients.constants import GOOGLE_MODEL_OPTIONS


class GoogleLLMClient(BaseClient[ChatGoogleGenerativeAI]):
    """Google Gemini LLM client implementation."""

    def __init__(
        self,
        api_key: str,
        model: GOOGLE_MODEL_OPTIONS = "gemini-pro",
        **kwargs
    ):
        """
        Initialize Google LLM client.

        Args:
            api_key: Google API key for authentication
            model: Google model to use (default: gemini-pro)
            **kwargs: Additional parameters for ChatGoogleGenerativeAI
        """
        super().__init__()

        # Validate required parameters
        if not api_key:
            raise ValueError("Google API key is required")

        try:
            self.client: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
                api_key=api_key,
                model=model,
                **kwargs
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Google LLM client: {e}")

    def get_client(self) -> ChatGoogleGenerativeAI:
        """Return the configured Google LLM client."""
        return self.client
```

#### Step 3: Update the Factory

Add the new client to `ClientFactory` in `app/clients/__init__.py`:

```python
# app/clients/__init__.py
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI  # Add import

from app.clients.embeddings.openai_embedding_client import OpenAIEmbeddingClient
from app.clients.llm.openai_llm_client import OpenAiLLMClient
from app.clients.llm.google_llm_client import GoogleLLMClient  # Add import
from app.core.config import settings
from app.clients.vector.chroma_client import ChromaClient
from app.clients.constants import (
    OPENAI_MODEL_OPTIONS,
    OPENAI_EMBEDDING_MODEL_OPTIONS,
    GOOGLE_MODEL_OPTIONS,  # Add import
)


class ClientFactory:
    """Client factory for creating clients."""

    # Existing methods...

    @staticmethod
    def get_google_llm_client(
        model: Optional[GOOGLE_MODEL_OPTIONS] = "gemini-pro", **kwargs
    ) -> ChatGoogleGenerativeAI:
        """
        Create a Google LLM client.

        Args:
            model: Google model to use
            **kwargs: Additional parameters

        Returns:
            Configured ChatGoogleGenerativeAI client

        Raises:
            ValueError: If API key is missing or client creation fails
        """
        try:
            if not hasattr(settings, 'google_api_key') or settings.google_api_key is None:
                raise ValueError("Google API key is not set in configuration")

            return GoogleLLMClient(
                api_key=settings.google_api_key,
                model=model,
                **kwargs
            ).get_client()
        except Exception as e:
            raise ValueError(f"Error creating Google LLM client: {e}")
```

#### Step 4: Add Configuration Support

Update `app/core/config.py` to include Google API key:

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings...
    openai_api_key: str | None = None

    # Add Google API key
    google_api_key: str | None = None

    class Config:
        env_file = ".env"
```

#### Step 5: Create Dependency Injection Function

Add dependency function in `app/api/deps.py`:

```python
# app/api/deps.py
from langchain_google_genai import ChatGoogleGenerativeAI
from app.clients.constants import GOOGLE_MODEL_OPTIONS

# Add new dependency function
async def get_google_llm_client(
    model: Optional[GOOGLE_MODEL_OPTIONS] = "gemini-pro",
) -> ChatGoogleGenerativeAI:
    """
    Dependency function for Google LLM client.

    Args:
        model: Google model to use

    Returns:
        Configured Google LLM client
    """
    return ClientFactory.get_google_llm_client(model=model)
```

#### Step 6: Update Service Layer

Modify services to support multiple providers. Update `ChunkService`:

```python
# app/services/chunk_service.py
from typing import Union
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Create a union type for all LLM clients
LLMClient = Union[ChatOpenAI, ChatGoogleGenerativeAI]
EmbeddingClient = Union[OpenAIEmbeddings, GoogleGenerativeAIEmbeddings]

class ChunkService:
    def __init__(
        self,
        embeddings: EmbeddingClient,
        llm: LLMClient,
    ):
        self.embeddings = embeddings
        self.llm = llm

    async def agentic_chunk(self, text: str) -> List[Document]:
        """Agentic chunking that works with any LLM provider."""
        agentic_chunker = AgenticChunker(llm=self.llm)
        propositions = agentic_chunker.get_propositions(text)
        agentic_chunker.add_propositions(propositions)
        chunks = agentic_chunker.get_chunks(get_type=GetType.LIST_OF_STRING)
        documents = [Document(page_content=chunk) for chunk in chunks]
        return documents
```

#### Step 7: Update API Endpoints

Modify endpoints to support provider selection:

```python
# app/api/v1/endpoints/documents.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from typing import Annotated, Optional
from app.api.deps import (
    get_openai_embedding_client,
    get_openai_llm_client,
    get_google_llm_client  # Add import
)
from app.clients.constants import LLM_PROVIDERS

router = APIRouter()

@router.post("/upload")
async def upload_documents(
    files: Annotated[
        list[UploadFile], File(description="Knowledge base document files")
    ],
    llm_provider: Optional[LLM_PROVIDERS] = Query(
        default="openai",
        description="LLM provider to use"
    ),
):
    """Upload and process documents with configurable LLM provider."""

    # Validate file types
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Get clients based on provider
    embeddings = await get_openai_embedding_client(model="text-embedding-3-large")

    if llm_provider == "openai":
        llm = await get_openai_llm_client(model="gpt-4o-mini")
    elif llm_provider == "google":
        llm = await get_google_llm_client(model="gemini-pro")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {llm_provider}")

    # Create services with injected clients
    document_service = DocumentService(llm=llm)
    chunk_service = ChunkService(embeddings=embeddings, llm=llm)

    # Process documents
    text = await document_service.extract_pdf(files)
    chunks = await chunk_service.semantic_chunk(text)

    return Response(content=json.dumps(chunks), media_type="application/json")
```

### Advanced Pattern: Provider-Agnostic Client Manager

For more complex scenarios, create a provider-agnostic client manager:

```python
# app/clients/client_manager.py
from typing import Dict, Any, Optional, Union
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.clients.constants import LLM_PROVIDERS, EMBEDDING_PROVIDERS
from app.clients import ClientFactory

class ClientManager:
    """Centralized client manager with provider support."""

    def __init__(self):
        self._llm_clients: Dict[str, Any] = {}
        self._embedding_clients: Dict[str, Any] = {}

    def get_llm_client(
        self,
        provider: LLM_PROVIDERS,
        model: Optional[str] = None,
        **kwargs
    ) -> Union[ChatOpenAI, ChatGoogleGenerativeAI]:
        """
        Get LLM client for specified provider.

        Args:
            provider: LLM provider to use
            model: Specific model to use (optional)
            **kwargs: Additional parameters

        Returns:
            Configured LLM client
        """
        cache_key = f"{provider}_{model or 'default'}"

        if cache_key not in self._llm_clients:
            if provider == "openai":
                model = model or "gpt-4o-mini"
                self._llm_clients[cache_key] = ClientFactory.get_openai_llm_client(
                    model=model, **kwargs
                )
            elif provider == "google":
                model = model or "gemini-pro"
                self._llm_clients[cache_key] = ClientFactory.get_google_llm_client(
                    model=model, **kwargs
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        return self._llm_clients[cache_key]

    def get_embedding_client(
        self,
        provider: EMBEDDING_PROVIDERS,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Get embedding client for specified provider."""
        cache_key = f"{provider}_{model or 'default'}"

        if cache_key not in self._embedding_clients:
            if provider == "openai":
                model = model or "text-embedding-3-large"
                self._embedding_clients[cache_key] = ClientFactory.get_openai_embedding_client(
                    model=model, **kwargs
                )
            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")

        return self._embedding_clients[cache_key]

# Global instance
client_manager = ClientManager()
```

### Testing New Clients

#### Unit Tests for New Client

```python
# tests/test_clients/test_google_llm_client.py
import pytest
from unittest.mock import Mock, patch
from app.clients.llm.google_llm_client import GoogleLLMClient
from app.clients.constants import GOOGLE_MODEL_OPTIONS

class TestGoogleLLMClient:
    def test_init_success(self):
        """Test successful client initialization."""
        with patch('app.clients.llm.google_llm_client.ChatGoogleGenerativeAI') as mock_chat:
            mock_client = Mock()
            mock_chat.return_value = mock_client

            client = GoogleLLMClient(api_key="test-key", model="gemini-pro")

            assert client.get_client() == mock_client
            mock_chat.assert_called_once_with(api_key="test-key", model="gemini-pro")

    def test_init_missing_api_key(self):
        """Test initialization with missing API key."""
        with pytest.raises(ValueError, match="Google API key is required"):
            GoogleLLMClient(api_key="", model="gemini-pro")

    def test_init_client_creation_failure(self):
        """Test handling of client creation failure."""
        with patch('app.clients.llm.google_llm_client.ChatGoogleGenerativeAI') as mock_chat:
            mock_chat.side_effect = Exception("API Error")

            with pytest.raises(ValueError, match="Failed to initialize Google LLM client"):
                GoogleLLMClient(api_key="test-key", model="gemini-pro")
```

#### Integration Tests

```python
# tests/test_integration/test_client_factory.py
import pytest
from app.clients import ClientFactory
from app.core.config import settings

class TestClientFactory:
    @pytest.mark.asyncio
    async def test_get_google_llm_client_success(self):
        """Test successful Google LLM client creation."""
        with patch.object(settings, 'google_api_key', 'test-key'):
            with patch('app.clients.llm.google_llm_client.ChatGoogleGenerativeAI'):
                client = ClientFactory.get_google_llm_client(model="gemini-pro")
                assert client is not None

    @pytest.mark.asyncio
    async def test_get_google_llm_client_missing_key(self):
        """Test Google LLM client creation with missing API key."""
        with patch.object(settings, 'google_api_key', None):
            with pytest.raises(ValueError, match="Google API key is not set"):
                ClientFactory.get_google_llm_client()
```

### Best Practices for Adding New Clients

#### 1. Follow the Established Pattern

✅ **Always follow this structure:**

```python
# 1. Constants
PROVIDER_MODEL_OPTIONS = Literal["model1", "model2"]

# 2. Client Implementation
class ProviderClient(BaseClient[ProviderType]):
    def __init__(self, api_key: str, model: PROVIDER_MODEL_OPTIONS, **kwargs):
        # Implementation
    def get_client(self) -> ProviderType:
        # Return client

# 3. Factory Method
@staticmethod
def get_provider_client(model: Optional[PROVIDER_MODEL_OPTIONS], **kwargs) -> ProviderType:
    # Factory implementation

# 4. Dependency Function
async def get_provider_client(model: Optional[PROVIDER_MODEL_OPTIONS]) -> ProviderType:
    # Dependency implementation
```

#### 2. Maintain Type Safety

✅ **Use proper type annotations:**

```python
from typing import Union, Optional, Literal

# Union types for multiple providers
LLMClient = Union[ChatOpenAI, ChatGoogleGenerativeAI]

# Literal types for model options
GOOGLE_MODEL_OPTIONS = Literal["gemini-pro", "gemini-pro-vision"]
```

#### 3. Implement Comprehensive Error Handling

✅ **Always include validation:**

```python
def __init__(self, api_key: str, model: MODEL_OPTIONS, **kwargs):
    if not api_key:
        raise ValueError("API key is required")

    try:
        self.client = ProviderClient(api_key=api_key, model=model, **kwargs)
    except Exception as e:
        raise ValueError(f"Failed to initialize client: {e}")
```

#### 4. Add Configuration Support

✅ **Update settings and environment:**

```python
# In .env
GOOGLE_API_KEY=your_google_api_key_here

# In config.py
google_api_key: str | None = None
```

#### 5. Write Comprehensive Tests

✅ **Test all scenarios:**

- Successful initialization
- Missing API keys
- Invalid models
- Client creation failures
- Integration with factory

### Common Pitfalls to Avoid

#### ❌ **Don't Skip Error Handling**

```python
# Bad
def __init__(self, api_key: str):
    self.client = ProviderClient(api_key=api_key)  # No validation
```

#### ❌ **Don't Hardcode Configuration**

```python
# Bad
def get_client(self):
    return ProviderClient(api_key="hardcoded-key")  # Hardcoded
```

#### ❌ **Don't Skip Type Annotations**

```python
# Bad
def get_client(self):  # No return type
    return self.client
```

#### ❌ **Don't Forget Dependency Injection**

```python
# Bad - Direct instantiation in services
class SomeService:
    def __init__(self):
        self.client = ClientFactory.get_provider_client()  # Direct usage
```

### Configuration Management

#### Environment Variables

```bash
# .env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4o-mini
```

#### Configuration Class

```python
# app/core/config.py
class Settings(BaseSettings):
    # API Keys
    openai_api_key: str | None = None
    google_api_key: str | None = None

    # Default Settings
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o-mini"
    default_embedding_model: str = "text-embedding-3-large"

    # Client Settings
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000

    class Config:
        env_file = ".env"
```

This comprehensive guide ensures that new clients are added following established patterns while maintaining code quality, type safety, and testability.

## Performance Considerations

### 1. Client Reuse

Clients are designed to be reused across requests. The Factory pattern ensures efficient client creation:

```python
# Clients are created once per request and reused
async def process_multiple_documents(
    embeddings: OpenAIEmbeddings = Depends(get_openai_embedding_client)
):
    # Same embeddings client used for all documents
    for document in documents:
        result = await process_document(document, embeddings)
```

### 2. Connection Pooling

The underlying LangChain clients handle connection pooling automatically, so no additional configuration is needed.

## Security Considerations

### 1. API Key Management

- API keys are stored in environment variables
- Keys are validated before client creation
- No hardcoded credentials in the codebase

### 2. Error Information

- Error messages don't expose sensitive information
- Internal errors are wrapped with generic messages
- Detailed errors are logged server-side only

## Conclusion

The client architecture provides:

- **Type Safety**: Compile-time validation of models and parameters
- **Error Handling**: Comprehensive validation and graceful failure handling
- **Testability**: Easy mocking and testing through dependency injection
- **Extensibility**: Simple to add new client types and providers
- **Maintainability**: Clean separation of concerns and consistent patterns
- **Performance**: Efficient client creation and reuse

This architecture follows industry best practices and provides a solid foundation for integrating with AI services in a FastAPI application.
