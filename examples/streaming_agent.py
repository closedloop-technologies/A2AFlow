#!/usr/bin/env python3
"""
Streaming A2A Agent Example

This example demonstrates how to create an A2A-compatible agent with streaming support
using A2AFlow. The agent performs a simulated step-by-step processing task and
streams updates to the client in real-time.
"""


import argparse
import asyncio
import contextlib
import logging
import sys
import time

from a2aflow import AsyncA2ANode, A2AFlow, A2AServer


class StreamingProcessingNode(AsyncA2ANode):
    """Node that demonstrates streaming updates during processing."""

    async def exec_async(self, query):
        """Process the query with streaming updates."""
        # Parse out how many steps to simulate
        steps = 5  # Default
        if "steps=" in query:
            with contextlib.suppress(ValueError, IndexError):
                steps_str = query.split("steps=")[1].split()[0]
                steps = int(steps_str)
                # Limit steps to a reasonable range
                steps = max(2, min(steps, 20))
        # Start processing
        yield f"Starting to process your query: '{query}'"
        await asyncio.sleep(0.5)

        # Simulate a multi-step processing workflow
        for i in range(1, steps + 1):
            # Simulate different processing stages
            if i == 1:
                yield f"Step {i}/{steps}: Analyzing query..."
            elif i == 2:
                yield f"Step {i}/{steps}: Retrieving relevant information..."
            elif i == steps - 1:
                yield f"Step {i}/{steps}: Finalizing results..."
            elif i == steps:
                yield f"Step {i}/{steps}: Complete!"
            else:
                yield f"Step {i}/{steps}: Processing... ({int(i/steps * 100)}% complete)"

            # Simulate variable processing time
            delay = 0.2 + (i % 3) * 0.3
            await asyncio.sleep(delay)

        # Generate final answer
        await asyncio.sleep(0.7)
        yield f"Final answer for '{query}':\nProcessing completed successfully in {steps} steps!"


def stream_processing_server(logger, args):
    # Create the streaming agent node
    streaming_node = StreamingProcessingNode()

    # Create the A2A flow with streaming capability
    flow = A2AFlow(
        start=streaming_node,
        capabilities={"streaming": True, "pushNotifications": False},
        skills=[
            {
                "id": "stream_processing",
                "name": "Streaming processing",
                "description": "Demonstrates step-by-step processing with real-time updates",
                "examples": ["Process this with steps=10", "Analyze this data"],
            }
        ],
    )

    # Create and start the A2A server
    logger.info(f"Starting streaming A2A server on {args.host}:{args.port}")
    logger.info(
        "Try a query like 'Process this with steps=10' to control the number of steps"
    )
    server = A2AServer(flow=flow, host=args.host, port=args.port)
    server.start()


def main():
    """Run the streaming example agent."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a streaming A2A agent")
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
    logger = logging.getLogger("streaming_agent")

    try:
        stream_processing_server(logger, args)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
