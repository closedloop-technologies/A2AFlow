# 1. Define your agent nodes and flow
class QueryHandlerNode(A2ANode):
    def exec(self, query):
        # Process the query
        return f"Response to: {query}"


# 2. Create a PocketFlow with A2A capabilities
query_node = QueryHandlerNode()
flow = A2AFlow(
    start=query_node,
    capabilities={"streaming": True, "pushNotifications": False},
    skills=[{"id": "1", "name": "Question answering"}],
)

# 3. Create and start the A2A server
server = PocketFlowA2AServer(flow=flow, host="localhost", port=10000)
server.start()
