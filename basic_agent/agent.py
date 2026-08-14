from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from .custom_functions import get_fx_rate

root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[FunctionTool(get_fx_rate)]
)
