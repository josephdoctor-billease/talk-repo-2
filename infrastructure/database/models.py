import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from infrastructure.database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tasks = relationship(
        "TaskModel", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_users_email_active", "email", "is_active"),)


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserModel", back_populates="tasks")

    __table_args__ = (
        Index("ix_tasks_user_id", "user_id"),
        Index("ix_tasks_user_completed", "user_id", "completed"),
        Index("ix_tasks_created_at", "created_at"),
    )
