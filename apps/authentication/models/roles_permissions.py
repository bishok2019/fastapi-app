from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from base.models import BaseModel

# Association table for many-to-many relationship
role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column(
        "role_id",
        String(50),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        String(50),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class CustomRole(BaseModel):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship(
        "CustomPermission", secondary=role_permissions, back_populates="roles"
    )


class PermissionCategory(BaseModel):
    __tablename__ = "permission_categories"

    name = Column(String(50), unique=True, nullable=False)
    permissions = relationship("CustomPermission", back_populates="category")


class CustomPermission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String(50), unique=True, nullable=False)
    category_id = Column(
        String(50),
        ForeignKey("permission_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    category = relationship("PermissionCategory", back_populates="permissions")

    roles = relationship(
        "CustomRole", secondary=role_permissions, back_populates="permissions"
    )
