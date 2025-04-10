"""
Data models and type definitions for A2AFlow
"""

from typing import Dict, Any, Optional, List, Literal, Union
from pydantic import BaseModel, Field
from enum import Enum


class AgentCapabilities(BaseModel):
    """A2A Agent Capabilities model."""
    streaming: bool
    pushNotifications: bool


class AgentSkill(BaseModel):
    """A2A Agent Skill model."""
    id: str
    name: str
    description: str
    examples: List[str] = Field(...)


class TaskStatus(str, Enum):
    """A2A Task Status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Message(BaseModel):
    """A2A Message model."""
    id: str
    content: str
    type: str = Field(default="text")
    metadata: Optional[Dict[str, Any]]


class TaskSendParams(BaseModel):
    """A2A Task Send Parameters model."""
    task: str
    session_id: Optional[str]
    input: Optional[Union[str, Dict[str, Any]]]
    input_mode: Optional[str]
    output_mode: Optional[str]


class AgentCard(BaseModel):
    """A2A Agent Card model."""
    name: str
    version: str
    url: str
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
    defaultInputModes: List[str]
    defaultOutputModes: List[str]


class Task(BaseModel):
    """A2A Task model."""
    id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]


class TaskState(BaseModel):
    """A2A Task State model."""
    id: str
    status: str
    result: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]


class SendTaskRequest(BaseModel):
    """A2A Send Task Request model."""
    method: str
    params: Dict[str, Any]


class SendTaskResponse(BaseModel):
    """A2A Send Task Response model."""
    jsonrpc: str
    id: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]
