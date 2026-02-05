"""
Cohere AI Provider for AI Todo Chatbot
Handles communication with Cohere API
"""

import cohere
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..config import config


class CohereProvider:
    """Provider class for Cohere API integration"""

    def __init__(self):
        if not config.COHERE_API_KEY or config.COHERE_API_KEY == "your-cohere-api-key-here":
            # In development mode, set client to None to indicate we're using mock mode
            self.client = None
        else:
            self.client = cohere.Client(config.COHERE_API_KEY)

        self.model = config.COHERE_MODEL

    def chat(self,
             messages: List[Dict[str, str]],
             tools: Optional[List[Dict[str, Any]]] = None,
             temperature: float = 0.7) -> Dict[str, Any]:
        """
        Send chat request to Cohere API

        Args:
            messages: List of message dictionaries with 'role' and 'message' keys
            tools: Optional list of tool definitions
            temperature: Temperature for response creativity

        Returns:
            Response dictionary from Cohere API
        """
        # Check if we're in development mode with mock API key
        if not config.COHERE_API_KEY or config.COHERE_API_KEY == "your-cohere-api-key-here" or config.COHERE_API_KEY == "":
            # Return enhanced mock response for development
            import random
            user_message = messages[-1]["content"].strip().lower()
            original_message = messages[-1]["content"]

            # Enhanced rule-based responses with variations
            import time
            import hashlib
            
            # Create unique seed based on message content and timestamp
            message_hash = hashlib.md5(user_message.encode()).hexdigest()[:8]
            unique_seed = int(time.time() * 1000) + int(message_hash, 16)
            random.seed(unique_seed)
            
            if any(greeting in user_message for greeting in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
                responses = [
                    "Hello! 👋 I'm your personal task assistant. I'm here to help you stay organized and productive. What can I help you with today?",
                    "Hi there! 😊 Great to see you! I'm ready to help you manage your tasks and get things done. What's on your mind?",
                    "Hey! 🌟 Welcome back! I'm excited to help you tackle your to-do list. What would you like to work on?",
                    "Good to see you! 👋 I'm your AI task manager, here to make your life easier. How can I assist you today?",
                    "Hello! 🎯 Ready to boost your productivity? I can help you add, organize, and complete your tasks. What shall we start with?",
                    "Welcome! 🎆 I'm thrilled to help you get organized. What tasks are we working on today?",
                    "Hi! 💪 Let's make today productive together! How can I help with your task management?",
                    "Greetings! 🌈 I'm your friendly task assistant. Ready to help you achieve your goals!"
                ]
                response_text = random.choice(responses) + f" [ID: {random.randint(1000,9999)}]"
            elif any(word in user_message for word in ["help", "what can you do", "assist", "capabilities"]):
                responses = [
                    "I'm your personal task management assistant! 📝 I can help you:\n\n✅ Add new tasks with details\n📋 View your task list\n✔️ Mark tasks as complete\n✏️ Update task information\n🗑️ Delete tasks you no longer need\n\nJust tell me what you'd like to do in natural language!",
                    "Great question! I'm here to make task management effortless for you. I can:\n\n• Create new tasks with priorities and due dates\n• Show you all your tasks or filter by status\n• Help you complete tasks and celebrate your progress\n• Update task details when things change\n• Remove tasks you no longer need\n\nTry saying something like 'Add a task to call mom' or 'Show me my pending tasks'!",
                    "I'm your productivity partner! 🚀 Here's how I can help:\n\n📌 Create tasks: 'Add a task to buy groceries'\n📊 View tasks: 'Show me my tasks'\n✅ Complete tasks: 'Mark task 1 as done'\n📝 Update tasks: 'Change the due date for task 2'\n🗑️ Delete tasks: 'Remove task 3'\n\nWhat would you like to start with?"
                ]
                response_text = random.choice(responses)
            elif any(action in user_message for action in ["add", "create", "make", "new"]) and any(word in user_message for word in ["task", "todo", "item"]):
                responses = [
                    "Absolutely! I'd love to help you add a new task. 📝 What task would you like me to create for you? You can include details like priority or due date if you'd like!",
                    "Perfect! Let's get that task added to your list. ✨ What's the task you want to create? Feel free to give me as much detail as you want!",
                    "Great idea to add a new task! 🎯 Tell me what you need to get done, and I'll add it to your list right away.",
                    "I'm excited to help you stay organized! 📋 What new task should I add for you? Don't forget to mention if it's urgent or has a deadline!"
                ]
                response_text = random.choice(responses)
            elif any(word in user_message for word in ["list", "show", "display", "view", "my tasks", "all tasks", "tasks"]):
                responses = [
                    "I'd be happy to show you your tasks! 📋 Let me fetch your current list for you. This will help you see what needs to be done.",
                    "Great! Let me pull up your task list so you can see everything you have planned. 📊 This is a great way to stay on top of things!",
                    "Perfect timing to review your tasks! 🎯 I'll show you what's on your plate so you can prioritize your day.",
                    "Excellent! Checking your tasks regularly is a great productivity habit. 📝 Let me get your current list for you."
                ]
                response_text = random.choice(responses)
            elif any(word in user_message for word in ["complete", "done", "finish", "finished", "completed"]):
                responses = [
                    "Fantastic! 🎉 Completing tasks feels great, doesn't it? Which task have you finished? I'll mark it as complete for you!",
                    "Awesome work! ✅ I love helping people celebrate their accomplishments. Tell me which task you've completed!",
                    "Way to go! 🌟 Getting things done is so satisfying. Which task should I mark as complete?",
                    "Excellent! 🎊 You're making great progress. Let me know which task you've finished so I can update it for you!"
                ]
                response_text = random.choice(responses)
            elif any(word in user_message for word in ["update", "change", "modify", "edit", "alter"]):
                responses = [
                    "Of course! 📝 Things change, and I'm here to help you keep your tasks up to date. Which task would you like to modify and what changes should I make?",
                    "No problem! ✏️ Flexibility is key to good task management. Tell me which task needs updating and what you'd like to change.",
                    "Absolutely! 🔄 I can help you update any task details. Which task should I modify, and what changes do you need?"
                ]
                response_text = random.choice(responses)
            elif any(word in user_message for word in ["delete", "remove", "cancel", "eliminate"]):
                responses = [
                    "Sure thing! 🗑️ Sometimes we need to clean up our task list. Which task would you like me to remove for you?",
                    "No problem! ✨ Keeping your task list clean and relevant is important. Tell me which task should be deleted.",
                    "I can help with that! 🧹 Which task is no longer needed? I'll remove it from your list right away."
                ]
                response_text = random.choice(responses)
            else:
                # More encouraging and helpful general responses
                responses = [
                    f"I understand you said: '{original_message}' 💭 I'm here to help you manage your tasks effectively! You can ask me to add, view, complete, update, or delete tasks. What would you like to do?",
                    f"Thanks for your message: '{original_message}' 😊 I'm your task management assistant! I can help you stay organized and productive. What task-related help do you need?",
                    f"Got it: '{original_message}' 🎯 I'm ready to help you with your tasks! Whether you want to add something new, check your list, or update existing tasks, just let me know!",
                    f"I received: '{original_message}' 📝 I'm here to make task management easy for you! Try asking me to create a task, show your list, or mark something as complete. How can I help?"
                ]
                response_text = random.choice(responses)

            # Ensure we always return a non-empty response
            if not response_text or response_text.strip() == "":
                response_text = "I'm your AI assistant for task management. How can I help you today?"

            return {
                "text": response_text,
                "finish_reason": "COMPLETE",
                "tool_calls": [],  # No tool calls in mock mode
                "meta": {"development_mode": True}
            }

        # Convert messages to Cohere format
        chat_history = []
        for msg in messages:
            role = "USER" if msg["role"] == "user" else "CHATBOT"
            chat_history.append({
                "user_name": role,
                "text": msg["content"]
            })

        # Prepare the request
        kwargs = {
            "message": messages[-1]["content"],  # Last message is the current prompt
            "chat_history": chat_history[:-1],  # All previous messages as history
            "model": self.model,
            "temperature": temperature,
        }

        # Add tools if provided
        if tools:
            kwargs["tools"] = tools

        try:
            response = self.client.chat(**kwargs)
            return {
                "text": response.text,
                "finish_reason": getattr(response, 'finish_reason', 'COMPLETE'),
                "tool_calls": getattr(response, 'tool_calls', []),
                "meta": getattr(response, 'meta', {})
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": "Sorry, I encountered an error processing your request. Please try again.",
                "finish_reason": "ERROR"
            }

    def generate(self,
                 prompt: str,
                 max_tokens: int = 300,
                 temperature: float = 0.7) -> str:
        """
        Generate text using Cohere's generate endpoint

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response creativity

        Returns:
            Generated text
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.generations[0].text if response.generations else ""
        except Exception as e:
            return f"Error generating response: {str(e)}"