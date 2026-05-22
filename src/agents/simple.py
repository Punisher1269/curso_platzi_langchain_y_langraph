from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model

ai_model = init_chat_model("google_genai:gemini-3-flash-preview", temperature=1)

class State(MessagesState):
    customer_name : str
    age : int


state : State = {}
customer_name = state.get('customer_name', None)

def _construir_contexto(state: State) -> str:
    """Construye el contexto del estado actual"""
    return f"""Información del cliente:
        - Nombre: {state.get('customer_name') or 'Desconocido'}
        - Edad: {state.get('age') or 'No proporcionada'}

        Usa esta información para personalizar tus respuestas."""


def node_1(state: State):
    new_state : State = {}
    if state.get("customer_name") is None:
        new_state["customer_name"] = "David"
    else:
        new_state["age"] = 23
        
        
    contexto = _construir_contexto(state)
    history = state["messages"]
    
    # al historia de mensajes le agregamos el contexto actual
    history_mensages = [SystemMessage(content=contexto), *history]
        
    ai_message = ai_model.invoke(history_mensages)
    new_state["messages"] = [ai_message]
    return new_state



# def node_2(state: State):
#     if state.get("age") is None:
#         return {
#             "age" : 3
#         }
#     return {}



builder = StateGraph(State)

# Creacion de nodo
builder.add_node("node_1", node_1)

# Conexiones
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

agent = builder.compile()