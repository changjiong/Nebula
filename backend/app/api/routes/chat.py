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
    ConversationUpdate,
    ConversationWithMessages,
    ConversationsPublic,
    MessageCreate,
    MessagePublic,
    Tool,
)
from app.core.permissions import filter_tools_by_permission
from app.engine.nfc_graph import stream_nfc_agent
from app.llm.base import ToolDefinition

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

    message = ChatMessage(conversation_id=conversation_id, **message_in.model_dump())
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


async def nfc_stream_generator(
    input_text: str,
    user_id: uuid.UUID,
    session_id: str = "default",
    model: str = "deepseek-chat",
    db_session: Any = None,
    tools: list[ToolDefinition] | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stream NFC Agent responses with structured SSE events.
    
    Events:
    - tool_call: Agent decides to call a tool
    - tool_result: Tool execution result
    - message: Partial or final text response
    - error: Error details
    - done: Stream completion
    """
    import json
    
    try:
        # Stream events from the agent graph
        async for event in stream_nfc_agent(
            input_text=input_text,
            session_id=session_id,
            user_id=str(user_id),
            model=model,
            tools=tools,
            session=db_session,
        ):
            # Handle "think" node events (Tool Calls)
            if "think" in event:
                data = event["think"]
                # If tool calls are pending
                if "pending_tool_calls" in data and data["pending_tool_calls"]:
                    for call in data["pending_tool_calls"]:
                        # Emit tool_call event
                        sse_data = {
                            "id": call.id,
                            "name": call.name,
                            "arguments": call.arguments,
                            "status": "calling"
                        }
                        yield f"data: {json.dumps({'event': 'tool_call', 'data': json.dumps(sse_data)})}\n\n"
                
                # If final response is ready (or partial)
                if "final_response" in data and data["final_response"]:
                    # Depending on how the graph returns it, might be full text
                    # For streaming text, we might need granular LLM streaming support
                    # For now, yield the chunk
                    yield f"data: {json.dumps({'event': 'message', 'data': json.dumps({'content': data['final_response']})})}\n\n"

            # Handle "execute_tools" node events (Tool Results)
            if "execute_tools" in event:
                data = event["execute_tools"]
                if "tool_results" in data:
                    for result in data["tool_results"]:
                        sse_data = {
                            "id": result["tool_call_id"],
                            "name": result["tool_name"],
                            "result": str(result.get("result", "")),
                            "success": result.get("success", False),
                            "error": result.get("error")
                        }
                        yield f"data: {json.dumps({'event': 'tool_result', 'data': json.dumps(sse_data)})}\n\n"

            # Handle "respond" node (Done)
            if "respond" in event:
                # Completion
                pass

        yield f"data: {json.dumps({'event': 'done', 'data': '{}'})}\n\n"

    except Exception as e:
        import traceback
        traceback.print_exc()
        error_event = {
            "type": "error",
            "data": {"code": "stream_error", "message": str(e)}
        }
        yield f"data: {json.dumps(error_event)}\n\n"
        yield f"data: {json.dumps({'event': 'done', 'data': '{}'})}\n\n"


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
    model = message_in.model or "deepseek-chat"
    
    # 1. Permission Control: Fetch valid tools for current user
    all_tools = session.exec(select(Tool).where(Tool.status == "active")).all()
    accessible_tools = filter_tools_by_permission(current_user, all_tools)
    
    # Convert to ToolDefinition for LLM
    tool_definitions = []
    for t in accessible_tools:
        # Convert schema string to dict if needed, assuming input_schema is dict
        tool_definitions.append(ToolDefinition(
            name=t.name,
            description=t.description,
            parameters=t.input_schema
        ))

    # 2. Check Provider (Optional override)
    # The LLMGateway manages providers, but we can hint preference or API key override if needed
    # For now, we rely on Gateway's configuration management
    
    # 3. Stream Response
    return StreamingResponse(
        nfc_stream_generator(
            input_text=input_text,
            user_id=current_user.id,
            session_id=str(agent_id) if agent_id else "default",
            model=model,
            db_session=session,
            tools=tool_definitions,
        ),
        media_type="text/event-stream",
    )
