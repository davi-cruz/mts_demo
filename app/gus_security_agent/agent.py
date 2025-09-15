from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig
from google.genai import types
from google.adk.tools import google_search  # Import the tool


root_agent = Agent(
   name="gus_security_agent",
   # The Large Language Model (LLM) that agent will use.
   model="gemini-2.0-flash-exp", # if this model does not work, try below
   #model="gemini-2.0-flash-live-001",
   # A short description of the agent's purpose.
   description="Agent to answer questions using Google Search.",
   # Instructions to set the agent's behavior.
   instruction="Answer the question using the Google Search tool.",
   # Add google_search tool to perform grounding with Google search.
   tools=[google_search],
)