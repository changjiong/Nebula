import uuid
from typing import Any, AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.core.llm import stream_chat_completion
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
def read_messages(session: SessionDep, conversation_id: uuid.UUID) -> Any:
    """
    Get messages for a conversation.
    """
    statement = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
    )
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


async def ai_stream_generator(input_text: str) -> AsyncGenerator[str, None]:
    """
    Stream AI responses with thinking chain visualization.
    
    Yields SSE-formatted events:
    - thinking: Reasoning steps
    - message: Response content
    - error: Error messages
    """
    try:
        from app.core.llm_thinking import stream_chat_with_thinking
        
        # Prepare messages for LLM
        messages = [
            {
                "role": "system",
                "content": "你是一个有帮助的AI助手。请清晰简洁地回答问题。",
            },
            {
                "role": "user",
                "content": input_text,
            },
        ]
        
        # Stream from LLM with thinking chain
        async for sse_event in stream_chat_with_thinking(messages, enable_thinking=True):
            yield sse_event
        
    except Exception as e:
        import json
        error_event = {
            "type": "error",
            "data": {"code": "stream_error", "message": str(e)}
        }
        yield f"data: {json.dumps(error_event)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/stream")
def stream_chat(
    *,
    _session: SessionDep,
    _message_in: MessageCreate,
    _agent_id: uuid.UUID | None = None,
) -> Any:
    """
    Stream AI chat response using DeepSeek.
    """
    input_text = _message_in.content
    
    return StreamingResponse(
        ai_stream_generator(input_text),
        media_type="text/event-stream",
    )
