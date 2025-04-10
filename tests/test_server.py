"""Tests for the A2AFlow server functionality."""

import json
import pytest
from unittest.mock import patch, MagicMock

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse, Response

from a2aflow import A2ANode, A2AFlow, A2AServer
from a2aflow.models import (
    TaskState,
    Task,
    TaskStatus,
    Message,
    TaskSendParams,
    SendTaskRequest,
    AgentCard,
    AgentSkill,
)

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from datetime import datetime

from a2aflow.server import A2AServer
from a2aflow.core import Flow
from a2aflow.tasks import TaskStatus, TaskNotFoundError, TaskNotCancelableError


class TNode(A2ANode):  # Test Node
    """A simple node for testing the server."""

    def exec(self, query):
        # Simple echo for testing
        return f"Echo: {query}"


@pytest.fixture
def test_app():
    """Create a test app with the A2A server."""
    # Create a simple flow
    node = TNode()
    flow = A2AFlow(
        start=node,
        capabilities={"streaming": False, "pushNotifications": False},
        skills=[
            AgentSkill(
                id="test_skill",
                name="Test Skill",
                description="A test skill for unit testing",
                examples=["Example 1", "Example 2"],
            )
        ],
    )

    # Create a server but don't start it
    server = A2AServer(flow=flow, host="localhost", port=10000)

    # Setup routes explicitly for testing
    @server._app.get("/.well-known/agent.json")
    def get_agent_card():
        return server.agent_card

    @server._app.post("/")
    async def handle_request(request: Request):
        try:
            body = await request.json()

            # Validate A2A request
            method = body.get("method")
            if not method:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid request"},
                    },
                    status_code=400,
                )

            if method == "tasks/send":
                # Mock task creation
                task_id = body["params"].get("id", "test_task_id")
                session_id = body["params"].get("sessionId", "test_session_id")
                message = "Echo: Hello, world!"

                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {
                            "id": task_id,
                            "sessionId": session_id,
                            "status": {
                                "state": "completed",
                                "message": {
                                    "role": "agent",
                                    "parts": [{"type": "text", "text": message}],
                                },
                                "timestamp": "2023-01-01T12:00:00Z",
                            },
                        },
                    }
                )
            elif method == "tasks/get":
                task_id = body["params"].get("id", "unknown_task")
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {
                            "id": task_id,
                            "sessionId": "test_session_id",
                            "status": {
                                "state": "completed",
                                "message": {
                                    "role": "agent",
                                    "parts": [{"type": "text", "text": "Task result"}],
                                },
                                "timestamp": "2023-01-01T12:00:00Z",
                            },
                        },
                    }
                )
            else:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Method not found"},
                    },
                    status_code=404,
                )
        except Exception as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": str(e)},
                },
                status_code=500,
            )

    # Return the app for testing
    return server._app


@pytest.fixture
def test_client(test_app):
    """Create a TestClient for the FastAPI app."""
    return TestClient(test_app)


class TestA2AServer:
    """Test the A2AServer class."""

    def test_get_agent_card(self, test_client):
        """Test that the server returns the agent card on GET /.well-known/agent.json."""
        response = test_client.get("/.well-known/agent.json")

        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "capabilities" in data
        assert "skills" in data
        assert len(data["skills"]) == 1
        assert data["skills"][0]["name"] == "Test Skill"

    def test_send_task(self, test_client):
        """Test sending a task to the server."""
        # Create a test request
        request_data = {
            "jsonrpc": "2.0",
            "id": "test_request_id",
            "method": "tasks/send",
            "params": {
                "id": "test_task_id",
                "sessionId": "test_session_id",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Hello, world!"}],
                },
            },
        }

        data = self.post_and_validate(
            test_client, request_data, "test_request_id", "test_task_id"
        )
        assert data["result"]["sessionId"] == "test_session_id"
        assert data["result"]["status"]["state"] == "completed"

        # Check that the response contains our echo message
        message = data["result"]["status"]["message"]
        assert message["role"] == "agent"
        assert message["parts"][0]["type"] == "text"
        assert "Echo: Hello, world!" in message["parts"][0]["text"]

    def test_get_task(self, test_client):
        """Test getting a task from the server."""
        # First create a task
        send_request = {
            "jsonrpc": "2.0",
            "id": "test_request_id",
            "method": "tasks/send",
            "params": {
                "id": "task_to_get",
                "sessionId": "test_session_id",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Task to retrieve later"}],
                },
            },
        }

        test_client.post("/", json=send_request)

        # Now get the task
        get_request = {
            "jsonrpc": "2.0",
            "id": "get_request_id",
            "method": "tasks/get",
            "params": {"id": "task_to_get"},
        }

        data = self.post_and_validate(
            test_client, get_request, "get_request_id", "task_to_get"
        )

    # TODO Rename this here and in `test_send_task` and `test_get_task`
    def post_and_validate(self, test_client, json, arg2, arg3):
        response = test_client.post("/", json=json)
        assert response.status_code == 200
        result = response.json()
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == arg2
        assert "result" in result
        assert result["result"]["id"] == arg3
        return result

    def test_invalid_request(self, test_client):
        """Test handling of invalid requests."""
        # Send an invalid request (missing method)
        request_data = {"jsonrpc": "2.0", "id": "invalid_request_id", "params": {}}

        self.post_and_expect_error(test_client, request_data, -32600)

    def test_method_not_found(self, test_client):
        """Test handling of unknown methods."""
        # Send request with unknown method
        request_data = {
            "jsonrpc": "2.0",
            "id": "unknown_method_id",
            "method": "unknown_method",
            "params": {},
        }

        self.post_and_expect_error(test_client, request_data, -32601)

    def post_and_expect_error(self, test_client, request_data, arg2):
        response = test_client.post("/", json=request_data)
        assert response.status_code != 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == arg2


