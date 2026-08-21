# adk-agents

A [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) agent that answers user questions and can:

- Look up live currency exchange rates (`get_fx_rate`, via [CurrencyFreaks](https://currencyfreaks.com/)).
- Delegate real-time lookups to a `google_search_agent` sub-agent that uses ADK's native Google Search tool.
- Query a MongoDB Atlas cluster / manage Atlas resources through the official [MongoDB MCP Server](https://github.com/mongodb-js/mongodb-mcp-server), wired in as an `McpToolset`.

The agent lives in [basic_agent/](basic_agent/), with the root agent defined in [basic_agent/agent.py](basic_agent/agent.py).

## Prerequisites

- Python 3.12+
- [Node.js 20+](https://nodejs.org/) and `npx` — required to launch the MongoDB MCP server (`npx -y mongodb-mcp-server`). If you manage Node with `nvm`, note that [basic_agent/agent.py](basic_agent/agent.py) currently hardcodes a specific nvm Node path onto `PATH` — update that path (or remove the override) to match the Node version installed on your machine.
- A Google API key for Gemini (or a Vertex AI / enterprise setup) — see [Google AI Studio](https://aistudio.google.com/).
- A [CurrencyFreaks](https://currencyfreaks.com/) API key (free tier works) for the FX rate tool.
- A MongoDB Atlas project — see the [MongoDB Atlas MCP setup](#mongodb-atlas-mcp-setup) section below for credentials.

## Setup

1. **Create and activate a virtual environment** (this project was set up with [uv](https://docs.astral.sh/uv/), but plain `venv` works too):

   ```bash
   uv venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   uv pip install google-adk requests python-dotenv
   ```

   (or `pip install google-adk requests python-dotenv` if not using `uv`)

3. **Create a `.env` file inside `basic_agent/`** (ADK automatically loads it for the agent at startup):

   ```bash
   basic_agent/.env
   ```

   with the following variables:

   ```dotenv
   # Gemini access
   GOOGLE_API_KEY=your-gemini-api-key
   GOOGLE_GENAI_USE_ENTERPRISE=0   # set to 1 to use Vertex AI / enterprise auth instead

   # CurrencyFreaks (for get_fx_rate)
   CF_API_KEY=your-currencyfreaks-api-key

   # MongoDB Atlas MCP (see below)
   MDB_MCP_CONNECTION_STRING=your-atlas-connection-string
   MDB_MCP_API_CLIENT_ID=your-atlas-api-client-id
   MDB_MCP_API_CLIENT_SECRET=your-atlas-api-client-secret
   ```

   `basic_agent/.gitignore` already excludes `.env`, so it will not be committed.

## Running the agent

From the repository root, with your virtual environment active:

```bash
# Interactive web UI (recommended for local development)
adk web basic_agent

# Terminal chat, single-shot or interactive
adk run basic_agent
adk run basic_agent "What's the exchange rate for JPY?"

# Serve the agent over a local FastAPI server
adk api_server basic_agent
```

`adk web` prints a local URL (default `http://localhost:8000`) — open it in a browser to chat with the agent.

## MongoDB Atlas MCP setup

The root agent registers the [`mongodb-mcp-server`](https://github.com/mongodb-js/mongodb-mcp-server) as an `McpToolset` (see [basic_agent/agent.py:20-39](basic_agent/agent.py#L20-L39)). It's launched on demand via `npx`, so no separate install step is needed beyond having Node 20+ available — just make sure the `--readOnly` flag stays in `args` unless you intentionally want the agent to be able to write to your cluster.

There are two independent credential modes, and you can supply either or both depending on what you want the agent to do:

1. **Direct database access** — for running queries, aggregations, etc. against a specific cluster:
   - In Atlas, go to your cluster → **Connect** → grab a connection string (choose the driver/shell option and fill in your username and password).
   - Set it as `MDB_MCP_CONNECTION_STRING` in `basic_agent/.env`.

2. **Atlas administration (management API)** — for tools that create/inspect clusters, projects, users, etc. at the Atlas control-plane level:
   - In the Atlas UI, go to **Organization Access Manager → API Keys** (or your Project's Access Manager) and create a new API key with the permissions you need.
   - Set the generated public/private key pair as `MDB_MCP_API_CLIENT_ID` / `MDB_MCP_API_CLIENT_SECRET`.
   - If using API key auth, make sure your current IP is added to the Atlas API's **Access List**, or Atlas will reject the requests.

You don't need both modes — omit whichever pair of variables you don't use, and the MCP server will only expose the tools it has credentials for.

### Interacting with the MongoDB Atlas MCP through the agent

Once your `.env` is configured, start the agent (`adk web basic_agent` or `adk run basic_agent`) and just ask it what you want in plain English — the model chooses the right MCP tool(s) and, if needed, connects to the cluster on your behalf. You don't need to name tools explicitly.

**Database queries** (require `MDB_MCP_CONNECTION_STRING`):

- "Connect to my Atlas cluster and list the databases."
- "List the collections in the `sample_mflix` database."
- "How many documents are in the `movies` collection?"
- "Show me the schema of the `users` collection in the `app` database."
- "Find the 5 most recent orders in `orders` where `status` is `pending`."
- "Run an aggregation on `sales` to get total revenue per month."
- "What indexes exist on the `movies` collection, and are any queries missing one?"

**Atlas project/cluster management** (require `MDB_MCP_API_CLIENT_ID` / `MDB_MCP_API_CLIENT_SECRET`):

- "List the projects in my Atlas organization."
- "List the clusters in project X and tell me their state."
- "Inspect the cluster named `Cluster26645` and tell me its tier and region."
- "List the database users on this project."
- "Any performance advisor recommendations for this cluster?"
- "Are there any open alerts on this project?"

By default the toolset is started with `--readOnly` (see [basic_agent/agent.py:24](basic_agent/agent.py#L24)), so write/administrative operations — `insert-many`, `update-many`, `delete-many`, `drop-collection`, `drop-database`, `atlas-create-cluster`, `atlas-create-db-user`, etc. — are disabled and the agent will report them as unavailable if asked. To allow writes, remove `--readOnly` from `args` in `agent.py`, understanding that the agent can then modify or delete real data in your cluster/project.
