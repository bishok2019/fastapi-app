from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from base.models import BaseModel

from .users import role_permissions


class CustomRole(BaseModel):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship(
        "CustomPermission", secondary=role_permissions, back_populates="roles"
    )
    users = relationship("User", secondary="user_roles", back_populates="user_roles")


class PermissionCategory(BaseModel):
    __tablename__ = "permission_categories"

    name = Column(String(50), unique=True, nullable=False)
    permissions = relationship("CustomPermission", back_populates="category")


class CustomPermission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String(50), unique=True, nullable=False)
    code_name = Column(String(100), unique=True, nullable=False)
    category_id = Column(
        Integer,
        ForeignKey("permission_categories.id", ondelete="CASCADE"),
    )
    category = relationship("PermissionCategory", back_populates="permissions")

    roles = relationship(
        "CustomRole", secondary=role_permissions, back_populates="permissions"
    )
    users = relationship(
        "User", secondary="user_permissions", back_populates="user_permissions"
    )
