from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from base.models import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    posts = relationship("Post", back_populates="author")
    user_notifications = relationship(
        "UserNotification", back_populates="user"
    )  # reverse relationship to UserNotification
    user_roles = relationship(
        "CustomRole", secondary="user_roles", back_populates="users"
    )  # reverse relationship to UserRole
    user_permissions = relationship(
        "CustomPermission", secondary="user_permissions", back_populates="users"
    )  # reverse relationship to UserPermission


# Association tables
user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    extend_existing=True,  # This allows us to redefine the table if it already exists, which can be useful during development
)

user_permissions = Table(
    "user_permissions",
    BaseModel.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    extend_existing=True,  # This allows us to redefine the table if it already exists, which can be useful during development
)

role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    extend_existing=True,  # This allows us to redefine the table if it already exists, which can be useful during development
)
