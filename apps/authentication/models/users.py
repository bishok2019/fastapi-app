from sqlalchemy import Boolean, Column, String
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
        "UserRole", back_populates="user"
    )  # reverse relationship to UserRole
    user_permissions = relationship(
        "UserPermission", back_populates="user"
    )  # reverse relationship to UserPermission
