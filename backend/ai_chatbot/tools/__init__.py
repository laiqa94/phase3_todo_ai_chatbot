"""
Tools registry for AI Todo Chatbot
"""

from .add_task import AddTaskTool
from .list_tasks import ListTasksTool
from .complete_task import CompleteTaskTool
from .delete_task import DeleteTaskTool
from .update_task import UpdateTaskTool
from .get_user_info import GetUserInfoTool

# Registry of all available tools
TOOLS_REGISTRY = {
    AddTaskTool.name(): AddTaskTool,
    ListTasksTool.name(): ListTasksTool,
    CompleteTaskTool.name(): CompleteTaskTool,
    DeleteTaskTool.name(): DeleteTaskTool,
    UpdateTaskTool.name(): UpdateTaskTool,
    GetUserInfoTool.name(): GetUserInfoTool,
}

__all__ = [
    'AddTaskTool',
    'ListTasksTool',
    'CompleteTaskTool',
    'DeleteTaskTool',
    'UpdateTaskTool',
    'GetUserInfoTool',
    'TOOLS_REGISTRY'
]