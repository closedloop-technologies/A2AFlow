"""
Core A2AFlow classes extending PocketFlow
"""


from pocketflow import Node, AsyncNode, Flow
import asyncio
import requests
import base64


class A2ANode(Node):
    """Base Node with A2A capabilities."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, max_retries=1, wait=0):
        super().__init__(max_retries, wait)

    def prep(self, shared):
        """Extract task parameters from A2A request."""
        task_params = shared.get("a2a_request", {}).get("params", {})
        return self._get_user_query(task_params)

    def _get_user_query(self, task_params):
        """Extract user query from A2A task parameters."""
        if not task_params or not task_params.get("message", {}).get("parts"):
            return None

        part = task_params["message"]["parts"][0]
        return part.get("text", "") if part.get("type") == "text" else None


class StreamingNode(AsyncNode):
    async def exec_async(self, query):
        results = []
        # Simulate streaming results
        for i in range(5):
            results.append(f"Processing step {i+1}")
            yield {"is_task_complete": False, "content": results[-1]}
            await asyncio.sleep(0.5)

        yield {
            "is_task_complete": True,
            "content": "Final result: processed successfully",
        }


class PushNotificationNode(Node):
    def post(self, shared, prep_res, exec_res):
        # If push notification URL is configured
        if "push_notification_url" in shared:
            # Send result to callback URL
            notification = {"task_id": shared["task_id"], "result": exec_res}
            requests.post(shared["push_notification_url"], json=notification)

        return "default"


class MultiModalNode(A2ANode):
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain", "image/png", "image/jpeg"]

    def _get_user_query(self, task_params):
        """Extract text and/or images from A2A task parameters."""
        if not task_params or not task_params.get("message", {}).get("parts"):
            return None

        text_content = ""
        images = []

        for part in task_params["message"]["parts"]:
            if part.get("type") == "text":
                text_content += part.get("text", "")
            elif part.get("type") == "file" and part.get("file", {}).get(
                "mimeType", ""
            ).startswith("image/"):
                if image_data := part.get("file", {}).get("bytes"):
                    images.append(base64.b64decode(image_data))

        return {"text": text_content, "images": images}


class A2AFlow(Flow):
    """Flow with A2A protocol support."""

    def __init__(self, start, capabilities=None, skills=None, agent_card=None):
        super().__init__(start)
        self.capabilities = capabilities or {
            "streaming": False,
            "pushNotifications": False,
        }
        self.skills = skills or []
        self.agent_card = agent_card or {}
