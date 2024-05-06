"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .subadmin import subadmin_router
from .channels import chat_router
from .user import user_router

routers_list = [
    # admin_router,
    subadmin_router,
    chat_router,
    user_router,
]

__all__ = [
    "routers_list",
]
