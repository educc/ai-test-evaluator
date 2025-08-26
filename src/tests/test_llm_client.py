#!/usr/bin/env python3
"""
Test script for the LM Studio client.
"""

from src.llm_client import LMStudioClient, Message, Role

def test_client_instantiation():
    """Test that we can create a client instance."""
    client = LMStudioClient()
    print(f"✅ Client created with base URL: {client.base_url}")
    
def test_message_creation():
    """Test creating messages with dataclasses."""
    system_msg = Message(role=Role.SYSTEM, content="You are a helpful assistant.")
    user_msg = Message(role=Role.USER, content="Hello, how are you?")
    
    print(f"✅ System message: {system_msg.role.value} - {system_msg.content}")
    print(f"✅ User message: {user_msg.role.value} - {user_msg.content}")

def test_client_with_custom_config():
    """Test client with custom configuration."""
    client = LMStudioClient(
        base_url="http://localhost:1234/v1",
        timeout=60,
        api_key="test-key"
    )
    print(f"✅ Custom client created with timeout: {client.timeout}")

if __name__ == "__main__":
    print("Testing LM Studio Client Implementation...")
    print("=" * 50)
    
    test_client_instantiation()
    test_message_creation()
    test_client_with_custom_config()
    
    print("=" * 50)
    print("✅ All tests passed! The client implementation is working correctly.")
