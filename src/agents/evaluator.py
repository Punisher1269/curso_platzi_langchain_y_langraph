from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import Literal


class State(TypedDict):
    joke : str
    topic : str
    feedback : str
    is_funny : str
    

class FeedBack(BaseModel):
    is_funny : bool = Field(
        description="Decide if the joke is funny or not. Return True if it is, False otherwise."
    )
    feedback : str = Field(
        description="If the joke is not funny, provide feedback on how to improve it."
    )
SYSTEM_PROMPT = "Un chiste gracioso debe ser mas de 3 parrafo"
    
llm = init_chat_model("openai:gpt-4.1-mini", temperature=1)
llm_evaluator = llm.with_structured_output(schema=FeedBack, temperature=0)


def generator_node(state: State):
    feedback = state.get('feedback', None)
    topic = state.get('topic', None)
    if feedback:
        msg = llm.invoke(f"Write a joke about {topic} but take into account the feedback: {feedback} respond in spanish.")
    else:
        msg = llm.invoke(f"Write a joke about {topic} respond in spanish.")
    return {"joke" : msg.text}


def evaluator_node(state: State):
    joke = state.get("joke", None)
    schema = llm_evaluator.invoke(f"Grade the joke {joke} with the following prompt {SYSTEM_PROMPT}")
    return {"is_funny" : schema.is_funny, "feedback" : schema.feedback}


def router_edge(state : State) -> Literal[END,"generator_node"]: # type: ignore
    is_funny = state.get("is_funny", None)
    if is_funny:
        return END
    return "generator_node"


builder = StateGraph(State)

builder.add_node('generator_node', generator_node)
builder.add_node('evaluator_node', evaluator_node)

builder.add_edge(START, 'generator_node')
builder.add_edge('generator_node', 'evaluator_node')
builder.add_conditional_edges('evaluator_node', router_edge)
agent = builder.compile()