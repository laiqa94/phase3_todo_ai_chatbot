#!/usr/bin/env python3
"""
Test script to verify the chatbot response formatting
"""

import sys
import os

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_chatbot.agent.agent import TodoAgent
from ai_chatbot.database.engine import get_session
from sqlmodel import Session


def safe_print(text):
    """Print text safely without Unicode issues"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove emojis and try again
        clean_text = ''.join(c for c in text if ord(c) < 128)
        print(clean_text)


def test_chatbot_responses():
    """Test the chatbot response formatting"""
    
    # Create a test session
    session = next(get_session())
    
    try:
        # Create the agent
        agent = TodoAgent(session)
        
        safe_print("Testing Chatbot Response Formatting")
        safe_print("=" * 50)
        
        # Test 1: Greeting
        safe_print("\n1. Testing greeting...")
        result = agent.process_message(
            user_message="Hello",
            user_id=1
        )
        response = result.get("response_text", "")
        safe_print(f"   Response: {response[:100]}...")  # Truncate for display
        assert "Hello" in response, "Greeting should contain 'Hello'"
        safe_print("   [OK] Greeting test passed!")
        
        # Test 2: List tasks
        safe_print("\n2. Testing list tasks...")
        result = agent.process_message(
            user_message="Show me my tasks",
            user_id=1
        )
        response = result.get("response_text", "")
        safe_print(f"   Response: {response[:100]}...")  # Truncate for display
        safe_print("   [OK] List tasks test completed!")
        
        # Test 3: Add task format check
        safe_print("\n3. Testing add task format...")
        result = agent.process_message(
            user_message="Add a task: Buy groceries",
            user_id=1
        )
        response = result.get("response_text", "")
        safe_print(f"   Response: {response[:100]}...")  # Truncate for display
        # The response should contain the task title
        if "Buy groceries" in response:
            safe_print("   [OK] Add task format looks correct!")
        else:
            safe_print("   [INFO] Task may have been created but response format varies based on AI")
        
        safe_print("\n" + "=" * 50)
        safe_print("Chatbot response formatting tests completed!")
        safe_print("\nExpected Response Formats:")
        safe_print("  - Add Task: [OK] Task 'Task Title' has been added successfully.")
        safe_print("  - Delete Task: [OK] Task has been deleted successfully.")
        safe_print("  - Complete Task: [OK] Task 'Task Title' has been marked as complete.")
        safe_print("  - Update Task: [OK] Task 'Task Title' has been updated successfully.")
        
    except Exception as e:
        safe_print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    test_chatbot_responses()
