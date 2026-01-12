import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.models import Agent, AgentCreate, AgentPublic, AgentsPublic, AgentUpdate

router = APIRouter()

@router.get("/", response_model=AgentsPublic)
def read_agents(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve agents.
    """
    count_statement = select(func.count()).select_from(Agent)
    count = session.exec(count_statement).one()

    statement = select(Agent).offset(skip).limit(limit)
    agents = session.exec(statement).all()

    return AgentsPublic(data=agents, count=count)

@router.get("/{id}", response_model=AgentPublic)
def read_agent(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get agent by ID.
    """
    agent = session.get(Agent, id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/", response_model=AgentPublic)
def create_agent(
    *, session: SessionDep, agent_in: AgentCreate
) -> Any:
    """
    Create new agent.
    """
    agent = Agent.model_validate(agent_in)
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent

@router.put("/{id}", response_model=AgentPublic)
def update_agent(
    *, session: SessionDep, id: uuid.UUID, agent_in: AgentUpdate
) -> Any:
    """
    Update an agent.
    """
    agent = session.get(Agent, id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = agent_in.model_dump(exclude_unset=True)
    agent.sqlmodel_update(update_data)
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent

@router.delete("/{id}", response_model=AgentPublic)
def delete_agent(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Delete an agent.
    """
    agent = session.get(Agent, id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    session.delete(agent)
    session.commit()
    return agent
