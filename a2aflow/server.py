"""
A2A Server implementation for PocketFlow
"""

from fastapi import FastAPI, Request, Response
from uvicorn import run as uvicorn_run
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel

from .tasks import (
    PocketFlowTaskManager,
    SendTaskRequest,
    SendTaskResponse,
    TaskNotFoundError,
    TaskNotCancelableError
)

class A2AServer:
    """A2A Server implementation backed by PocketFlow."""

    def __init__(
        self, flow, host="localhost", port=10000, agent_card=None, task_manager=None
    ):
        self.flow = flow
        self.host = host
        self.port = port
        self.agent_card = agent_card or self._create_default_agent_card()
        self.task_manager = task_manager or PocketFlowTaskManager(self.flow)
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
                            "id": body.get("id"),
                            "error": {"code": -32600, "message": "Invalid request"},
                        },
                        media_type="application/json",
                        status_code=400,
                    )

                if method == "tasks/send":
                    return await self._handle_send_task(body)
                elif method == "tasks/get":
                    return await self._handle_get_task(body)
                elif method == "tasks/cancel":
                    return await self._handle_cancel_task(body)
                else:
                    return Response(
                        content={
                            "jsonrpc": "2.0",
                            "id": body.get("id"),
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
                        "id": body.get("id"),
                        "error": {"code": -32603, "message": str(e)},
                    },
                    media_type="application/json",
                    status_code=500,
                )

        uvicorn_run(self._app, host=self.host, port=self.port)

    async def _handle_send_task(self, request):
        """Handle tasks/send request using PocketFlow."""
        try:
            # Parse request
            send_task_request = SendTaskRequest(**request)
            
            # Process through task manager
            response = await self.task_manager.on_send_task(send_task_request)
            
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response.result.dict(),
                },
                media_type="application/json",
            )
        except Exception as e:
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": str(e)},
                },
                media_type="application/json",
                status_code=500,
            )

    async def _handle_get_task(self, request):
        """Handle tasks/get request."""
        try:
            task_id = request["params"].get("task_id")
            if not task_id:
                return Response(
                    content={
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "Invalid params"},
                    },
                    media_type="application/json",
                    status_code=400,
                )

            task = await self.task_manager.on_get_task(task_id)
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": task.dict(),
                },
                media_type="application/json",
            )
        except TaskNotFoundError as e:
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": e.code, "message": e.message},
                },
                media_type="application/json",
                status_code=404,
            )
        except Exception as e:
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": str(e)},
                },
                media_type="application/json",
                status_code=500,
            )

    async def _handle_cancel_task(self, request):
        """Handle tasks/cancel request."""
        try:
            task_id = request["params"].get("task_id")
            if not task_id:
                return Response(
                    content={
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32602, "message": "Invalid params"},
                    },
                    media_type="application/json",
                    status_code=400,
                )

            task = await self.task_manager.on_cancel_task(task_id)
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": task.dict(),
                },
                media_type="application/json",
            )
        except TaskNotFoundError as e:
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": e.code, "message": e.message},
                },
                media_type="application/json",
                status_code=404,
            )
        except TaskNotCancelableError as e:
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": e.code, "message": e.message},
                },
                media_type="application/json",
                status_code=400,
            )
        except Exception as e:
            return Response(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": str(e)},
                },
                media_type="application/json",
                status_code=500,
            )
