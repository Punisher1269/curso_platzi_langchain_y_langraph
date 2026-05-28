from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import TypedDict, Optional
from langchain.chat_models import init_chat_model


llm = init_chat_model("openai:gpt-4.1-mini")


class SecurityReview(BaseModel):
    vulnerabilities: Optional[list[str]] = Field(
        description="The vulnerabilities in the code"
    )
    riskLevel: Optional[str] = Field(
        description="The risk level of the vulnerabilities"
    )
    suggestions: Optional[list[str]] = Field(
        description="The suggestions for fixing the vulnerabilities"
    )


class MaintainabilityReview(BaseModel):
    concerns: Optional[list[str]] = Field(description="The concerns about the code")
    qualityScore: Optional[int] = Field(
        description="The quality score of the code from 1 to 10", ge=1, le=10
    )
    recommendations: Optional[list[str]] = Field(
        description="The recommendations for improving the code"
    )


class State(TypedDict):
    code: str
    security_review: SecurityReview
    mantenibility_review: MaintainabilityReview
    final_review: str


# nodos


def security_review(state: State):
    code = state["code"]
    messages = [
        (
            "system",
            "You are an extert in code security, Focus on identitying security vulnerabilities, injection risks and authentication issues.",
        ),
        ("user", f"Review this code {code}"),
    ]
    llm_with_structured_output = llm.with_structured_output(schema=SecurityReview)
    schema = llm_with_structured_output.invoke(messages)
    return {"security_review": schema}


def mantenibility_review(state: State):
    code = state["code"]
    messages = [
        (
            "system",
            "You are an extert in code security, Focus on identitying security vulnerabilities, injection risks and authentication issues.",
        ),
        ("user", f"Review this code {code}"),
    ]
    llm_with_structured_output = llm.with_structured_output(schema=MaintainabilityReview)
    schema = llm_with_structured_output.invoke(messages)
    return {"mantenibility_review": schema}


def agregator(state: State):
    security_review = state["security_review"]
    mantenibility_review = state["mantenibility_review"]
    messages = [
        ("system","You are a tecnical lead summarizing multiple code reviews."),
        ("user", f"Synthesize these code review result into a concise sumary with keys actions: Security Reviews : {security_review} and Mantenibility Review {mantenibility_review}")
        ]
    response = llm.invoke(messages)
    # text_content = ""
    # for block in response.content:
    #     if isinstance(block, dict) and "text" in block:
    #         text_content += block["text"]
    #     elif isinstance(block, str):
    #         text_content += block
    # # Reemplazamos el contenido complejo con el texto plano
    # response.content = text_content
    return {"final_review" : response.text}
    




# Creacion de Grafo del agente
builder = StateGraph(State)
builder.add_node("security_review", security_review)
builder.add_node("mantenibility_review", mantenibility_review)
builder.add_node("agregator", agregator)


builder.add_edge(START, "security_review")
builder.add_edge(START, "mantenibility_review")
builder.add_edge("security_review", "agregator")
builder.add_edge("mantenibility_review", "agregator")
builder.add_edge("agregator", END)

agent = builder.compile()
