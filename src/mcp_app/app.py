import asyncio
import os
from dotenv import load_dotenv
import streamlit as st
from langchain.mcp import MCPAdapter
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

load_dotenv()

st.set_page_config(page_title="MCP LangGraph Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 MCP LangGraph Chatbot with Groq")

# Initialize session state for message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You must always use the available custom tools to perform calculations. Never calculate math answers yourself.")
    ]

# Async function to execute the LangGraph pipeline with MCP
async def process_query(user_query):
    groq_api_key = os.getenv("GROQ_API_KEY")
    model = ChatGroq(model="openai/gpt-oss-20b", api_key=groq_api_key)

    # Pass the HTTP/Streamable HTTP server URL directly as a string
    async with MCPAdapter("http://127.0.0.1:8000/mcp") as adapter:
        tools = await adapter.list_tools()

    model_with_tools = model.bind_tools(tools)
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
    builder.add_conditional_edges("call_model", should_continue)
    builder.add_edge("tools", "call_model")

    graph = builder.compile()

    # Append the new user message to state history
    st.session_state.messages.append(HumanMessage(content=user_query))

    # Invoke graph with the full history
    result = await graph.ainvoke({"messages": st.session_state.messages})
    
    # Update state messages with the complete conversation trace
    st.session_state.messages = result["messages"]
    return result["messages"]

# Render previous chat history (ignoring SystemMessage for clean UI display)
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage) and msg.content:
        with st.chat_message("assistant"):
            st.write(msg.content)
    elif isinstance(msg, ToolMessage):
        with st.chat_message("ai", avatar="🔧"):
            st.write(f"**Tool Output:** {msg.content}")

# Streamlit chat input box
if user_input := st.chat_input("Ask your question..."):
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and invoking MCP tools..."):
            try:
                # Safely run the async function in Streamlit's event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response_messages = loop.run_until_complete(process_query(user_input))
                
                # Display the latest AI text response
                final_content = response_messages[-1].content
                st.write(final_content)
            except Exception as e:
                st.error(f"Error connecting to MCP server: {e}")