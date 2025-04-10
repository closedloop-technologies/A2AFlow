import pytest
from unittest.mock import Mock, patch

from pocketflow import Flow, Node
from a2aflow.core import A2ANode, A2AFlow


class TestA2ANode:
    """Tests for the A2ANode class extending PocketFlow's Node."""

    def test_initialization(self):
        """Test basic initialization of A2ANode."""
        node = A2ANode(max_retries=3, wait=5)
        assert node.max_retries == 3
        assert node.wait == 5
        assert node.SUPPORTED_CONTENT_TYPES == ["text", "text/plain"]

    def test_get_user_query(self):
        """Test extracting user query from A2A task parameters."""
        node = A2ANode()

        # Test with valid text part
        task_params = {
            "message": {"parts": [{"type": "text", "text": "Hello, world!"}]}
        }
        assert node._get_user_query(task_params) == "Hello, world!"

        # Test with empty parts
        task_params = {"message": {"parts": []}}
        assert node._get_user_query(task_params) is None

        # Test with missing parts
        task_params = {"message": {}}
        assert node._get_user_query(task_params) is None

        # Test with missing message
        task_params = {}
        assert node._get_user_query(task_params) is None

        # Test with non-text part
        task_params = {
            "message": {
                "parts": [
                    {
                        "type": "file",
                        "file": {"mimeType": "image/png", "bytes": "base64data"},
                    }
                ]
            }
        }
        assert node._get_user_query(task_params) is None

    def test_prep(self):
        """Test prep method extracting from A2A request."""
        node = A2ANode()

        # Test with valid request
        shared = {
            "a2a_request": {
                "params": {
                    "message": {"parts": [{"type": "text", "text": "Hello, world!"}]}
                }
            }
        }
        assert node.prep(shared) == "Hello, world!"

        # Test with missing request
        shared = {}
        assert node.prep(shared) is None

    def test_exec_and_post(self):
        """Test that exec and post methods can be overridden."""

        class TNode(A2ANode):
            def exec(self, query):
                return f"Response: {query}"

            def post(self, shared, prep_res, exec_res):
                shared["result"] = exec_res
                return "custom_action"

        node = TNode()
        shared = {
            "a2a_request": {
                "params": {
                    "message": {"parts": [{"type": "text", "text": "Test query"}]}
                }
            }
        }

        action = node.run(shared)
        assert action == "custom_action"
        assert shared["result"] == "Response: Test query"


class TestA2AFlow:
    """Tests for the A2AFlow class extending PocketFlow's Flow."""

    def test_initialization(self):
        """Test basic initialization of A2AFlow."""
        mock_node = Mock(spec=Node)
        capabilities = {"streaming": True, "pushNotifications": False}
        skills = [{"id": "1", "name": "Test skill"}]
        agent_card = {"name": "Test Agent", "version": "1.0.0"}

        flow = A2AFlow(
            start=mock_node,
            capabilities=capabilities,
            skills=skills,
            agent_card=agent_card,
        )

        assert flow.start == mock_node
        assert flow.capabilities == capabilities
        assert flow.skills == skills
        assert flow.agent_card == agent_card

    def test_default_values(self):
        """Test default values when not provided."""
        mock_node = Mock(spec=Node)
        flow = A2AFlow(start=mock_node)

        assert flow.capabilities == {"streaming": False, "pushNotifications": False}
        assert flow.skills == []
        assert flow.agent_card == {}

    @patch.object(Flow, "run")
    def test_run_method(self, mock_run):
        """Test that run method calls parent class run method."""
        mock_node = Mock(spec=Node)
        flow = A2AFlow(start=mock_node)
        shared = {"test": "data"}

        flow.run(shared)
        mock_run.assert_called_once_with(shared)

    def test_with_real_nodes(self):
        """Test A2AFlow with real A2ANodes."""

        class QueryNode(A2ANode):
            def exec(self, query):
                return f"Processed: {query}"

            def post(self, shared, prep_res, exec_res):
                shared["result"] = exec_res
                return "next"

        class ResponseNode(A2ANode):
            def exec(self, query):
                return "Final response"

            def post(self, shared, prep_res, exec_res):
                shared["final"] = exec_res
                return "end"

        query_node = QueryNode()
        response_node = ResponseNode()

        # Connect nodes
        query_node - "next" >> response_node

        # Create flow
        flow = A2AFlow(
            start=query_node,
            capabilities={"streaming": True},
            skills=[{"id": "qa", "name": "Q&A"}],
        )

        # Execute flow
        shared = {
            "a2a_request": {
                "params": {
                    "message": {"parts": [{"type": "text", "text": "Test query"}]}
                }
            }
        }

        flow.run(shared)

        # Check results
        assert shared["result"] == "Processed: Test query"
        assert shared["final"] == "Final response"
