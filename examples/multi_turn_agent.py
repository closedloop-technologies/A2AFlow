#!/usr/bin/env python3
"""
Multi-turn A2A Agent Example

This example demonstrates how to create an A2A-compatible agent that supports
multi-turn conversations. The agent gathers information over multiple interactions
and maintains state between turns.
"""

import argparse
import logging
import re
import sys
from enum import Enum, auto

from a2aflow import A2ANode, A2AFlow, A2AServer


class FormState(Enum):
    """Enumeration of possible form states."""

    INITIAL = auto()
    ASKING_NAME = auto()
    ASKING_EMAIL = auto()
    ASKING_PURPOSE = auto()
    COMPLETED = auto()


class FormCompletionNode(A2ANode):
    """Node that demonstrates multi-turn form completion."""

    def prep(self, shared):
        """Prepare by retrieving conversation state from shared store."""
        # Initialize the form state if it doesn't exist
        session_id = self._get_session_id(shared.get("a2a_request", {}))

        # Retrieve or initialize session data
        if "sessions" not in shared:
            shared["sessions"] = {}

        if session_id not in shared["sessions"]:
            shared["sessions"][session_id] = {
                "state": FormState.INITIAL,
                "form_data": {"name": None, "email": None, "purpose": None},
            }

        # Get the query from the A2A request
        query = self._get_user_query(shared.get("a2a_request", {}).get("params", {}))

        # Return both the session data and query
        return {
            "session": shared["sessions"][session_id],
            "query": query,
            "session_id": session_id,
        }

    def exec(self, inputs):
        """Process current input based on form state."""
        session = inputs["session"]
        query = inputs["query"]
        state = session["state"]
        form_data = session["form_data"]

        # Initial state - welcome and ask for name
        if state == FormState.INITIAL:
            session["state"] = FormState.ASKING_NAME
            return "Welcome to the form completion agent! To get started, please tell me your name."

        elif state == FormState.ASKING_NAME:
            if not query or len(query.strip()) <= 0:
                return "I didn't catch that. Could you please tell me your name?"

            form_data["name"] = query.strip()
            session["state"] = FormState.ASKING_EMAIL
            return (
                f"Thanks, {form_data['name']}! Now, please provide your email address."
            )
        elif state == FormState.ASKING_EMAIL:
            # Validate email format
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, query.strip()):
                return "That doesn't look like a valid email address. Please provide a valid email."

            form_data["email"] = query.strip()
            session["state"] = FormState.ASKING_PURPOSE
            return (
                "Great! Finally, could you briefly explain the purpose of your inquiry?"
            )
        elif state == FormState.ASKING_PURPOSE:
            if not query or len(query.strip()) <= 0:
                return "I didn't catch that. Could you please explain the purpose of your inquiry?"

            form_data["purpose"] = query.strip()
            session["state"] = FormState.COMPLETED

            return f"""
                Thank you! Your form has been completed. Here's a summary:
                
                Name: {form_data['name']}
                Email: {form_data['email']}
                Purpose: {form_data['purpose']}
                
                Is there anything else you'd like to do? You can type 'reset' to start over.
                """
        elif state == FormState.COMPLETED:
            return self._extracted_from_exec_(query, form_data, session)
        # Fallback for unexpected states
        return "Sorry, something went wrong. Let's start over. What is your name?"

    # TODO Rename this here and in `exec`
    def _extracted_from_exec_(self, query, form_data, session):
        if query.lower() != "reset":
            return f"Your form is already complete, {form_data['name']}. Type 'reset' to start over or ask me something else."

        # Reset the form
        form_data["name"] = None
        form_data["email"] = None
        form_data["purpose"] = None
        session["state"] = FormState.ASKING_NAME
        return "Let's start over. What is your name?"

    def post(self, shared, prep_res, exec_res):
        """Update session state in the shared store and return default action."""
        # Session data is already updated in the prep_res reference
        # There's nothing special to do here for this example
        return "default"

    def _get_session_id(self, request):
        """Extract session ID from A2A request."""
        if not request:
            return "default_session"
        params = request.get("params", {})
        return params.get("sessionId", "default_session")


def main():
    """Run the multi-turn example agent."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a multi-turn A2A agent")
    parser.add_argument(
        "--host", default="localhost", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=10000, help="Port to bind the server to"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("multi_turn_agent")

    try:
        # Create the form completion node
        form_node = FormCompletionNode()

        # Create the A2A flow with input-required capability
        flow = A2AFlow(
            start=form_node,
            capabilities={"streaming": False, "pushNotifications": False},
            skills=[
                {
                    "id": "form_completion",
                    "name": "Form completion",
                    "description": "Guides users through a multi-step form completion process",
                }
            ],
        )

        # Create and start the A2A server
        logger.info(f"Starting multi-turn A2A server on {args.host}:{args.port}")
        server = A2AServer(flow=flow, host=args.host, port=args.port)
        server.start()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
