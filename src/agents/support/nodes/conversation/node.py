from agents.support.state import State
from langchain.chat_models import init_chat_model
from agents.support.nodes.conversation.tools import tools
from agents.support.nodes.conversation.promt import SYSTEM_PROMT

ai_model = init_chat_model("openai:gpt-4o", temperature=1)
ai_model = ai_model.bind_tools(tools)



def conversation(state: State):
    new_state : State = {} 
    # contexto = _construir_contexto(state)
    history = state["messages"]
    
    # al historia de mensajes le agregamos el contexto actual
    # history_mensages = [SystemMessage(content=contexto), *history]
    last_message = history[-1]
    # customer_name = state.get("customer_name", "Jhon Doe")
    ai_message = ai_model.invoke([("system", SYSTEM_PROMT), ("user", last_message.text)])
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