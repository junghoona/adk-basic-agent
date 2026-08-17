from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from .custom_functions import get_fx_rate
from .custom_agents import google_search_agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import os


root_agent = Agent(
    model='gemini-3.1-flash-lite',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[
        FunctionTool(get_fx_rate),
        AgentTool(agent=google_search_agent),
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[ "-y", "mongodb-mcp-server", "--readOnly", # Remove for write operations
                    ],
                    env={
                        # mongodb-mcp-server requires Node >=20; prepend a compatible
                        # Node install so npx doesn't resolve the older `node` on PATH.
                        "PATH": os.path.expanduser("~/.nvm/versions/node/v24.19.0/bin") + os.pathsep + os.environ.get("PATH", ""),
                        # For database access, use:
                        "MDB_MCP_CONNECTION_STRING": os.getenv("MDB_MCP_CONNECTION_STRING"),
                        # For Atlas management, use:
                        "MDB_MCP_API_CLIENT_ID": os.getenv("MDB_MCP_API_CLIENT_ID"),
                        "MDB_MCP_API_CLIENT_SECRET": os.getenv("MDB_MCP_API_CLIENT_SECRET"),
                    },
                ),
                timeout=60,
            ),
        )
    ],
)
