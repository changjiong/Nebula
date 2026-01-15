"""
Permission Control Utilities

Provides functions for checking user permissions against Tool/Skill visibility settings.
"""

from typing import Any

from app.models import User, Tool, Skill


def check_tool_permission(user: User | None, tool: Tool) -> bool:
    """
    Check if a user has permission to access a tool.

    Permission rules:
    1. Superusers can access all tools
    2. Public tools are accessible to everyone
    3. Internal tools require matching department or roles
    4. Private tools require matching created_by

    Args:
        user: Current user (None for anonymous)
        tool: Tool to check access for

    Returns:
        True if user has permission, False otherwise
    """
    # Public tools are accessible to everyone
    if tool.visibility == "public":
        return True

    # Anonymous users can only access public tools
    if user is None:
        return False

    # Superusers can access all tools
    if user.is_superuser:
        return True

    # Private tools - only creator can access
    if tool.visibility == "private":
        return str(tool.created_by) == str(user.id)

    # Internal tools - check department and roles
    if tool.visibility == "internal":
        # Check department match
        if tool.allowed_departments:
            if user.department and user.department in tool.allowed_departments:
                return True

        # Check role match
        if tool.allowed_roles:
            user_roles = set(user.roles or [])
            allowed_roles = set(tool.allowed_roles)
            if user_roles & allowed_roles:  # Intersection
                return True

        # No match found
        return False

    # Default deny
    return False


def check_skill_permission(user: User | None, skill: Skill) -> bool:
    """
    Check if a user has permission to access a skill.

    Same permission rules as tools.
    """
    # Public skills are accessible to everyone
    if skill.visibility == "public":
        return True

    if user is None:
        return False

    if user.is_superuser:
        return True

    if skill.visibility == "private":
        return str(skill.created_by) == str(user.id)

    if skill.visibility == "internal":
        if skill.allowed_departments:
            if user.department and user.department in skill.allowed_departments:
                return True

        if skill.allowed_roles:
            user_roles = set(user.roles or [])
            allowed_roles = set(skill.allowed_roles)
            if user_roles & allowed_roles:
                return True

        return False

    return False


def filter_tools_by_permission(user: User | None, tools: list[Tool]) -> list[Tool]:
    """Filter a list of tools to only those the user can access."""
    return [tool for tool in tools if check_tool_permission(user, tool)]


def filter_skills_by_permission(user: User | None, skills: list[Skill]) -> list[Skill]:
    """Filter a list of skills to only those the user can access."""
    return [skill for skill in skills if check_skill_permission(user, skill)]


def get_user_accessible_departments(user: User) -> list[str]:
    """
    Get list of departments a user can access tools/skills from.

    Returns:
        List of department names, empty list for unrestricted access
    """
    if user.is_superuser:
        return []  # Empty means unrestricted

    departments = []
    if user.department:
        departments.append(user.department)

    return departments


def get_user_roles(user: User) -> list[str]:
    """Get list of roles for a user."""
    return user.roles or []


# Common role definitions
class Roles:
    """Common role constants."""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    DEVELOPER = "developer"


# Common department definitions
class Departments:
    """Common department constants."""
    RISK = "风险管理部"
    CREDIT = "信贷管理部"
    TECH = "科技部"
    BUSINESS = "业务部"
    OPERATIONS = "运营部"
