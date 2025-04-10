from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class TaskStatus(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

class Task(BaseModel):
    id: str
    status: TaskStatus
    sessionId: str
    createdAt: str
    updatedAt: str
    parts: Optional[List[Dict[str, Any]]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None
    error: Optional[Dict[str, Any]] = None

class SendTaskRequest(BaseModel):
    method: str
    id: str
    params: Dict[str, Any]

class SendTaskResponse(BaseModel):
    result: Task

class TaskNotFoundError(Exception):
    code = -32001
    message = "Task not found"

class TaskNotCancelableError(Exception):
    code = -32002
    message = "Task cannot be canceled"

class PocketFlowTaskManager:
    """Task manager that uses PocketFlow to process tasks."""

    def __init__(self, flow):
        self.flow = flow
        self.tasks: Dict[str, Task] = {}
        self.next_id = 1

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Handle send task request by running PocketFlow."""
        task_send_params = request.params
        
        # Create new task
        task_id = f"task_{self.next_id}"
        self.next_id += 1

        # Initialize task in submitted state
        task = Task(
            id=task_id,
            status=TaskStatus.SUBMITTED,
            sessionId=task_send_params["sessionId"],
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat(),
        )
        self.tasks[task_id] = task

        try:
            # Prepare shared store with A2A context
            shared = {
                "a2a_request": request.model_dump(),
                "query": task_send_params["query"],
                "session_id": task_send_params["sessionId"],
                "task_id": task_id,
            }

            # Update task status to working
            task.status = TaskStatus.WORKING
            task.updatedAt = datetime.now().isoformat()
            
            # Run PocketFlow
            self.flow.run(shared)

            # Process results
            parts = shared.get("a2a_output_parts", [])
            artifacts = shared.get("a2a_output_artifacts", [])

            # Determine final task state
            if "a2a_required_input" in shared:
                task.status = TaskStatus.INPUT_REQUIRED
            elif "error" in shared:
                task.status = TaskStatus.FAILED
                task.error = shared["error"]
            else:
                task.status = TaskStatus.COMPLETED

            # Update task with results
            task.parts = parts
            task.artifacts = artifacts
            task.updatedAt = datetime.now().isoformat()

            return SendTaskResponse(result=task)

        except Exception as e:
            # Handle flow execution errors
            task.status = TaskStatus.FAILED
            task.error = {
                "code": -32603,
                "message": str(e)
            }
            task.updatedAt = datetime.now().isoformat()
            raise

    async def on_get_task(self, task_id: str) -> Task:
        """Get task by ID."""
        task = self.tasks.get(task_id)
        if not task:
            raise TaskNotFoundError()
        return task

    async def on_cancel_task(self, task_id: str) -> Task:
        """Cancel a task."""
        task = self.tasks.get(task_id)
        if not task:
            raise TaskNotFoundError()

        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED]:
            raise TaskNotCancelableError()

        task.status = TaskStatus.CANCELED
        task.updatedAt = datetime.now().isoformat()
        return task
