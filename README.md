<div align="center">
  <img src="https://github.com/closedloop-technologies/A2AFlow/raw/main/docs/assets/a2aflow-banner.png" width="600"/>
  <h1>A2AFlow</h1>
  <p><em>A universal translator for interoperable AI agents, built on PocketFlow + Agent2Agent (A2A)</em></p>
  
  ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
  [![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://closedloop-technologies.github.io/A2AFlow/)
</div>

---

## 🧠 What is A2AFlow?

**A2AFlow** is a lightweight, framework-agnostic bridge between [PocketFlow](https://github.com/The-Pocket/PocketFlow) and [Google’s Agent2Agent (A2A) protocol](https://github.com/google/A2A).

It lets developers build LLM agents that:

- **Communicate via a shared protocol**
- **Stream real-time responses**
- **Share capabilities across platforms**
- **Maintain context across multi-turn tasks**

> Think of it as the *HTTP for AI agents* — a drop-in protocol layer that turns your logic into something other agents can talk to.

---

## ✨ Why Use A2AFlow?

| Feature               | Description |
|-----------------------|-------------|
| 🧩 **Interoperable** | Connect your agent to any A2A-compatible service |
| 🧠 **Stateful**      | Session-aware memory for multi-turn interactions |
| 🖼️ **Multi-modal**   | Support for text, images, and structured data |
| 🚀 **Streaming**     | Emit intermediate results with async updates |
| 🔔 **Push-Ready**    | Send results via webhooks or background workers |
| 🪶 **Minimalist**    | ~200 lines of code on top of PocketFlow’s 100-line runtime |

---

## 🛠️ Quickstart

```bash
pip install a2aflow
```

```python
from a2aflow import A2ANode, A2AFlow, A2AServer

class Bot(A2ANode):
    def exec(self, query):
        return f"You said: {query}"

flow = A2AFlow(start=Bot())
server = A2AServer(flow=flow, host="localhost", port=10000)
server.start()
```

Now your agent is live and A2A-compatible! 🎉

---

## 🧪 Example Agents

### ✅ Simple Q&A

```bash
python examples/simple_agent.py
```

### 🔁 Multi-turn Form Assistant

```bash
python examples/multi_turn_agent.py
```

### 📡 Streaming Workflow Bot

```bash
python examples/streaming_agent.py
```

---

## 🌐 What Can You Build?

- Customer support agents that escalate to one another
- ETL processors that stream progress updates
- Frontends that invoke remote AI tools via shared protocol
- Autonomous workflows that route tasks between agents

---

## 🧱 Design Patterns

- **Agent**: Decision-making systems
- **Workflow**: Graph of processing steps
- **RAG**: Retrieval-augmented generation
- **MapReduce**: Split and aggregate inputs
- **Push-based**: Send updates after long-running tasks
- **Multi-agent**: Inter-agent collaboration

---

## 📚 Documentation

Full docs, agent recipes, and deployment guides available at  
👉 [https://your-username.github.io/A2AFlow](https://your-username.github.io/A2AFlow)

---

## Testing

A2AFlow uses pytest for testing. The repository is configured with various test markers for different test types:

- `unit`: Unit tests that test individual components in isolation
- `integration`: Tests that verify interactions between components
- `slow`: Tests that take longer to run

### Running Tests

```bash
# Install development dependencies
uv sync --group dev

# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=a2aflow --cov-report=term-missing

# Run only unit tests
python -m pytest -m "unit"

# Run all tests except slow ones
python -m pytest -m "not slow"
```

---

## 🤝 Contributing

Pull requests are welcome!  
Check out [`CONTRIBUTING.md`](CONTRIBUTING.md) to get started.

---

## ❤️ Credits

Built with:

- [PocketFlow](https://github.com/The-Pocket/PocketFlow): 100-line agent runtime
- [Agent2Agent Protocol](https://github.com/google/A2A): Agent comms spec

Made with ❤️ by ClosedLoop and the open-source community.
