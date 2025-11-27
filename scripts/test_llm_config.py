#!/usr/bin/env python3
"""Test script for LLM configuration.

Tests both OpenAI and Anthropic models to ensure configuration works.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from apps.agents.transactional.config import get_conversation_llm, get_llm
from apps.orchestrator.settings import settings


def test_current_llm():
    """Test currently configured LLM."""
    print("=" * 60)
    print("🧪 Testing Current LLM Configuration")
    print("=" * 60)
    print(
        f"Provider: {settings.LLM_MODEL.split(':')[0] if ':' in settings.LLM_MODEL else 'openai'}"
    )
    print(f"Model: {settings.LLM_MODEL}")
    print(f"Temperature: {settings.LLM_TEMPERATURE}")
    print()

    try:
        print("⏳ Initializing LLM...")
        llm = get_conversation_llm()
        print("✅ LLM initialized successfully!")
        print(f"   Model: {llm.__class__.__name__}")
        print()

        # Simple test
        print("⏳ Testing simple invocation...")
        response = llm.invoke("Di 'Hola' en una palabra")
        print(f"✅ Response: {response.content}")
        print()

        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        sys.exit(1)


def test_anthropic():
    """Test Anthropic model specifically."""
    print("\n" + "=" * 60)
    print("🧪 Testing Anthropic Model")
    print("=" * 60)

    try:
        llm = get_llm(provider="anthropic", model="claude-3-5-haiku-20241022", temperature=0.7)
        print("✅ Anthropic LLM initialized")

        response = llm.invoke("Di 'Hola' en una palabra")
        print(f"✅ Response: {response.content}")

    except Exception as e:
        print(f"❌ Anthropic test failed: {e}")


def test_openai():
    """Test OpenAI model specifically."""
    print("\n" + "=" * 60)
    print("🧪 Testing OpenAI Model")
    print("=" * 60)

    try:
        llm = get_llm(provider="openai", model="gpt-4o-mini", temperature=0.7)
        print("✅ OpenAI LLM initialized")

        response = llm.invoke("Say 'Hello' in one word")
        print(f"✅ Response: {response.content}")

    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")


if __name__ == "__main__":
    # Test current configuration
    test_current_llm()

    # Optionally test both providers
    if len(sys.argv) > 1 and sys.argv[1] == "--test-all":
        test_anthropic()
        test_openai()
