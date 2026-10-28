Project Architecture

MCP/
├── .venv/                   # Python virtual environment (managed by uv)
├── src/
│   └── mcp_app/
│       ├── __init__.py
│       ├── app.py           # Streamlit Web UI + LangGraph + MCP Client
│       └── custom_mcp_server.py # Custom MCP Server implementation
├── .env                     # Environment variables (Groq API Key)
├── pyproject.toml           # Project dependencies & configuration
└── README.md                # Project documentation


🛠️ Tech Stack & Prerequisites
Package Manager: uv (Fast Python package installer and resolver)

Python Version: >=3.12

Orchestration: langgraph & langchain

LLM Provider: groq (via langchain-groq)

Protocol: mcp (Model Context Protocol)

Frontend: streamlit

⚙️ Installation & Setup
1. Clone or Open the Project
Navigate to your project directory in the terminal:

Bash
cd path/to/MCP
2. Configure Environment Variables
Create a .env file in the root directory and add your Groq API key:

Code snippet
GROQ_API_KEY=your_groq_api_key_here
3. Install Dependencies with uv
This project uses uv for lightning-fast dependency synchronization based on pyproject.toml:

Bash
uv sync
🚀 Running the Application
This project uses an MCP server communicating over HTTP (streamable-http / streamable_http) linked to an interactive Streamlit chat interface.

Step 1: Start your MCP Server
In your first terminal window, start your custom MCP server:

Bash
uv run python src/mcp_app/custom_mcp_server.py
Step 2: Launch the Streamlit App
In your second terminal window, run the Streamlit frontend using uv run:

Bash
uv run streamlit run src/mcp_app/app.py
Open the provided local URL (typically http://localhost:8501) in your browser to chat with your agent and watch it dynamically invoke tools via MCP!

🧠 Key Concepts Covered
Model Context Protocol (MCP): Decoupling tools from AI models using standardized client-server architectures.

LangGraph State Management: Managing agent loops, conditional edges (should_continue), and message histories (MessagesState).

Tool Integration: Binding external MCP toolsets dynamically to Groq models via MCPAdapter.

Interactive UI: Building stateful chat applications using Streamlit session states.