"""
A2A Server implementation for PocketFlow
"""

from fastapi import FastAPI, Request, Response
from uvicorn import run as uvicorn_run
from typing import Dict, Any, Optional, List
from datetime import datetime


class InMemoryTaskManager:
    """In-memory task manager for A2A server."""

    def __init__(self, flow):
        self.flow = flow
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.next_id = 1

    def create_task(self, params: Dict[str, Any]) -> str:
        """Create a new task."""
        task_id = f"task_{self.next_id}"
        self.next_id += 1
        
        self.tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "params": params,
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
        }
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None, error: Optional[Dict[str, Any]] = None):
        """Update task status and result/error."""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if result is not None:
                self.tasks[task_id]["result"] = result
            if error is not None:
                self.tasks[task_id]["error"] = error


class A2AServer:
    """A2A Server implementation backed by PocketFlow."""

    def __init__(
        self, flow, host="localhost", port=10000, agent_card=None, task_manager=None
    ):
        self.flow = flow
        self.host = host
        self.port = port
        self.agent_card = agent_card or self._create_default_agent_card()
        self.task_manager = task_manager or InMemoryTaskManager(self.flow)
        self._app = FastAPI()

    def _create_default_agent_card(self):
        """Create a default agent card based on flow capabilities."""
        return {
            "name": "PocketFlow Agent",
            "version": "1.0.0",
            "url": f"http://{self.host}:{self.port}",
            "capabilities": self.flow.capabilities,
            "skills": self.flow.skills,
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
        }

    def start(self):
        """Start the A2A server."""

        @self._app.get("/.well-known/agent.json")
        def get_agent_card():
            return Response(content=self.agent_card, media_type="application/json")

        @self._app.post("/")
        async def handle_request(request: Request):
            try:
                body = await request.json()
                
                # Validate A2A request
                method = body.get("method")
                if not method:
                    return Response(
                        content={
                            "jsonrpc": "2.0",
                            "error": {"code": -32600, "message": "Invalid request"},
                        },
                        media_type="application/json",
                        status_code=400,
                    )

                if method == "tasks/send":
                    return await self._handle_send_task(body)
                elif method == "tasks/sendSubscribe":
                    return await self._handle_send_task_streaming(body)
                elif method == "tasks/get":
                    return await self._handle_get_task(body)
                else:
                    return Response(
                        content={
                            "jsonrpc": "2.0",
                            "error": {"code": -32601, "message": "Method not found"},
                        },
                        media_type="application/json",
                        status_code=404,
                    )
            except Exception as e:
                # Handle error according to A2A spec
                return Response(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": str(e)},
                    },
                    media_type="application/json",
                    status_code=500,
                )

        uvicorn_run(self._app, host=self.host, port=self.port)

    async def _handle_send_task(self, request):
        """Handle tasks/send request using PocketFlow."""
        # 1. Convert A2A request to PocketFlow shared store
        shared = {"a2a_request": request}

        # 2. Run the flow
        self.flow.run(shared)

        # 3. Convert PocketFlow result back to A2A response format
        task_result = self._create_task_response(shared, request)

        return Response(
            content={
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": task_result,
            },
            media_type="application/json",
        )

    async def _handle_get_task(self, request):
        """Handle tasks/get request."""
        task_id = request["params"].get("task_id")
        if not task_id:
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Invalid params"},
                },
                media_type="application/json",
                status_code=400,
            )

        task = self.task_manager.get_task(task_id)
        if not task:
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": "Task not found"},
                },
                media_type="application/json",
                status_code=404,
            )

        return Response(
            content={
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "status": task["status"],
                    "result": task["result"],
                    "error": task["error"],
                },
            },
            media_type="application/json",
        )

    def _create_task_response(self, shared: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Create A2A task response from PocketFlow shared store."""
        # Extract task parameters and create task
        task_id = self.task_manager.create_task(request["params"])
        
        # Get result from shared store and determine status
        result = shared.get("result")
        status = "completed" if result is not None else "pending"
        
        # Return formatted response
        return {
            "task_id": task_id,
            "status": status,
            "result": result,
        }
