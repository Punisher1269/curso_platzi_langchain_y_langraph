from langgraph.graph import MessagesState
from pydantic import BaseModel, Field, EmailStr
from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

# ai_model = init_chat_model("google_genai:gemini-3-flash-preview", temperature=1)
ai_model = init_chat_model("openai:gpt-4o", temperature=1)
file_search_tool = {
    "type" : "file_search",
    "vector_store_ids" : ["vs_69fb5f76f630819199504fcfd2ad76bd"] # id de la base de datos vectorial
}
ai_model = ai_model.bind_tools([file_search_tool])


class State(MessagesState):
    customer_name : str
    phone : int
    age : str

class BasicUserData(BaseModel):
    "Basic data of a person"
    name : str = Field(description="The name of the person")
    email : EmailStr = Field(description="The email adress of the person", default=None)
    phone : str = Field(description="The phone of the person")
    age : str = Field(description="The age of the person")


llm_with_structures_data = init_chat_model("google_genai:gemini-3-flash-preview", temperature=0)
llm_with_structured_output = llm_with_structures_data.with_structured_output(schema=BasicUserData)
state : State = {}


def _construir_contexto(state: State) -> str:
    """Construye el contexto del estado actual"""
    return f"""Información del cliente:
        - Nombre: {state.get('customer_name') or 'Desconocido'}
        - Edad: {state.get('age') or 'No proporcionada'}

        Usa esta información para personalizar tus respuestas."""


def extractor(state : State):
    customer_name = state.get("customer_name")
    new_state = {}
    if customer_name is None or len(state["messages"]) > 5:
        schema = llm_with_structured_output.invoke(state["messages"])
        new_state["customer_name"] = schema.name
        new_state["phone"] = schema.phone
        new_state["age"] = schema.age
    return new_state

def conversation(state: State):
    new_state : State = {} 
    # contexto = _construir_contexto(state)
    history = state["messages"]
    
    # al historia de mensajes le agregamos el contexto actual
    # history_mensages = [SystemMessage(content=contexto), *history]
    last_message = history[-1]
    customer_name = state.get("customer_name", "Jhon Doe")
    system_message = f"You are a helpful assistan that can answer questions about the custimer {customer_name}"
    ai_message = ai_model.invoke([("system", system_message), ("user", last_message.text)])
    text_content = ""
    for block in ai_message.content:
        if isinstance(block, dict) and "text" in block:
            text_content += block["text"]
        elif isinstance(block, str):
            text_content += block
    # Reemplazamos el contenido complejo con el texto plano
    ai_message.content = text_content
    # Al devolver el nuevo state, se actualiza la memoria del agente
    new_state["messages"] = [ai_message]
    return new_state





builder = StateGraph(State)

# Creacion de nodo
builder.add_node("conversation", conversation)
builder.add_node("extractor", extractor)

# Conexiones
builder.add_edge(START, "extractor")
builder.add_edge("extractor", "conversation")
builder.add_edge("conversation", END)

agent = builder.compile()