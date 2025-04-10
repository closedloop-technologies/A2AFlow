"""
Tests for A2A Client implementation
"""

import pytest
from unittest.mock import patch, MagicMock
from a2aflow.models import AgentCard, AgentSkill, AgentCapabilities
from a2aflow.client import A2AClient


@pytest.mark.asyncio
async def test_client_creation():
    """Test client creation with minimal parameters."""
    client = A2AClient()
    assert client.url == "http://localhost:10000"  # Default URL


@pytest.mark.asyncio
async def test_client_with_agent_card():
    """Test client creation with custom agent card."""
    custom_card = AgentCard(
        name="Custom Agent",
        version="1.0.0",
        url="http://custom-agent.com",
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        skills=[
            AgentSkill(
                id="custom_skill",
                name="Custom Skill",
                description="A custom skill",
                examples=["Example 1", "Example 2"]
            )
        ],
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
    )
    client = A2AClient(agent_card=custom_card)
    assert client.agent_card == custom_card


@pytest.mark.asyncio
async def test_client_with_url():
    """Test client creation with custom URL."""
    custom_url = "http://custom-agent.com"
    client = A2AClient(url=custom_url)
    assert client.url == custom_url


@pytest.mark.asyncio
async def test_resolve_agent_card():
    """Test resolving agent card from URL."""
    mock_agent_card = AgentCard(
        name="Test Agent",
        version="1.0.0",
        url="http://localhost:10000",
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        skills=[
            AgentSkill(
                id="test_skill",
                name="Test Skill",
                description="A test skill",
                examples=["Example 1", "Example 2"]
            )
        ],
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
    )

    with patch("a2aflow.client.httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_agent_card.model_dump()
        mock_get.return_value = mock_response
        
        client = A2AClient(url="http://test.example.com")
        # Need to call a method that will trigger the agent card resolution
        await client._ensure_agent_card()
        assert client.agent_card.model_dump() == mock_agent_card.model_dump()


@pytest.mark.asyncio
async def test_send_task():
    """Test sending a task."""
    mock_agent_card = AgentCard(
        name="Test Agent",
        version="1.0.0",
        url="http://localhost:10000",
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        skills=[
            AgentSkill(
                id="test_skill",
                name="Test Skill",
                description="A test skill",
                examples=["Example 1", "Example 2"]
            )
        ],
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
    )

    client = A2AClient(agent_card=mock_agent_card)
    with patch("a2aflow.client.httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"task_id": "123"}
        }
        mock_post.return_value = mock_response
        
        result = await client.send_task("test task")
        assert result["result"]["task_id"] == "123"


@pytest.mark.asyncio
async def test_get_task():
    """Test getting task status."""
    mock_agent_card = AgentCard(
        name="Test Agent",
        version="1.0.0",
        url="http://localhost:10000",
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        skills=[
            AgentSkill(
                id="test_skill",
                name="Test Skill",
                description="A test skill",
                examples=["Example 1", "Example 2"]
            )
        ],
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
    )

    client = A2AClient(agent_card=mock_agent_card)
    with patch("a2aflow.client.httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"status": "completed", "result": "done"}
        }
        mock_post.return_value = mock_response
        
        result = await client.get_task("123")
        assert result["result"]["status"] == "completed"
        assert result["result"]["result"] == "done"