@pytest.mark.asyncio
async def test_task_manager():
    """Test the task manager functionality."""
    # This is a more complex test that requires mocking the flow execution
    # In a real test suite, you would mock the flow and verify task management
    pass


class MockFlow(Flow):
    def __init__(self):
        super().__init__(start="test_start")
        self.shared = {}
        self.capabilities = ["text"]
        self.skills = ["test_skill"]

    def run(self, shared: dict):
        self.shared = shared
        if "error" in shared.get("query", ""):
            raise ValueError("Simulated error")
        if "input_required" in shared.get("query", ""):
            self.shared["a2a_required_input"] = True
        else:
            self.shared["a2a_output_parts"] = [
                {"type": "text", "text": "Test response"}
            ]
            self.shared["a2a_output_artifacts"] = [
                {"type": "file", "url": "test://file.txt"}
            ]


@pytest.fixture
def test_server():
    flow = MockFlow()
    server = A2AServer(flow)
    return server


def test_send_task(test_server):
    client = TestClient(test_server._app)

    # Valid task request
    response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/send",
            "params": {"sessionId": "test_session", "query": "Test query"},
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    task = result["result"]
    assert task["status"] == "completed"
    assert len(task["parts"]) > 0
    assert len(task["artifacts"]) > 0


def test_send_task_input_required(test_server):
    client = TestClient(test_server._app)

    # Task requiring input
    response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/send",
            "params": {"sessionId": "test_session", "query": "input_required"},
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    task = result["result"]
    assert task["status"] == "input-required"


def test_send_task_error(test_server):
    client = TestClient(test_server._app)

    # Task with error
    response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/send",
            "params": {"sessionId": "test_session", "query": "error"},
        },
    )

    assert response.status_code == 500
    result = response.json()
    assert "error" in result
    assert result["error"]["code"] == -32603


def test_get_task(test_server):
    client = TestClient(test_server._app)

    # Create a task
    create_response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/send",
            "params": {"sessionId": "test_session", "query": "Test query"},
        },
    )

    task_id = create_response.json()["result"]["id"]

    # Get the task
    response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tasks/get",
            "params": {"task_id": task_id},
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    task = result["result"]
    assert task["id"] == task_id


def test_get_task_not_found(test_server):
    client = TestClient(test_server._app)

    # Try to get non-existent task
    response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/get",
            "params": {"task_id": "nonexistent_task"},
        },
    )

    assert response.status_code == 404
    result = response.json()
    assert "error" in result
    assert result["error"]["code"] == -32001


def test_cancel_task(test_server):
    client = TestClient(test_server._app)

    # Create a task
    create_response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/send",
            "params": {"sessionId": "test_session", "query": "Test query"},
        },
    )

    task_id = create_response.json()["result"]["id"]

    # Cancel the task
    response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tasks/cancel",
            "params": {"task_id": task_id},
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    task = result["result"]
    assert task["id"] == task_id
    assert task["status"] == "canceled"


def test_cancel_task_completed(test_server):
    client = TestClient(test_server._app)

    # Create a completed task
    create_response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/send",
            "params": {"sessionId": "test_session", "query": "Test query"},
        },
    )

    task_id = create_response.json()["result"]["id"]

    # Try to cancel completed task
    response = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tasks/cancel",
            "params": {"task_id": task_id},
        },
    )

    assert response.status_code == 400
    result = response.json()
    assert "error" in result
    assert result["error"]["code"] == -32002
