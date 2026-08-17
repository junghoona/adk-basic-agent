"""AI agent (Python wrapper function) to call native Google Search
"""


from google.adk.agents import Agent
from google.adk.tools import google_search

# Create an agent with google search tool as a search specialist

google_search_agent = Agent(
    model='gemini-3.1-flash-lite',
    name='google_search_agent',
    description='A search agent that uses google search to get latest information...',
    instruction='Use google search to answer user questions about real-time info.',
    tools=[google_search],
)
