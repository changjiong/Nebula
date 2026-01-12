import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ChatMessage,
    Conversation,
    ConversationCreate,
    ConversationPublic,
    MessageCreate,
    MessagePublic,
)

router = APIRouter()

@router.post("/", response_model=ConversationPublic)
def create_conversation(
    *, session: SessionDep, current_user: CurrentUser, conversation_in: ConversationCreate
) -> Any:
    """
    Create new conversation.
    """
    conversation = Conversation.model_validate(conversation_in)
    conversation.user_id = current_user.id
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

@router.get("/{conversation_id}/messages", response_model=list[MessagePublic])
def read_messages(
    session: SessionDep, conversation_id: uuid.UUID
) -> Any:
    """
    Get messages for a conversation.
    """
    statement = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id).order_by(ChatMessage.created_at)
    messages = session.exec(statement).all()
    return messages

@router.post("/{conversation_id}/send", response_model=MessagePublic)
def send_message(
    *, session: SessionDep, conversation_id: uuid.UUID, message_in: MessageCreate
) -> Any:
    """
    Send a message to a conversation.
    """
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    message = ChatMessage.model_validate(message_in)
    message.conversation_id = conversation_id
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def stream_generator():
    """
    Mock generator for SSE.
    """
    import time
    response_text = "This is a streaming response from the Agent Portal."
    # Simulate thinking
    time.sleep(0.5)

    words = response_text.split()
    for word in words:
        # Format as SSE event
        yield f"data: {word} \n\n"
        time.sleep(0.1)

    # End of stream signal if needed, or just close connection
    yield "data: [DONE]\n\n"

@router.post("/stream")
def stream_chat(
    *, _session: SessionDep, _message_in: MessageCreate, _agent_id: uuid.UUID | None = None
) -> Any:
    """
    Stream chat response (SSE).
    """
    # In a real scenario, this would interact with the Agent/LLM backend
    return StreamingResponse(stream_generator(), media_type="text/event-stream")
