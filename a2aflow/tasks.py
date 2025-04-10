class PocketFlowTaskManager(InMemoryTaskManager):
    """Task manager that uses PocketFlow to process tasks."""

    def __init__(self, flow):
        super().__init__()
        self.flow = flow

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Handle send task request by running PocketFlow."""
        task_send_params = request.params

        # 1. Extract query from A2A request
        query = self._get_user_query(task_send_params)

        # 2. Prepare shared store with A2A context
        shared = {
            "a2a_request": request.model_dump(),
            "query": query,
            "session_id": task_send_params.sessionId,
        }

        # 3. Run PocketFlow
        self.flow.run(shared)

        # 4. Convert result to A2A Task object
        result = shared.get("result", "")
        parts = [{"type": "text", "text": result}]

        # Determine task state based on flow result
        task_state = TaskState.COMPLETED
        if "input_required" in shared:
            task_state = TaskState.INPUT_REQUIRED

        # Create and return task
        task = await self._update_store(
            task_id=task_send_params.id,
            task_send_params=task_send_params,
            task_state=task_state,
            parts=parts,
        )

        return SendTaskResponse(result=task)
