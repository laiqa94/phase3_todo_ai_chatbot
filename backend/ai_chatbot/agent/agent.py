"""
AI Agent for Todo Chatbot
Integrates with Cohere to provide task management capabilities
"""

from typing import List, Dict, Any, Optional
from sqlmodel import Session
from .cohere_provider import CohereProvider
from ..tools import TOOLS_REGISTRY
from ..database.repositories import TaskRepository, ConversationRepository, MessageRepository, UserRepository


class TodoAgent:
    """AI Agent for Todo Chatbot with Cohere integration"""

    def __init__(self, session: Session):
        self.session = session
        self.provider = CohereProvider()
        self.tools_registry = TOOLS_REGISTRY
        self.task_repo = TaskRepository(session)
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)
        self.user_repo = UserRepository(session)

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions in Cohere-compatible format"""
        tools = []
        for tool_name, tool_class in self.tools_registry.items():
            tool_def = {
                "name": tool_class.name(),
                "description": tool_class.description(),
                "parameter_definitions": {}
            }

            # Get parameters from the tool's schema
            params_schema = tool_class.parameters()
            for param_name, param_details in params_schema.get("properties", {}).items():
                # Map JSON schema types to Cohere types
                json_type = param_details.get("type", "string")
                cohere_type = "str" if json_type == "string" else json_type

                tool_def["parameter_definitions"][param_name] = {
                    "type": cohere_type,
                    "required": param_name in params_schema.get("required", []),
                    "description": param_details.get("description", "")
                }

            tools.append(tool_def)

        return tools

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool with given arguments"""
        if tool_name not in self.tools_registry:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "message": f"Unknown tool: {tool_name}"
            }

        tool_class = self.tools_registry[tool_name]

        try:
            result = tool_class.execute(tool_args, self.session)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Tool execution failed: {str(e)}"
            }

    def _format_system_prompt(self) -> str:
        """Format the system prompt for the agent"""
        return """
        You are a helpful and intelligent AI assistant for a todo application. You help users manage their tasks efficiently.
        
        SUPPORTED LANGUAGES: English, Hindi, Hinglish (Hindi-English mix), Roman Urdu (Urdu written in Latin script)
        You can understand and respond in any of these languages based on the user's preference.
        Examples of Roman Urdu:
        - "mujhe ek task add karna hai" = "I want to add a task"
        - "mera kaam dikhao" = "show me my work/tasks"
        - "task complete karo" = "complete the task"
        - "task delete karo" = "delete the task"
        - "mera profile dikhao" = "show my profile"

        PERSONALITY:
        - Be friendly, professional, and encouraging
        - Use a conversational tone
        - Show enthusiasm when helping with tasks
        - Be patient and understanding
        - Support multi-language communication
        - Always respond in the same language the user uses

        CORE RESPONSIBILITIES:
        1. Help users create, view, update, and manage their tasks
        2. Provide clear confirmations for all actions
        3. Ask clarifying questions when requests are unclear
        4. Give helpful suggestions for task management
        5. Understand and respond in user's preferred language
        6. Provide user account information when asked

        AVAILABLE TOOLS (use when appropriate):
        - add_task: Create new tasks with title, description, priority, due date
        - list_tasks: Show user's tasks (all, completed, or pending)
        - complete_task: Mark tasks as done or undone
        - update_task: Modify existing task details
        - delete_task: Remove tasks from the list
        - get_user_info: Get the current user's profile information

        LANGUAGE KEYWORDS:
        
        ENGLISH Keywords:
        - Add task: "add task", "create task", "make new task", "new task"
        - View tasks: "show tasks", "list tasks", "my tasks", "view tasks"
        - Complete: "complete task", "mark done", "finished task"
        - Delete: "delete task", "remove task", "cancel task"
        - Update: "update task", "edit task", "change task"
        - User info: "my profile", "my account", "who am i"
        
        HINDI Keywords:
        - Add task: "nayi task banao", "ek kaam add karo", "task add karo"
        - View tasks: "mera kaam dikha do", "tasks dikhao", "mere pending kaam batao"
        - Complete: "complete karo", "ho gaya", "karte ho"
        - Delete: "hatao", "nikalo", "delete karo"
        - Update: "badlo", "change karo", "sudharo"
        - User info: "mera profile", "mera account", "mera info"
        
        ROMAN URDU Keywords:
        - Add task: "task add karo", "nayi task", "kaam add karo", "task banao", "task create karo"
        - View tasks: "mera kaam dikhao", "tasks dikhao", "meri tasks", "tasks show karo"
        - Complete: "task complete karo", "task khatam karo", "task ho gaya", "task done karo"
        - Delete: "task hatao", "task delete karo", "task nikalo", "task mitado"
        - Update: "task update karo", "task change karo", "task edit karo", "task badlo"
        - User info: "mera profile", "mera account", "meri info", "who am i", "mera info batao"

        RESPONSE GUIDELINES:
        - Always acknowledge what the user wants to do
        - Use tools when users mention specific task actions
        - Provide helpful context and next steps in user's language
        - If unsure, ask for clarification politely
        - Celebrate completed tasks with positive reinforcement
        - Suggest productivity tips when appropriate
        - When user asks about their profile/account, provide helpful information
        - Always respond in the SAME LANGUAGE the user uses
        
        TASK RESPONSE FORMAT (always use these exact formats after completing an action):
        - When adding a task: "✅ Task 'Task Title' has been added successfully."
        - When deleting a task: "✅ Task has been deleted successfully."
        - When completing a task: "✅ Task 'Task Title' has been marked as complete."
        - When updating a task: "✅ Task 'Task Title' has been updated successfully."
        
        EXAMPLES OF GOOD RESPONSES:
        - English: "I'd be happy to help you add that task! Let me create it for you."
        - Hindi: "Mit bhaari! वह task complete हो गया! अगला क्या करें?"
        - Hinglish: "Bilkul! Main vo task delete kar dunga!"
        - Roman Urdu: "Khayal rakho! Main aapki task add kar raha hoon!"
        
        Remember: You're here to make task management easier and more enjoyable for users! Always try to understand the user's intent even if they use mixed languages or non-standard phrases.
        """

    def process_message(self,
                       user_message: str,
                       user_id: int,
                       conversation_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a user message and return AI response

        Args:
            user_message: The message from the user
            user_id: ID of the authenticated user
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary with AI response and any tool executions
        """
        try:
            # Build conversation context
            messages = [{"role": "system", "content": self._format_system_prompt()}]

            # If there's an existing conversation, fetch recent messages
            if conversation_id:
                recent_messages = self.message_repo.get_latest_messages(conversation_id, limit=10)
                for msg in reversed(recent_messages):  # Add in chronological order
                    messages.append({
                        "role": "user" if msg.role == "user" else "assistant",
                        "content": msg.content
                    })

            # Add the current user message
            messages.append({"role": "user", "content": user_message})

            # Get tool definitions
            tools = self._get_tool_definitions()

            # Call Cohere API
            response = self.provider.chat(messages, tools=tools)

            # Check if there are tool calls in the response
            tool_results = []
            if "tool_calls" in response and response["tool_calls"]:
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("parameters", {})

                    # Ensure user_id is included in tool arguments
                    if "user_id" not in tool_args:
                        tool_args["user_id"] = user_id

                    # Execute the tool
                    result = self._execute_tool(tool_name, tool_args)
                    tool_results.append({
                        "tool_name": tool_name,
                        "result": result,
                        "arguments": tool_args
                    })

            # Get the response text from the provider
            response_text = response.get("text", "")

            # Enhance response with tool results data
            enhanced_response = response_text
            for tool_result in tool_results:
                tool_name = tool_result.get("tool_name", "")
                result = tool_result.get("result", {})
                
                # For list_tasks, include the actual task data
                if tool_name == "list_tasks" and result.get("success"):
                    tasks = result.get("tasks", [])
                    if tasks:
                        enhanced_response += "\n\nHere are your tasks:\n"
                        for task in tasks:
                            status = "[Done]" if task.get("completed") else "[Pending]"
                            priority = task.get("priority", "medium")
                            enhanced_response += f"  {status} Task {task.get('id')}: {task.get('title')} (Priority: {priority})\n"
                    else:
                        enhanced_response += "\n\nYou don't have any tasks yet."
                
                # For add_task, use the user's specific format
                elif tool_name == "add_task" and result.get("success"):
                    enhanced_response = f"✅ Task '{result.get('title')}' has been added successfully."
                
                # For complete_task, use the user's specific format
                elif tool_name == "complete_task" and result.get("success"):
                    enhanced_response = f"✅ Task '{result.get('title')}' has been marked as complete."
                
                # For delete_task, use the user's specific format
                elif tool_name == "delete_task" and result.get("success"):
                    enhanced_response = f"✅ Task has been deleted successfully."
                
                # For get_user_info, include user profile information
                elif tool_name == "get_user_info" and result.get("success"):
                    username = result.get('username', 'N/A')
                    email = result.get('email', 'N/A')
                    full_name = result.get('full_name', '')
                    name_display = full_name if full_name else username
                    enhanced_response = f"\n👤 **User Profile**\n"
                    enhanced_response += f"━━━━━━━━━━━━━━━━\n"
                    enhanced_response += f"📛 Name: {name_display}\n"
                    enhanced_response += f"📧 Email: {email}\n"
                    enhanced_response += f"🆔 User ID: {result.get('user_id', 'N/A')}\n"
                    enhanced_response += f"━━━━━━━━━━━━━━━━"
                
                # For update_task, use the user's specific format
                elif tool_name == "update_task" and result.get("success"):
                    updated_fields = result.get('updated_fields', [])
                    if updated_fields:
                        enhanced_response = f"✅ Task '{result.get('title')}' has been updated successfully."
                    else:
                        enhanced_response = f"✅ Task '{result.get('title')}' has been updated."

            # Ensure we always have a non-empty response
            if not enhanced_response or enhanced_response.strip() == "":
                if user_message.lower() in ['hello', 'hi', 'hey']:
                    enhanced_response = "Hello! I'm your AI assistant. How can I help you with your tasks today?"
                else:
                    enhanced_response = "I received your message. How can I help you with your tasks?"

            # Format the final response
            final_response = {
                "response_text": enhanced_response,
                "tool_results": tool_results,
                "has_tools_executed": len(tool_results) > 0,
                "user_id": user_id,
                "conversation_id": conversation_id or 1  # Ensure conversation_id is not None
            }

            return final_response

        except Exception as e:
            # Ensure we always return a proper response even if an error occurs
            error_response = f"I'm sorry, I encountered an error: {str(e)}"

            # If this is related to a greeting, respond appropriately
            if user_message and any(greeting in user_message.lower() for greeting in ['hello', 'hi', 'hey']):
                error_response = "Hello! I'm your AI assistant. How can I help you with your tasks today?"
            elif not user_message or user_message.strip() == "":
                error_response = "Hi there! Please let me know how I can help you with your tasks."

            return {
                "response_text": error_response,
                "tool_results": [],
                "has_tools_executed": False,
                "conversation_id": 1,  # Ensure conversation_id is always present
                "error": str(e)
            }

    def run_conversation(self,
                        user_message: str,
                        user_id: int,
                        conversation_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a complete conversation cycle with conversation management

        Args:
            user_message: The message from the user
            user_id: ID of the authenticated user
            conversation_title: Optional title for new conversation

        Returns:
            Dictionary with complete conversation response
        """
        # Create or retrieve conversation
        if not conversation_title:
            conversation_title = f"Conversation with {user_message[:30]}..."

        conversation = self.conversation_repo.create_conversation(
            conversation_create={"title": conversation_title},
            user_id=user_id
        )

        # Process the message
        result = self.process_message(user_message, user_id, conversation.id)

        # Store the messages in the database
        from ..database.models import MessageCreate

        # Save user message
        user_msg = MessageCreate(
            role="user",
            content=user_message,
            conversation_id=conversation.id
        )
        self.message_repo.create_message(user_msg)

        # Save AI response
        ai_response_content = result["response_text"]
        if result["tool_results"]:
            # Include tool execution results in the response
            tool_result_texts = [f"{tr['tool_name']}({tr['arguments']}): {tr['result'].get('message', '')}"
                               for tr in result["tool_results"]]
            ai_response_content += "\n\nTool Results: " + "; ".join(tool_result_texts)

        ai_msg = MessageCreate(
            role="assistant",
            content=ai_response_content,
            conversation_id=conversation.id
        )
        self.message_repo.create_message(ai_msg)

        # Add conversation info to result
        result["conversation_id"] = conversation.id
        result["conversation_title"] = conversation.title

        return result