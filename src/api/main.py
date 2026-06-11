from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from fastapi.responses import StreamingResponse
from .schemas import Message
from langchain_core.messages import HumanMessage
from api.db import lifespan, CheckpointerDep
from src.agents.support.agent import make_graph  # noqa: E402


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "API OK"}


@app.post("/chat/{chat_id}")
async def read_item(chat_id: str, item : Message, checkpointer : CheckpointerDep):
    config = {
        "configurable" : {
            "thread_id" : chat_id
        }
    }
    humen_message = HumanMessage(content=item.message)
    agent = make_graph(config={"checkpointer" : checkpointer})
    state = {"messages" : [humen_message]} 
    response =  agent.invoke(state, config)
    last_message = response["messages"][-1]
    # return last_message.text
    return response["messages"]



@app.post("/chat/{chat_id}/stream")
async def stream_chat(chat_id: str, message: Message, checkpointer : CheckpointerDep):
    human_message = HumanMessage(content=message.message)
    async def generate_response():
        agent = make_graph(config={"checkpointer" : checkpointer})
        for message_chunk, metadata in agent.stream({"messages": [human_message]}, stream_mode="messages"):
            if message_chunk.content:
                yield f"data: {message_chunk.content}\n\n"

        print(message_chunk.content, end="|", flush=True)

    return StreamingResponse(generate_response(), media_type="text/event-stream")