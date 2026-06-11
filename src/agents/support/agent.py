from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from agents.support.state import State
from agents.support.nodes.conversation.node import conversation 
from agents.support.nodes.extractor.node import extractor 
from agents.support.nodes.booking.node import booking_node
from agents.support.routes.intent.route import intent_route



def make_graph(config : TypedDict): # type: ignore
    checkpointer = config.get("checkpointer", None)
    builder = StateGraph(State)
    # Creacion de nodo
    builder.add_node("conversation", conversation)
    builder.add_node("extractor", extractor)
    builder.add_node("booking_node", booking_node)

    # Conexiones
    builder.add_edge(START, "extractor") 
    builder.add_conditional_edges("extractor", intent_route) 
    builder.add_edge("conversation", END)
    builder.add_edge("booking_node", END)

    return builder.compile(checkpointer=checkpointer)