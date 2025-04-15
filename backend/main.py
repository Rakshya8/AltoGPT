import glob
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from utils.data_loader import load_iaq
from agents.orchestrator import build_graph
from pprint import pprint

app = FastAPI()
recent_history = []
chat_history = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

compiled_graph = build_graph()  # Compile once

class QueryRequest(BaseModel):
    question: str

@app.get("/summary")
async def summary():
    df = load_iaq("Room101")
    latest = df.iloc[-1].to_dict()
    return {"summary": f"Room 101 latest CO2: {latest['co2']} ppm"}

@app.post("/query")
async def query(data: QueryRequest):

    global chat_history
    global recent_history

    print("Query Received:", data.question)

    # compiled_graph = build_graph()
    # final_state = {}
    initial_state = {
        "question": data.question,
        "chat_history": recent_history
    }

    # for event in compiled_graph.stream(initial_state, stream_mode="values"):
    #     # final_state = event.value  # latest state from stream
    #     print("\nIntermediate State:")
    #     pprint(event)

    event = compiled_graph.invoke(initial_state)

    chat_history = event.get("chat_history", chat_history)
    recent_history = chat_history[-3:]  # Keep only the last 3 exchanges
    
    # print("\nFinal Graph Result:")
    # pprint(event)
    return {"response": event.get("response", "No response generated."), "history": chat_history}

@app.post("/reset")
async def reset_chat():
    global chat_history, recent_history
    chat_history.clear()
    recent_history.clear()
    print("Chat history reset.")
    return {"status": "Chat history cleared."}


