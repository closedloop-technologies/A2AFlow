def convert_shared_to_task(shared, task_id, session_id):
    """Convert PocketFlow shared store to A2A Task."""
    # Extract results from shared store
    result = shared.get("result", "")

    # Create A2A parts
    parts = [{"type": "text", "text": result}]

    # Determine task state
    task_state = TaskState.COMPLETED
    if shared.get("input_required"):
        task_state = TaskState.INPUT_REQUIRED

    # Create message and status
    message = Message(role="agent", parts=parts)
    status = TaskStatus(state=task_state, message=message)

    # Create and return task
    return Task(id=task_id, sessionId=session_id, status=status)


def convert_task_to_shared(task):
    """Convert A2A Task to PocketFlow shared store."""
    shared = {}

    # Extract message parts
    if task.status and task.status.message and task.status.message.parts:
        for part in task.status.message.parts:
            if part.get("type") == "text":
                shared["result"] = part.get("text", "")

    # Set state information
    if task.status and task.status.state:
        shared["task_state"] = task.status.state
        if task.status.state == TaskState.INPUT_REQUIRED:
            shared["input_required"] = True

    # Set session information
    shared["task_id"] = task.id
    shared["session_id"] = task.sessionId

    return shared
