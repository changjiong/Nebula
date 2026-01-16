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
        # Lazy creation if conversation not found (similar to stream endpoint)
        conversation = Conversation(
            id=conversation_id,
            user_id=current_user.id,
            title=message_in.content[:50]  # Auto title
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # Re-check ownership even if just created (for safety, though redundant if just created)
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    message = ChatMessage(conversation_id=conversation_id, **message_in.model_dump(exclude={"conversation_id"}))
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
    provider_id: str | None = None,
    conversation_id: uuid.UUID | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stream NFC Agent responses with structured SSE events.
    
    Events:
    - tool_call: Agent decides to call a tool (with group and subItem info)
    - tool_result: Tool execution result
    - thinking: Reasoning/thinking process
    - message: Partial or final text response
    - error: Error details
    - done: Stream completion
    """
    import json
    import asyncio
    from app.llm.stream_context import stream_context_var, StreamContext

    # Helper function to determine tool group based on tool name
    def get_tool_group(tool_name: str) -> str:
        """Categorize tools into groups for Manus-style timeline display."""
        search_tools = ["search", "web_search", "google_search", "bing_search", "search_web"]
        browse_tools = ["browse", "browse_url", "read_url", "fetch_page", "scrape"]
        file_tools = ["create_file", "edit_file", "read_file", "write_file", "delete_file"]
        mcp_tools = ["mcp_", "supabase", "database"]
        code_tools = ["run_code", "execute", "python", "shell", "terminal"]
        
        tool_lower = tool_name.lower()
        
        if any(t in tool_lower for t in search_tools):
            return "搜索信息"
        elif any(t in tool_lower for t in browse_tools):
            return "深度访问"
        elif any(t in tool_lower for t in file_tools):
            return "文件操作"
        elif any(t in tool_lower for t in mcp_tools):
            return "MCP服务调用"
        elif any(t in tool_lower for t in code_tools):
            return "代码执行"
        else:
            return "工具调用"
    
    # Helper function to determine sub-item type
    def get_sub_item_type(tool_name: str) -> str:
        """Determine the sub-item type for frontend icon display."""
        tool_lower = tool_name.lower()
        
        if any(t in tool_lower for t in ["search", "google", "bing"]):
            return "search-result"
        elif any(t in tool_lower for t in ["browse", "url", "fetch", "scrape", "read_url"]):
            return "browse"
        elif any(t in tool_lower for t in ["file", "create", "edit", "write", "read"]):
            return "file-operation"
        elif any(t in tool_lower for t in ["mcp", "supabase", "database"]):
            return "mcp-call"
        elif any(t in tool_lower for t in ["run", "execute", "python", "shell"]):
            return "code-execution"
        else:
            return "api-call"
    
    # Helper function to get display title for tool
    def get_tool_display_title(tool_name: str, arguments: dict) -> str:
        """Generate a user-friendly display title for the tool call."""
        tool_lower = tool_name.lower()
        
        if "search" in tool_lower:
            query = arguments.get("query", arguments.get("q", ""))
            return f"正在搜索 {query[:50]}..." if query else f"正在搜索..."
        elif "browse" in tool_lower or "url" in tool_lower:
            url = arguments.get("url", "")
            return f"正在浏览 {url[:50]}..." if url else f"正在浏览网页..."
        elif "file" in tool_lower:
            path = arguments.get("path", arguments.get("filename", ""))
            if "create" in tool_lower or "write" in tool_lower:
                return f"正在创建文件 {path}" if path else "正在创建文件..."
            elif "read" in tool_lower:
                return f"正在读取文件 {path}" if path else "正在读取文件..."
            elif "edit" in tool_lower:
                return f"正在编辑文件 {path}" if path else "正在编辑文件..."
            else:
                return f"文件操作 {path}" if path else "文件操作..."
        elif "mcp" in tool_lower or "supabase" in tool_lower:
            return f"调用MCP服务: {tool_name}"
        else:
            return f"调用工具: {tool_name}"

    queue = asyncio.Queue()
    token = stream_context_var.set(StreamContext(queue=queue))
    
    # Track tool calls for grouping
    active_tool_groups: dict[str, str] = {}  # group_name -> group_id
    
    # Task to run the graph execution
    async def run_graph():
        try:
            async for event in stream_nfc_agent(
                input_text=input_text,
                session_id=session_id,
                user_id=str(user_id),
                model=model,
                tools=tools,
                session=db_session,
                provider_id=provider_id,
            ):
                await queue.put({"type": "graph_event", "payload": event})
        except Exception as e:
            await queue.put({"type": "error", "error": e})
        finally:
            await queue.put(None)  # Signal done

    # Start graph execution in background
    graph_task = asyncio.create_task(run_graph())
    
    try:
        current_think_id = None
        accumulated_reasoning = ""  # Accumulate reasoning content
        
        # Track full response and thinking steps for persistence
        full_response_content = ""
        thinking_steps_log: list[dict] = []
        # Local map to update steps in log by ID
        steps_map: dict[str, dict] = {}

        
        # NO initial empty thinking event - wait for actual content
        
        while True:
            # Wait for next item in queue
            item = await queue.get()
            
            if item is None:
                # Complete any pending thinking step
                if current_think_id:
                    sse_data = {
                        "id": current_think_id,
                        "title": "思考过程",
                        "status": "completed",
                        "content": accumulated_reasoning
                    }
                    yield f"data: {json.dumps({'event': 'thinking', 'data': json.dumps(sse_data)})}\n\n"
                break
            
            if isinstance(item, dict) and item.get("type") == "error":
                raise item["error"]
            
            if isinstance(item, dict) and item.get("type") == "graph_event":
                # Handle standard graph events
                event = item["payload"]
                
                if "think" in event:
                    data = event["think"]
                    # If tool calls are pending
                    if "pending_tool_calls" in data and data["pending_tool_calls"]:
                        for call in data["pending_tool_calls"]:
                            tool_group = get_tool_group(call.name)
                            sub_item_type = get_sub_item_type(call.name)
                            display_title = get_tool_display_title(call.name, call.arguments)
                            
                            # Create or get group ID
                            if tool_group not in active_tool_groups:
                                active_tool_groups[tool_group] = f"group-{uuid.uuid4()}"
                            
                            sse_data = {
                                "id": call.id,
                                "name": call.name,
                                "arguments": call.arguments,
                                "status": "calling",
                                # Manus-style enhancements
                                "group": tool_group,
                                "groupId": active_tool_groups[tool_group],
                                "displayTitle": display_title,
                                "subItemType": sub_item_type,
                            }
                            
                            # Log tool call step
                            step_entry = {
                                "id": call.id,
                                "title": display_title,
                                "status": "in-progress",
                                "content": f"参数:\n{json.dumps(call.arguments, indent=2, ensure_ascii=False)}",
                                "timestamp": int(datetime.now().timestamp() * 1000),
                                "group": tool_group,
                                "subItems": [{
                                    "id": f"sub-{call.id}",
                                    "type": sub_item_type,
                                    "title": call.name,
                                    "content": json.dumps(call.arguments, indent=2, ensure_ascii=False),
                                    "previewable": True
                                }]
                            }
                            thinking_steps_log.append(step_entry)
                            steps_map[call.id] = step_entry
                            
                            yield f"data: {json.dumps({'event': 'tool_call', 'data': json.dumps(sse_data)})}\n\n"
                
                if "execute_tools" in event:
                    data = event["execute_tools"]
                    if "tool_results" in data:
                        for result in data["tool_results"]:
                            tool_name = result.get("tool_name", "")
                            tool_group = get_tool_group(tool_name)
                            sub_item_type = get_sub_item_type(tool_name)
                            
                            # Format result for display
                            result_content = result.get("result", "")
                            if isinstance(result_content, dict):
                                result_content = json.dumps(result_content, ensure_ascii=False, indent=2)
                            else:
                                result_content = str(result_content)
                            
                            sse_data = {
                                "id": result["tool_call_id"],
                                "name": tool_name,
                                "result": result_content,
                                "success": result.get("success", False),
                                "error": result.get("error"),
                                # Manus-style enhancements
                                "group": tool_group,
                                "groupId": active_tool_groups.get(tool_group, ""),
                                "subItemType": sub_item_type,
                            }
                            
                            # Update step in log
                            if result["tool_call_id"] in steps_map:
                                step = steps_map[result["tool_call_id"]]
                                step["status"] = "completed" if result.get("success", False) else "failed"
                                step["content"] = f"执行失败: {result.get('error')}" if result.get("error") else f"执行完成\n\n结果:\n{result_content}"
                                # Update subItem
                                if step.get("subItems"):
                                    step["subItems"][0]["content"] = f"错误: {result.get('error')}" if result.get("error") else result_content
                            
                            yield f"data: {json.dumps({'event': 'tool_result', 'data': json.dumps(sse_data)})}\n\n"
                            
            else:
                # It's a StreamChunk from the adapter
                chunk = item
                
                # Handle Reasoning Content
                if chunk.reasoning_content:
                    if not current_think_id:
                        current_think_id = f"think-{uuid.uuid4()}"
                        accumulated_reasoning = ""
                        # Initialize think step with group
                        sse_data = {
                            "id": current_think_id,
                            "title": "思考过程",
                            "status": "in-progress",
                            "content": "",
                            "group": "分析与推理"
                        }
                        
                        # Log thinking step
                        step_entry = {
                            "id": current_think_id,
                            "title": "思考过程",
                            "status": "in-progress",
                            "content": "",
                            "timestamp": int(datetime.now().timestamp() * 1000),
                            "group": "分析与推理"
                        }
                        thinking_steps_log.append(step_entry)
                        steps_map[current_think_id] = step_entry
                        
                        yield f"data: {json.dumps({'event': 'thinking', 'data': json.dumps(sse_data)})}\n\n"
                    
                    # Accumulate and stream reasoning update
                    accumulated_reasoning += chunk.reasoning_content
                    sse_data = {
                        "id": current_think_id,
                        "title": "思考过程",
                        "status": "in-progress",
                        "content": chunk.reasoning_content,  # Send delta
                        "accumulated": accumulated_reasoning  # Also send full content
                    }
                    
                    # Update log
                    if current_think_id in steps_map:
                        steps_map[current_think_id]["content"] = accumulated_reasoning
                        
                    yield f"data: {json.dumps({'event': 'thinking', 'data': json.dumps(sse_data)})}\n\n"

                # Check if we should close the thinking step
                if current_think_id and (chunk.content or chunk.finish_reason):
                    sse_data = {
                        "id": current_think_id,
                        "title": "思考过程",
                        "status": "completed",
                        "content": accumulated_reasoning,
                        "group": "分析与推理"
                    }
                    
                    if current_think_id in steps_map:
                        steps_map[current_think_id]["status"] = "completed"
                        steps_map[current_think_id]["content"] = accumulated_reasoning

                    yield f"data: {json.dumps({'event': 'thinking', 'data': json.dumps(sse_data)})}\n\n"
                    current_think_id = None
                    accumulated_reasoning = ""

                # Handle Message Content
                if chunk.content:
                    full_response_content += chunk.content
                    yield f"data: {json.dumps({'event': 'message', 'data': json.dumps({'content': chunk.content})})}\n\n"
                
                # Check for finish
                if chunk.finish_reason:
                    pass

        # Persist the assistant message
        if conversation_id and db_session:
            # Check permissions? Already checked in endpoint.
            assistant_msg = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=full_response_content,
                thinking_steps=thinking_steps_log
            )
            db_session.add(assistant_msg)
            db_session.commit()

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
    
    finally:
        stream_context_var.reset(token)




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
    provider_id = message_in.provider_id
    conversation_id = message_in.conversation_id
    
    # Handle Conversation/Message persistence if conversation_id provided
    if conversation_id:
        conversation = session.get(Conversation, conversation_id)
        if not conversation:
            # Create if missing (lazy creation for client flexibility)
            conversation = Conversation(
                id=conversation_id,
                user_id=current_user.id,
                title=input_text[:50]  # Auto title
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            
        if conversation.user_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Save USER message
        user_msg = ChatMessage(
            conversation_id=conversation_id,
            role="user",
            content=input_text
        )
        session.add(user_msg)
        session.commit()

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
            provider_id=provider_id,
            conversation_id=conversation_id,
        ),
        media_type="text/event-stream",
    )
