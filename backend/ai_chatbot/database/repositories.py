"""
Repository classes for AI Todo Chatbot database operations
Provides data access layer for Task, Conversation, and Message entities
"""

from typing import List, Optional
from sqlmodel import select, Session, func
from .models import (
    Task, TaskCreate, TaskUpdate,
    Conversation, ConversationCreate,
    Message, MessageCreate,
    User
)


class TaskRepository:
    """Repository for Task operations with user isolation"""

    def __init__(self, session: Session):
        self.session = session

    def create_task(self, task_create: TaskCreate, user_id: int) -> Task:
        """Create a new task for a specific user"""
        task = Task(**task_create.dict(), user_id=user_id)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_task_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a specific task by ID for a specific user (enforces user isolation)"""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return self.session.exec(statement).first()

    def get_tasks_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Task]:
        """Get all tasks for a specific user with optional filtering"""
        statement = select(Task).where(Task.user_id == user_id)

        if status == "completed":
            statement = statement.where(Task.completed == True)
        elif status == "pending":
            statement = statement.where(Task.completed == False)

        statement = statement.offset(skip).limit(limit).order_by(Task.created_at.desc())
        return self.session.exec(statement).all()

    def update_task(self, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[Task]:
        """Update a specific task for a specific user"""
        task = self.get_task_by_id(task_id, user_id)
        if task:
            update_data = task_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(task, key, value)
            task.updated_at = func.now()  # type: ignore
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
        return task

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete a specific task for a specific user"""
        task = self.get_task_by_id(task_id, user_id)
        if task:
            self.session.delete(task)
            self.session.commit()
            return True
        return False

    def complete_task(self, task_id: int, user_id: int, completed: bool = True) -> Optional[Task]:
        """Mark a specific task as completed/incompleted for a specific user"""
        task = self.get_task_by_id(task_id, user_id)
        if task:
            task.completed = completed
            task.updated_at = func.now()  # type: ignore
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
        return task


class ConversationRepository:
    """Repository for Conversation operations with user isolation"""

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, conversation_create: ConversationCreate, user_id: int) -> Conversation:
        """Create a new conversation for a specific user"""
        conversation = Conversation(**conversation_create.dict(), user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Get a specific conversation by ID for a specific user (enforces user isolation)"""
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_conversations_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """Get all conversations for a specific user"""
        statement = select(Conversation).where(Conversation.user_id == user_id)
        statement = statement.offset(skip).limit(limit).order_by(Conversation.created_at.desc())
        return self.session.exec(statement).all()


class MessageRepository:
    """Repository for Message operations"""

    def __init__(self, session: Session):
        self.session = session

    def create_message(self, message_create: MessageCreate) -> Message:
        """Create a new message in a conversation"""
        message = Message(**message_create.dict())
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages_by_conversation(self, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get all messages for a specific conversation"""
        statement = select(Message).where(Message.conversation_id == conversation_id)
        statement = statement.offset(skip).limit(limit).order_by(Message.created_at.asc())
        return self.session.exec(statement).all()

    def get_latest_messages(self, conversation_id: int, limit: int = 10) -> List[Message]:
        """Get the latest messages for a specific conversation"""
        statement = select(Message).where(Message.conversation_id == conversation_id)
        statement = statement.order_by(Message.created_at.desc()).limit(limit)
        return self.session.exec(statement).all()


class UserRepository:
    """Repository for User operations"""

    def __init__(self, session: Session):
        self.session = session

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a specific user by ID"""
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a specific user by email"""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a specific user by username"""
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()