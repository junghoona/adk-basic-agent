# adk-basic-agent

> **⚠️ Work in progress.** This is an active coursework project built up lab by
> lab. The agent runs, but interfaces, tooling, and structure are still
> changing between commits, and several rough edges are known and unfixed —
> see [Known issues](#known-issues). Don't treat this as a stable reference.

A [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
agent that answers questions and reaches for external tools when it needs live
data from MongoDB Atlas MCP. It currently has three capabilities:

| Capability | Implemented as | Source |
|---|---|---|
| USD exchange rate lookup | `FunctionTool` over [CurrencyFreaks](https://currencyfreaks.com/) | [`custom_functions.py`](src/basic_agent/custom_functions.py) |
| Web search for real-time info | `AgentTool` wrapping a sub-agent with ADK's native `google_search` | [`custom_agents.py`](src/basic_agent/custom_agents.py) |
| MongoDB Atlas queries & administration | `McpToolset` over the official [MongoDB MCP Server](https://github.com/mongodb-js/mongodb-mcp-server) | [`agent.py`](src/basic_agent/agent.py) |

Both agents run on `gemini-3.6-flash`.

## Project structure

```
adk-basic-agent/
├── .python-version              3.12
├── requirements.txt             pinned freeze of the working environment
├── README.md
└── src/
    └── agent/                   the ADK agent package
        ├── __init__.py          `from . import agent` — how ADK discovers the agent
        ├── agent.py             root_agent: the three tools above
        ├── custom_agents.py     google_search_agent sub-agent
        ├── custom_functions.py  get_fx_rate()
        ├── .env                 secrets (gitignored, not committed)
        └── .gitignore           excludes .env and .adk/
```

`src/basic_agent/` is the agent folder — the thing you point `adk` at. ADK finds
`root_agent` because [`__init__.py`](src/basic_agent/__init__.py) imports the
`agent` module, and it loads `src/basic_agent/.env` automatically at startup.

## Prerequisites

- **Python 3.12** — pinned in [`.python-version`](.python-version).
- **Node.js 20+** with `npx`. The MongoDB MCP server is a Node process launched
  on demand via `npx -y mongodb-mcp-server`; there's nothing to install ahead of
  time, but `node` has to be new enough. Verified against Node v26.7.0.
- **A Gemini API key** — [Google AI Studio](https://aistudio.google.com/apikey).
- **A CurrencyFreaks API key** (free tier is fine) for the FX tool.
- **A MongoDB Atlas project** — see [MongoDB Atlas MCP setup](#mongodb-atlas-mcp-setup).

## Setup

**1. Create and activate a virtual environment.** This project was set up with
[uv](https://docs.astral.sh/uv/), but `venv` works too:

```bash
uv venv --python 3.12
source .venv/bin/activate
```

**2. Install dependencies:**

```bash
uv pip install -r requirements.txt      # or: pip install -r requirements.txt
```

[`requirements.txt`](requirements.txt) is a full pinned freeze (60 packages,
transitive deps included), so this reproduces the exact working environment.
The direct dependencies are `google-adk`, `google-genai`, `requests`, and
`python-dotenv`.

> **Note on `mcp`:** `google-adk` does **not** install the `mcp` package by
> default — it's an optional extra, and without it [`agent.py`](src/basic_agent/agent.py)
> fails at import with `ModuleNotFoundError: No module named 'mcp'`. The freeze
> pins `mcp==1.29.1` directly, so installing from `requirements.txt` covers it.
> If you ever install ADK by hand, use `pip install "google-adk[mcp]"`.

**3. Create `src/basic_agent/.env`** with the following keys. ADK loads this
file for you at startup; `.gitignore` already excludes it.

```dotenv
# Gemini access
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_GENAI_USE_ENTERPRISE=0     # set to 1 for Vertex AI / enterprise auth

# CurrencyFreaks — powers get_fx_rate
CF_API_KEY=your-currencyfreaks-api-key

# MongoDB Atlas MCP — see the section below
MDB_MCP_CONNECTION_STRING=your-atlas-connection-string
MDB_MCP_API_CLIENT_ID=your-atlas-api-client-id
MDB_MCP_API_CLIENT_SECRET=your-atlas-api-client-secret
```

## Running the agent

Run these from the repository root with the virtualenv active. Note the two
different argument shapes: `adk run` wants the **agent folder**, while
`adk web` and `adk api_server` want a **directory of agents** (though they also
accept a single agent folder directly).

```bash
# Terminal chat — interactive, or single-shot with a query argument
adk run src/agent
adk run src/agent "What's the exchange rate for JPY?"

# Web UI — recommended for local development
adk web src

# Plain FastAPI server, no UI
adk api_server src
```

`adk web` prints a local URL (default `http://localhost:8000`). Its endpoints
are unauthenticated and meant for local development only — don't expose it to
an untrusted network.

Session history is written to `src/basic_agent/.adk/session.db` (gitignored).

### Things to try

```
What's the exchange rate for JPY?
Who won the most recent Formula 1 race?
Connect to my Atlas cluster and list the databases.
```

The model picks the tool — you never name one explicitly.

## MongoDB Atlas MCP setup

[`agent.py`](src/basic_agent/agent.py) registers `mongodb-mcp-server` as an
`McpToolset`, launched over stdio via `npx`. There are two independent
credential modes; supply either or both, and the MCP server exposes only the
tools it has credentials for.

**1. Direct database access** — queries, aggregations, schema inspection:

- In Atlas: your cluster → **Connect** → copy a connection string (pick the
  driver option, then fill in your username and password).
- Set it as `MDB_MCP_CONNECTION_STRING`.

**2. Atlas administration (management API)** — inspecting projects, clusters,
users at the control-plane level:

- In Atlas: **Organization Access Manager → API Keys** (or your project's
  Access Manager) → create a key with the permissions you need.
- Set the public/private pair as `MDB_MCP_API_CLIENT_ID` / `MDB_MCP_API_CLIENT_SECRET`.
- Add your current IP to the Atlas API **Access List**, or requests are rejected.

### Example prompts

Database queries (need `MDB_MCP_CONNECTION_STRING`):

- "List the collections in the `sample_mflix` database."
- "How many documents are in the `movies` collection?"
- "Show me the schema of the `users` collection."
- "Find the 5 most recent orders in `orders` where `status` is `pending`."
- "What indexes exist on `movies`, and are any queries missing one?"

Atlas management (need the API key pair):

- "List the projects in my Atlas organization."
- "List the clusters in project X and tell me their state."
- "Any performance advisor recommendations for this cluster?"
