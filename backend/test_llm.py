# File: backend/test_llm.py
"""
Test script for LLM integration
Run this to test Gemini and Ollama connections
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.llm_service import LLMService, LLMProvider
from app.core.config import settings

async def test_gemini():
    """Test Google Gemini connection"""
    print("🧪 Testing Google Gemini...")
    
    if not settings.google_api_key:
        print("❌ GOOGLE_API_KEY not set in environment")
        return False
    
    try:
        from app.services.llm_service import GeminiClient
        client = GeminiClient(settings.google_api_key)
        
        messages = [
            {"role": "user", "content": "Say 'Gemini test successful' if you can read this"}
        ]
        
        response = await client.generate_response(messages, max_tokens=50)
        print(f"✅ Gemini Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return False

async def test_ollama():
    """Test Ollama connection"""
    print("\n🦙 Testing Ollama...")
    print("💡 Note: Ollama is optional and only used if available")
    
    try:
        from app.services.llm_service import OllamaClient
        client = OllamaClient(settings.ollama_url, settings.ollama_model)
        
        # Check health first
        is_healthy = await client._check_health()
        if not is_healthy:
            print("ℹ️  Ollama service not available at", settings.ollama_url)
            print("💡 This is optional! You can:")
            print("   • Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("   • Or use Docker: docker run -d -p 11434:11434 ollama/ollama")
            print("   • Or just use Gemini only")
            return False
        
        # List available models
        models = await client.list_models()
        print(f"📋 Available models: {models}")
        
        if not models:
            print("⚠️  No models installed in Ollama")
            print(f"💡 Install a model: ollama pull {settings.ollama_model}")
            return False
        
        if settings.ollama_model not in [m.split(':')[0] for m in models]:
            print(f"⚠️  Model '{settings.ollama_model}' not found")
            print(f"💡 Install model: ollama pull {settings.ollama_model}")
            print(f"📋 Available: {models}")
            return False
        
        # Test generation
        messages = [
            {"role": "user", "content": "Say 'Ollama test successful' if you can read this"}
        ]
        
        response = await client.generate_response(messages, max_tokens=50)
        print(f"✅ Ollama Response: {response}")
        return True
        
    except Exception as e:
        print(f"ℹ️  Ollama not available: {e}")
        print("💡 This is optional - system works fine with just Gemini!")
        return False

async def test_llm_service():
    """Test the unified LLM service"""
    print("\n🔧 Testing LLM Service...")
    
    try:
        llm_service = LLMService()
        providers = llm_service.get_available_providers()
        
        print(f"📡 Available providers: {providers}")
        
        if not providers:
            print("❌ No LLM providers available!")
            return False
        
        # Test each provider
        for provider_name in providers:
            print(f"\n🧪 Testing provider: {provider_name}")
            
            try:
                provider = LLMProvider(provider_name)
                result = await llm_service.generate_response(
                    messages=[{"role": "user", "content": f"Say '{provider_name} via LLMService works!'"}],
                    provider=provider,
                    max_tokens=50
                )
                
                if result["success"]:
                    print(f"✅ {provider_name}: {result['response']}")
                else:
                    print(f"❌ {provider_name}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ {provider_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Service Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 RagFlow LLM Integration Test")
    print("=" * 50)
    
    # Show configuration
    print("⚙️  Configuration:")
    print(f"   Gemini API Key: {'✅ Set' if settings.google_api_key else '❌ Not set'}")
    print(f"   Ollama URL: {settings.ollama_url}")
    print(f"   Ollama Model: {settings.ollama_model}")
    print()
    
    # Run tests
    gemini_ok = await test_gemini()
    ollama_ok = await test_ollama()
    service_ok = await test_llm_service()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    print(f"Gemini:      {'✅ PASS' if gemini_ok else '❌ FAIL'}")
    print(f"Ollama:      {'✅ PASS' if ollama_ok else '❌ FAIL'}")
    print(f"LLM Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    
    if gemini_ok or ollama_ok:
        print("\n🎉 LLM system is ready!")
        if gemini_ok and ollama_ok:
            print("Both Gemini and Ollama are working!")
        elif gemini_ok:
            print("Gemini is working! (Ollama is optional and can be added later)")
        else:
            print("Ollama is working! (Consider adding Gemini for cloud backup)")
        print("Ready to implement RAG functionality.")
    else:
        print("\n⚠️  No LLM providers are working.")
        print("Please configure at least one provider:")
        print("• Gemini: Set GOOGLE_API_KEY in .env")
        print("• Ollama: Install and run Ollama locally")

if __name__ == "__main__":
    # Set environment variables if .env file exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    asyncio.run(main())