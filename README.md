<div align="center">
  <img src="https://github.com/your-username/A2AFlow/raw/main/docs/assets/a2aflow-banner.png" width="600"/>
  <h1>A2AFlow</h1>
  <p><em>A lightweight, framework-agnostic bridge between PocketFlow and the Agent2Agent protocol</em></p>
  
  ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
  [![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://your-username.github.io/A2AFlow/)
  <a href="https://discord.gg/your-invite-link">
    <img src="https://img.shields.io/discord/1234567890?logo=discord&style=flat">
  </a>
</div>

## Overview

A2AFlow combines the minimalist approach of [PocketFlow](https://github.com/The-Pocket/PocketFlow) with Google's [Agent2Agent (A2A) protocol](https://github.com/google/A2A), creating a powerful yet lightweight framework for building interoperable AI agents.

- **Lightweight**: Just ~200 lines of core code built on PocketFlow's 100-line foundation
- **Interoperable**: Seamlessly connect with any A2A-compatible agent
- **Framework-agnostic**: Works with any LLM provider or agent framework
- **Clean abstractions**: Simple, intuitive API that follows PocketFlow's design philosophy

## Features

- **A2A Protocol Support**: Full implementation of the A2A protocol specification
- **Graph-based Processing**: Use PocketFlow's intuitive directed graph structure for agent logic
- **Streaming Responses**: Real-time updates for longer processing tasks
- **Push Notifications**: Server-initiated communication for background processing
- **Multi-modal Content**: Support for text, images, structured data, and more
- **Session Management**: Built-in state tracking across multiple interactions
- **Tool Integration**: Easy integration with external tools and API calls

## Installation

### Using UV (Recommended)

```bash
# Install UV if you don't have it already
pip install uv

# Install A2AFlow
uv sync
```

### Using Pip

```bash
pip install a2aflow
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/your-username/A2AFlow.git
cd A2AFlow

# Using UV (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --group dev --group docs

# Using Pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,docs]"
```

## Quick Start

### Create an A2A-Compatible Agent

```python
from a2aflow import A2ANode, A2AFlow, A2AServer

# 1. Define your agent node
class QuestionAnswerNode(A2ANode):
    def exec(self, query):
        return f"The answer to '{query}' is 42!"

# 2. Create a flow with A2A capabilities
qa_node = QuestionAnswerNode()
flow = A2AFlow(
    start=qa_node,
    capabilities={"streaming": True, "pushNotifications": False},
    skills=[{"id": "qa_skill", "name": "Question answering"}]
)

# 3. Start the A2A server
server = A2AServer(
    flow=flow,
    host="localhost",
    port=10000
)
server.start()
```

### Connect to an A2A Agent

```python
from a2aflow import A2AClient

# Connect to an A2A server
client = A2AClient(url="http://localhost:10000")

# Send a task and get response
response = await client.send_task("What is the meaning of life?")
print(response["result"]["status"]["message"]["parts"][0]["text"])
# Output: The answer to 'What is the meaning of life?' is 42!
```

## More Examples

### Streaming Agent

```python
from a2aflow import AsyncA2ANode, A2AFlow, A2AServer
import asyncio

class StreamingNode(AsyncA2ANode):
    async def exec_async(self, query):
        for i in range(5):
            yield f"Processing step {i+1}..."
            await asyncio.sleep(0.5)
        yield f"Final answer: {query} → Completed!"

# Create and start server with streaming capabilities
flow = A2AFlow(start=StreamingNode(), capabilities={"streaming": True})
server = A2AServer(flow, host="localhost", port=10000)
server.start()
```

### Multi-turn Agent with Memory

```python
from a2aflow import A2ANode, A2AFlow, A2AServer

class ConversationNode(A2ANode):
    def prep(self, shared):
        # Initialize conversation history
        if "history" not in shared:
            shared["history"] = []
        
        # Get query and pass history for context
        query = self._get_user_query(shared.get("a2a_request", {}).get("params", {}))
        return {"query": query, "history": shared["history"]}
    
    def exec(self, inputs):
        query, history = inputs["query"], inputs["history"]
        
        # Simple response based on history length
        if not history:
            response = f"Hello! You said: {query}"
        else:
            response = f"You've sent {len(history)+1} messages. Most recent: {query}"
        
        return response
    
    def post(self, shared, prep_res, exec_res):
        # Update conversation history
        shared["history"].append({"query": prep_res["query"], "response": exec_res})
        return "default"

# Create and start conversation agent
flow = A2AFlow(start=ConversationNode())
server = A2AServer(flow, host="localhost", port=10000)
server.start()
```

## Documentation

For more detailed documentation, examples, and tutorials, visit our [documentation site](https://your-username.github.io/A2AFlow/).

## Design Patterns

A2AFlow supports all the design patterns from PocketFlow:

- **Agent**: Build agentic systems that make decisions based on context
- **RAG**: Implement Retrieval Augmented Generation for context-aware responses
- **MapReduce**: Process large inputs by splitting and then aggregating
- **Multi-Agent**: Create collaborative agent systems
- **Workflow**: Chain multiple steps for complex tasks

Plus A2A-specific patterns:

- **Agent Discovery**: Auto-discover agent capabilities through Agent Cards
- **Multi-modal Conversations**: Exchange text, images, and structured data
- **Push-Based Background Processing**: Process tasks asynchronously with callbacks

## A2A Protocol Support

A2AFlow implements the full A2A protocol specification:

- **Agent Card**: Well-known endpoint with agent capabilities
- **Task Management**: Create, monitor, and cancel tasks
- **Streaming**: Real-time progress updates
- **Push Notifications**: Server-initiated callbacks
- **Multi-modal Content**: Support for text, files, and structured data

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

### Development Setup

We recommend using UV for development:

```bash
# Clone the repository
git clone https://github.com/your-username/A2AFlow.git
cd A2AFlow

# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies including development and documentation groups
uv sync --group dev --group docs

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

A2AFlow is built on two amazing projects:

- [PocketFlow](https://github.com/The-Pocket/PocketFlow): A minimalist LLM framework in 100 lines
- [Agent2Agent (A2A) Protocol](https://github.com/google/A2A): An open protocol for agent communication

Special thanks to all contributors to both projects.

---

<div align="center">
  <p>Built with ❤️ by ClosedLoop and the community</p>
</div>
