import asyncio
from langchain.mcp import MCPAdapter
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    groq_api_key = os.getenv("GROQ_API_KEY")

    model = ChatGroq(model="openai/gpt-oss-20b", api_key=groq_api_key)

    # Setup MCP client configuration
    config = {
        "mcpServers": {
            "math": {
                "command": "uv",
                "args": [
                    "run",
                    "python",
                    r"C:\Users\Tejashvi Anand\Downloads\MCP\src\mcp_app\custom_mcp_server.py"
                ]
            }
        }
    }

    # MCPAdapter manages connection lifecycle via async context manager
    async with MCPAdapter(config) as adapter:
        tools = await adapter.list_tools()

    # Debug: Print loaded tools to ensure the server is communicating properly
    print("--- DEBUG: Loaded Tools ---")
    for t in tools:
        print(f"- {t.name}: {t.description}")
    print("--------------------------\n")

    # Bind tools with the model
    model_with_tools = model.bind_tools(tools)

    # Wrap tools in a ToolNode for LangGraph
    tool_node = ToolNode(tools)

    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    async def call_model(state: MessagesState):
        messages = state["messages"]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model", should_continue,
    )
    builder.add_edge("tools", "call_model")

    graph = builder.compile()

    # Pass a System Prompt to force tool usage alongside the user prompt
    initial_messages = [
        SystemMessage(content="You must always use the available custom tools to perform calculations. Never calculate math answers yourself."),
        HumanMessage(content="what is (4+5) by 10 then add 20 then reduce 10?")
    ]

    result = await graph.ainvoke({"messages": initial_messages})

    # Print out all interactions in the graph
    print("--- Full Conversation History ---")
    for msg in result["messages"]:
        msg_type = msg.__class__.__name__
        print(f"\n[{msg_type}]")
        print(f"Content: {msg.content}")
        
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"Tool Calls: {msg.tool_calls}")

if __name__ == "__main__":
    asyncio.run(main())