from agents.support.state import State
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field, EmailStr
from agents.support.nodes.extractor.promt import SYSTEM_PROMT
    

class BasicUserData(BaseModel):
    "Basic data of a person"
    name : str = Field(description="The name of the person")
    email : str = Field(description="The email adress of the person", default=None)
    phone : str = Field(description="The phone of the person")
    age : str = Field(description="The age of the person")


llm_with_structures_data = init_chat_model("google_genai:gemini-3-flash-preview", temperature=0)
llm_with_structured_output = llm_with_structures_data.with_structured_output(schema=BasicUserData)



def extractor(state : State):
    customer_name = state.get("customer_name")
    history = state["messages"]
    new_state = {}
    if customer_name is None or len(history) >= 5:
        schema = llm_with_structured_output.invoke([("system", SYSTEM_PROMT)] + history)
        new_state["customer_name"] = schema.name
        new_state["phone"] = schema.phone
        new_state["age"] = schema.age
    return new_state