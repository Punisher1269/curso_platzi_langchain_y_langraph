# pip install -qU langchain "langchain[google-genai]"
from agents.support.nodes.booking.tools import tools
from agents.support.nodes.booking.prompt import prompt_template
from langchain.agents import create_agent


booking_node = create_agent(
    model="google_genai:gemini-3-flash-preview",
    tools=tools , 
    system_prompt=prompt_template.format(),
)