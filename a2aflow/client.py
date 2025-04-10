"""
A2A Client implementation for PocketFlow
"""

from typing import Dict, Any, Optional, AsyncGenerator
import httpx
import uuid
from a2aflow.models import AgentCard


class A2ACardResolver:
    """A2A Agent Card Resolver."""

    def __init__(self, url: str):
        self.url = url

    async def get_agent_card(self) -> AgentCard:
        """Resolve agent card from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.url}/.well-known/agent.json")
            response.raise_for_status()
            return AgentCard(**response.json())


class A2AClient:
    """A2A client implementation for PocketFlow."""

    def __init__(self, agent_card=None, url=None):
        self.agent_card = agent_card
        self.url = url or "http://localhost:10000"  # Default URL if none provided
        self._resolver = None
        if url and not agent_card:
            # Create resolver but don't await it yet - will be resolved on first use
            self._resolver = A2ACardResolver(url)

    async def _ensure_agent_card(self):
        """Ensure agent card is resolved if needed."""
        if self._resolver and not isinstance(self.agent_card, AgentCard):
            self.agent_card = await self._resolver.get_agent_card()
        return self.agent_card

    async def send_task(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Send a task to the A2A server."""
        await self._ensure_agent_card()

        if not session_id:
            session_id = str(uuid.uuid4())

        task_id = str(uuid.uuid4())
        request = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "tasks/send",
            "params": {
                "task": query,
                "session_id": session_id,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=request)
            response.raise_for_status()
            return response.json()

    # These methods would be implemented for more complex task handling in the future
    async def _send_streaming_task(self, payload):
        """Send a streaming task and collect results."""
        # Implementation for streaming
        raise NotImplementedError("Streaming not implemented yet")

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task status from the A2A server."""
        await self._ensure_agent_card()

        request = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "tasks/get",
            "params": {
                "task_id": task_id,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=request)
            response.raise_for_status()
            return response.json()
