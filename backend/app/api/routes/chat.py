import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ChatMessage,
    Conversation,
    ConversationCreate,
    ConversationPublic,
    ConversationsPublic,
    ConversationUpdate,
    ConversationWithMessages,
    MessageCreate,
    MessagePublic,
)

router = APIRouter()


@router.get("/", response_model=ConversationsPublic)
def read_conversations(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve conversations for the current user.
    """
    count_statement = (
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    conversations = session.exec(statement).all()

    return ConversationsPublic(data=conversations, count=count)


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


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
def read_conversation(
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: uuid.UUID,
) -> Any:
    """
    Get a specific conversation with all its messages.
    """
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Load messages
    statement = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
    )
    messages = session.exec(statement).all()

    return ConversationWithMessages(
        id=conversation.id,
        title=conversation.title,
        is_pinned=conversation.is_pinned,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[MessagePublic.model_validate(m) for m in messages],
    )


@router.patch("/{conversation_id}", response_model=ConversationPublic)
def update_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: uuid.UUID,
    conversation_in: ConversationUpdate,
) -> Any:
    """
    Update a conversation (title, pinned status).
    """
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = conversation_in.model_dump(exclude_unset=True)
    conversation.sqlmodel_update(update_data)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@router.delete("/{conversation_id}")
def delete_conversation(
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: uuid.UUID,
) -> Any:
    """
    Delete a conversation.
    """
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(conversation)
    session.commit()
    return {"message": "Conversation deleted successfully"}


@router.get("/{conversation_id}/messages", response_model=list[MessagePublic])
def read_messages(session: SessionDep, current_user: CurrentUser, conversation_id: uuid.UUID) -> Any:
    """
    Get messages for a conversation.
    """
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    statement = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
    )
    messages = session.exec(statement).all()
    return messages


@router.post("/{conversation_id}/send", response_model=MessagePublic)
def send_message(
    *, session: SessionDep, current_user: CurrentUser, conversation_id: uuid.UUID, message_in: MessageCreate
) -> Any:
    """
    Send a message to a conversation.
    """
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    message = ChatMessage.model_validate(message_in)
    message.conversation_id = conversation_id
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


async def ai_stream_generator(
    input_text: str,
    model: str | None = None,
    api_key: str | None = None,
    api_base: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stream AI responses with thinking chain visualization.

    Args:
        input_text: User's input message
        model: Model name to use
        api_key: API key for the provider
        api_base: API base URL for the provider

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

        # Stream from LLM with thinking chain, passing provider config
        async for sse_event in stream_chat_with_thinking(
            messages,
            model=model,
            enable_thinking=True,
            api_key=api_key,
            api_base=api_base,
        ):
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
    session: SessionDep,
    current_user: CurrentUser,
    message_in: MessageCreate,
    agent_id: uuid.UUID | None = None,
) -> Any:
    """
    Stream AI chat response using the user's selected model provider.
    
    If provider_id is specified, looks up the provider's API config from the database.
    Otherwise, falls back to environment variable configuration.
    """
    from app.models import ModelProvider
    
    input_text = message_in.content
    model = message_in.model
    api_key = None
    api_base = None
    
    # If provider_id is specified, look up provider config from database
    if message_in.provider_id:
        try:
            provider_uuid = uuid.UUID(message_in.provider_id)
            provider = session.get(ModelProvider, provider_uuid)
            if provider and provider.owner_id == current_user.id:
                api_key = provider.api_key
                api_base = provider.api_url
        except ValueError:
            pass  # Invalid UUID, use default config
    
    return StreamingResponse(
        ai_stream_generator(
            input_text,
            model=model,
            api_key=api_key,
            api_base=api_base,
        ),
        media_type="text/event-stream",
    )
