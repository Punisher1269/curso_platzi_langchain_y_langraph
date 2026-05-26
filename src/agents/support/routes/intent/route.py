from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from agents.support.state import State
from agents.support.routes.intent.prompt import SYSTEM_PROMT
from typing import Literal


class RouteIntent(BaseModel):
    step : Literal["conversation", "booking_node"] = Field("conversation", description="The next step in the routing procces")
    

llm = init_chat_model("google_genai:gemini-3-flash-preview", temperature=0)
llm_structured_output = llm.with_structured_output(schema=RouteIntent)

def intent_route(state : State) -> Literal["conversation", "booking_node"]:
    history = state["messages"]
    schema : RouteIntent = llm_structured_output.invoke([("system", SYSTEM_PROMT)] + history)

    if schema.step is None:
        return "conversation"

    print(f"Step elejido por la IA: {schema.step}")
    return schema.step

