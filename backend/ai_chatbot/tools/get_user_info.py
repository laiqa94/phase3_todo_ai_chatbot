"""
MCP tool for getting user information
Implements the get_user_info functionality for the AI agent
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from ..database.repositories import UserRepository
from sqlmodel import Session


class GetUserInfoInput(BaseModel):
    """Input schema for get_user_info tool"""
    user_id: int = Field(..., description="ID of the user to get information for")


class GetUserInfoTool:
    """MCP Tool for getting user information"""

    @staticmethod
    def name() -> str:
        return "get_user_info"

    @staticmethod
    def description() -> str:
        return "Get the current user's profile information"

    @staticmethod
    def parameters() -> Dict[str, Any]:
        return GetUserInfoInput.schema()

    @staticmethod
    def execute(input_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
        """
        Execute the get_user_info operation

        Args:
            input_data: Dictionary containing user_id
            session: Database session

        Returns:
            Dictionary with user information
        """
        try:
            # Validate input
            params = GetUserInfoInput(**input_data)

            # Create user repository
            user_repo = UserRepository(session)

            # Get user by ID
            user = user_repo.get_user_by_id(params.user_id)

            if user:
                return {
                    "success": True,
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name if hasattr(user, 'full_name') else None,
                    "is_active": user.is_active if hasattr(user, 'is_active') else True,
                    "message": f"User '{user.username}' information retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"User with ID {params.user_id} not found"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve user information. Please try again."
            }
