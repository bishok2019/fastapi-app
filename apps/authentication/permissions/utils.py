from functools import wraps
from typing import List

from fastapi import Depends, HTTPException, security, status
from fastapi.security import HTTPAuthorizationCredentials

from ..authentication import check_permissions, get_current_active_user, verify_token
from ..models import User


class PermissionLists:
    HTTP_GET_METHOD = "GET"
    HTTP_POST_METHOD = "POST"
    HTTP_PATCH_METHOD = "PATCH"

    # ------SUPPORT_ROLE_NAME--------#
    SUPPORT_ROLE_NAME = "SUPPORT"

    # -------Authentication APP -------#
    CUSTOM_USER = "custom_user"
    USER_PROFILE = "user_profile"
    CUSTOM_PERMISSION = "custom_permission"
    PERMISSION_CATEGORY = "permission_category"
    ROLES = "roles"
    ROLE_NAME = "SUPPORT"

    # -------API Logs APP -------#
    API_LOG = "api_log"

    # --------Blog APP -------#
    BLOG = "blog_post"
    # --------Stock APP-------#
    STOCK = "stock"

    # --------All model list for Management Command -------#
    # ALL_MODELS = {
    #     "CUSTOM_USER": CUSTOM_USER,
    #     "USER_PROFILE": USER_PROFILE,
    #     "CUSTOM_PERMISSION": CUSTOM_PERMISSION,
    #     "PERMISSION_CATEGORY": PERMISSION_CATEGORY,
    #     "ROLES": ROLES,
    #     "API_LOG": API_LOG,
    #     "BLOG": BLOG,
    #     "STOCK": STOCK,
    # }


class HttpBasedPermissionActionMaps:
    CAN_CREATE = "can_create"
    CAN_VIEW = "can_view"
    CAN_UPDATE = "can_update"
    CAN_DELETE = "can_delete"


def required_permissions(require_permissions: List[str]):
    """
    Dependency factory: returns a dependency that checks if the user has the required permissions.
    Usage: Depends(required_permissions(["permission_code"]))
    """

    def dependency(current_user: User = Depends(get_current_active_user)):
        if not check_permissions(require_permissions, current_user):
            if require_permissions.startswith("can_"):
                message = require_permissions[4:].replace("_", " ").title()
            else:
                message = require_permissions.replace("_", " ").title()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to {message}.",
            )
        return current_user  # return user for use inside the endpoint if needed

    return dependency


def permission_required(permission: str):
    def permission_required_decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request & db from endpoint args
            request = kwargs.get("request")
            db = kwargs.get("db")

            if request is None or db is None:
                raise RuntimeError(
                    "permission_required needs request and db dependencies."
                )

            # Extract token manually
            credentials: HTTPAuthorizationCredentials = await security(request)
            token = credentials.credentials

            user_id = verify_token(token)
            current_user = db.query(User).filter(User.id == user_id).first()

            if not current_user:
                raise HTTPException(status_code=401, detail="User not found")

            if not current_user.is_active:
                raise HTTPException(status_code=400, detail="Inactive user")

            if not check_permissions([permission], current_user):
                action = (
                    permission[4:].replace("_", " ")
                    if permission.startswith("can_")
                    else permission
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You do not have permission to {action}.",
                )

            return await func(*args, **kwargs)

        return wrapper

    return permission_required_decorator
