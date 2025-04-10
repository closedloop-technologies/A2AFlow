#!/usr/bin/env python3
"""
Simple A2A Agent Example

This example demonstrates how to create a basic A2A-compatible agent using A2AFlow.
It creates a simple question-answering agent that responds to user queries.
"""

import argparse
import logging
import sys

from a2aflow import A2ANode, A2AFlow, A2AServer


class QuestionAnswerNode(A2ANode):
    """Simple node that responds to questions with predefined answers."""

    def exec(self, query):
        """Process the query and return a response."""
        # Handle common questions with predefined answers
        if "hello" in query.lower() or "hi" in query.lower():
            return "Hello! I'm a simple A2A agent. How can I help you today?"

        if "name" in query.lower():
            return "I'm a Simple A2A Agent, built with A2AFlow!"

        if "help" in query.lower():
            return (
                "I can answer basic questions. Try asking about my name or say hello!"
            )

        if "bye" in query.lower() or "goodbye" in query.lower():
            return "Goodbye! Have a great day!"

        # Default response for other queries
        return f"You asked: '{query}'. I'm a simple agent and don't know much yet."


def main():
    """Run the example agent."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a simple A2A agent")
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
    logger = logging.getLogger("simple_agent")

    try:
        # Create the agent node
        qa_node = QuestionAnswerNode()

        # Create the A2A flow with capabilities
        flow = A2AFlow(
            start=qa_node,
            capabilities={"streaming": False, "pushNotifications": False},
            skills=[
                {
                    "id": "qa_skill",
                    "name": "Question answering",
                    "description": "Can answer basic questions about greetings and identity",
                }
            ],
        )

        # Create and start the A2A server
        logger.info(f"Starting A2A server on {args.host}:{args.port}")
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
