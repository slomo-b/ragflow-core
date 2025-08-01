# File: backend/app/services/llm_service.py
import google.generativeai as genai
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from enum import Enum

from ..core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    GEMINI = "gemini"
    OLLAMA = "ollama"

class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        pass

class GeminiClient(BaseLLMClient):
    """Google Gemini API client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("Gemini client initialized")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        try:
            # Convert messages to Gemini format
            prompt = self._format_messages(messages)
            
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                top_k=64,
            )
            
            # Generate response
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            if response.text:
                logger.info(f"Gemini response generated: {len(response.text)} chars")
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini")
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to single prompt for Gemini"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                formatted.append(f"Instructions: {content}")
            elif role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        
        return "\n\n".join(formatted)

class OllamaClient(BaseLLMClient):
    """Ollama local API client"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        logger.info(f"Ollama client initialized: {base_url} - {model}")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        try:
            # Check if Ollama is available
            if not await self._check_health():
                raise Exception("Ollama service is not available")
            
            # Prepare request
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_ctx": 4096,
                    "temperature": temperature,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": max_tokens
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("message", {}).get("content", "")
                        logger.info(f"Ollama response generated: {len(content)} chars")
                        return content.strip()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise Exception(f"Ollama API error: {str(e)}")
    
    async def _check_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
                    return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []

class LLMService:
    """Unified LLM service supporting multiple providers"""
    
    def __init__(self):
        self.clients: Dict[LLMProvider, BaseLLMClient] = {}
        self.default_provider = LLMProvider.GEMINI
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available LLM clients"""
        # Initialize Gemini if API key is available
        if hasattr(settings, 'google_api_key') and settings.google_api_key:
            try:
                self.clients[LLMProvider.GEMINI] = GeminiClient(settings.google_api_key)
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        
        # Initialize Ollama ONLY if service is available (optional)
        try:
            ollama_url = getattr(settings, 'ollama_url', 'http://localhost:11434')
            ollama_model = getattr(settings, 'ollama_model', 'llama3.2')
            
            # Test if Ollama is available before initializing
            import aiohttp
            import asyncio
            
            async def check_ollama():
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{ollama_url}/api/tags",
                            timeout=aiohttp.ClientTimeout(total=3)
                        ) as response:
                            return response.status == 200
                except:
                    return False
            
            # Check if Ollama is available
            try:
                loop = asyncio.get_event_loop()
                is_available = loop.run_until_complete(check_ollama())
            except:
                # No event loop, create one for the check
                is_available = asyncio.run(check_ollama())
            
            if is_available:
                self.clients[LLMProvider.OLLAMA] = OllamaClient(ollama_url, ollama_model)
                logger.info(f"Ollama client initialized successfully at {ollama_url}")
            else:
                logger.info(f"Ollama not available at {ollama_url} - skipping (this is optional)")
                
        except Exception as e:
            logger.info(f"Ollama not available: {e} - skipping (this is optional)")
        
        # Set default provider based on availability
        if LLMProvider.GEMINI in self.clients:
            self.default_provider = LLMProvider.GEMINI
        elif LLMProvider.OLLAMA in self.clients:
            self.default_provider = LLMProvider.OLLAMA
        else:
            logger.warning("No LLM providers available! Please configure at least one provider.")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]],
        provider: Optional[LLMProvider] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate response using specified or default provider"""
        
        # Use default provider if none specified
        if provider is None:
            provider = self.default_provider
        
        # Check if provider is available
        if provider not in self.clients:
            available = list(self.clients.keys())
            raise Exception(f"Provider {provider.value} not available. Available: {[p.value for p in available]}")
        
        client = self.clients[provider]
        
        try:
            response = await client.generate_response(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "response": response,
                "provider": provider.value,
                "tokens": len(response.split()),  # Rough estimate
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating response with {provider.value}: {e}")
            return {
                "response": f"Error: {str(e)}",
                "provider": provider.value,
                "tokens": 0,
                "success": False,
                "error": str(e)
            }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [provider.value for provider in self.clients.keys()]
    
    async def check_provider_health(self, provider: LLMProvider) -> bool:
        """Check if a provider is healthy"""
        if provider not in self.clients:
            return False
        
        try:
            # Simple test generation
            test_messages = [{"role": "user", "content": "Hello"}]
            result = await self.clients[provider].generate_response(test_messages, max_tokens=10)
            return bool(result and len(result.strip()) > 0)
        except:
            return False