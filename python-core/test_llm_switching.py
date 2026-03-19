#!/usr/bin/env python3
"""
Test script for LLM switching functionality.

This script demonstrates how to switch between different LLM providers
(OpenAI, DeepSeek, Doubao) in the Smart Ticket System.
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_factory import LLMFactory
from app.config import LLMProvider


def test_llm_creation():
    """Test creating LLM instances for different providers."""
    print("Testing LLM Factory...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test 1: Default LLM (from environment)
    print("\n1. Testing default LLM (from environment):")
    try:
        llm = LLMFactory.get_default_llm()
        print(f"   Successfully created default LLM")
        print(f"   Provider: {os.getenv('LLM_PROVIDER', 'openai')}")
        print(f"   Model: {llm.model_name}")
    except Exception as e:
        print(f"   Error creating default LLM: {e}")
    
    # Test 2: OpenAI LLM
    print("\n2. Testing OpenAI LLM:")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            llm = LLMFactory.create_llm(
                provider=LLMProvider.OPENAI,
                api_key=openai_key,
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                temperature=0
            )
            print(f"   Successfully created OpenAI LLM")
            print(f"   Model: {llm.model_name}")
        except Exception as e:
            print(f"   Error creating OpenAI LLM: {e}")
    else:
        print("   OpenAI API key not found in environment")
    
    # Test 3: DeepSeek LLM
    print("\n3. Testing DeepSeek LLM:")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        try:
            llm = LLMFactory.create_llm(
                provider=LLMProvider.DEEPSEEK,
                api_key=deepseek_key,
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                temperature=0
            )
            print(f"   Successfully created DeepSeek LLM")
            print(f"   Model: {llm.model_name}")
            print(f"   Base URL: {llm.base_url}")
        except Exception as e:
            print(f"   Error creating DeepSeek LLM: {e}")
    else:
        print("   DeepSeek API key not found in environment")
    
    # Test 4: Doubao LLM
    print("\n4. Testing Doubao LLM:")
    doubao_key = os.getenv("DOUBAO_API_KEY")
    if doubao_key:
        try:
            llm = LLMFactory.create_llm(
                provider=LLMProvider.DOUBAO,
                api_key=doubao_key,
                model=os.getenv("DOUBAO_MODEL", "Doubao-pro-32k"),
                temperature=0
            )
            print(f"   Successfully created Doubao LLM")
            print(f"   Model: {llm.model_name}")
            print(f"   Base URL: {llm.base_url}")
        except Exception as e:
            print(f"   Error creating Doubao LLM: {e}")
    else:
        print("   Doubao API key not found in environment")
    
    print("\n" + "=" * 50)
    print("LLM Factory test completed!")


def test_intent_recognition():
    """Test intent recognition with different LLM providers."""
    print("\n\nTesting Intent Recognition with different LLMs...")
    print("=" * 50)
    
    from app.services.intent_recognition import IntentRecognitionService
    
    # Test messages
    test_messages = [
        "我的订单ORD001到哪了？",
        "帮我催一下订单ORD002",
        "我想取消订单ORD003",
    ]
    
    # Create service instance
    service = IntentRecognitionService()
    
    for message in test_messages:
        print(f"\nTesting message: '{message}'")
        try:
            result = service.recognize(message)
            print(f"  Intent: {result.intent.value}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Order ID: {result.entities.order_id}")
            print(f"  Needs clarification: {result.needs_clarification}")
        except Exception as e:
            print(f"  Error: {e}")


def main():
    """Main test function."""
    print("Smart Ticket System - LLM Switching Test")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        print(f"Warning: .env file not found at {env_file}")
        print("Please copy .env.example to .env and configure your API keys")
        print("Using environment variables if available...")
    
    # Run tests
    test_llm_creation()
    test_intent_recognition()
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("\nTo switch LLM providers, set the LLM_PROVIDER environment variable:")
    print("  - LLM_PROVIDER=openai (default)")
    print("  - LLM_PROVIDER=deepseek")
    print("  - LLM_PROVIDER=doubao")
    print("\nMake sure to set the corresponding API keys:")
    print("  - OPENAI_API_KEY for OpenAI")
    print("  - DEEPSEEK_API_KEY for DeepSeek")
    print("  - DOUBAO_API_KEY for Doubao")


if __name__ == "__main__":
    main()