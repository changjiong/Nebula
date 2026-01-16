import uuid
from datetime import datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


# Shared properties for Conversation
class ConversationBase(SQLModel):
    title: str | None = Field(default=None, max_length=255)


# Properties to receive on creation
class ConversationCreate(ConversationBase):
    pass


# Properties to receive on update
class ConversationUpdate(SQLModel):
    title: str | None = None
    is_pinned: bool | None = None


# Database model for Conversation
class Conversation(ConversationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", nullable=True, ondelete="CASCADE")
    is_pinned: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    messages: list["Message"] = Relationship(back_populates="conversation", sa_relationship_kwargs={"cascade": "all, delete"})


# Properties to return via API
class ConversationPublic(ConversationBase):
    id: uuid.UUID
    is_pinned: bool
    created_at: datetime
    updated_at: datetime


# List of conversations
class ConversationsPublic(SQLModel):
    data: list[ConversationPublic]
    count: int


# Shared properties for Message
class MessageBase(SQLModel):
    role: str = Field(max_length=50)  # user, assistant, system
    content: str
    thinking_steps: list[dict] | None = Field(default=None, sa_column=Column(JSON))


# Properties to receive on creation
class MessageCreate(MessageBase):
    model: str | None = None  # Selected model name (e.g., "gpt-4o", "deepseek-chat")
    provider_id: str | None = None  # UUID of the ModelProvider to use
    conversation_id: uuid.UUID | None = None


# Database model for Message
class Message(MessageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")


# Properties to return via API
class MessagePublic(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime


# Conversation with all messages included
class ConversationWithMessages(ConversationPublic):
    messages: list[MessagePublic] = []
