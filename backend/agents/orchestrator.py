import datetime
import os
from pyexpat import model
import torch

from pprint import pprint
from matplotlib.style import available
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
# from langchain_huggingface import HuggingFacePipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.tool_agent import ToolAgent

from agents.sensor_agent import SensorAgent
from agents.rag_agent import RAGAgent
from agents.answer_agent import AnswerAgent
# from agents.llm_triton import TritonPhi2Client

torch.set_default_device("cuda")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", None)

# TRITON_URL = os.environ.get("TRITON_URL", "http://localhost:8000")

# llm = TritonPhi2Client(triton_url=TRITON_URL)

print("Loading LLM...")

# llm = HuggingFacePipeline.from_model_id(
#     model_id="microsoft/Phi-3-mini-4k-instruct",
#     # model_id="microsoft/phi-2",
#     task="text-generation",
#     device=0,
#     batch_size=1,
#     pipeline_kwargs={
#         "max_new_tokens": 50,
#         # "top_k": 50,
#         # "temperature": 0.1,
#     },
# )

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    temperature=0,
    max_tokens=None,
    google_api_key=GEMINI_API_KEY
)

print("LLM loaded.")

available_room = ["Room101", "Room102", "Room103"]
available_operation = ["latest", "average", "sum", "time_specific"]

def run_keyword_agent(state: dict):
    print("\nRunning KeywordAgent")
    question = state.get("question", "")
    chat_history = state.get("chat_history", [])

    room, operation, datetime = None, None, None

    for turn in chat_history[::-1]:
        if "room" in turn:
            room = turn["room"]
            break

    for turn in chat_history[::-1]:
        if "operation" in turn:
            operation = turn["operation"]
            break

    for turn in chat_history[::-1]:
        if "datetime" in turn:
            datetime = turn["datetime"]
            break

    # Construct a rich system + user prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that analyzes room the user is asking about.
        The possible rooms are: {room_types}. If the room is not in the list, say "N/A".
        If room are known, just say "Roomxxx" where xxx is the room number."""),
        ("user", """Question: {question}""")
    ])

    formatted_prompt = prompt.format_messages(
        question=question,
        room_types=", ".join(available_room)
    )

    new_room = llm.invoke(formatted_prompt).content.capitalize()

    print("No previous operation found. Searching operation from user prompt.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that analyzes what type of operation the user is asking about.
        The possible operation types are: {operation_types}. If the room is not in the list, say "N/A".
        If operation type is known, just say "xxx" where xxx is the operation type."""),
        ("user", """Question: {question}""")
    ])

    formatted_prompt = prompt.format_messages(
        question=question,
        operation_types=", ".join(available_operation)
    )

    new_operation = llm.invoke(formatted_prompt).content.lower()

    updated_room = new_room if new_room in available_room else room
    updated_operation = new_operation if new_operation in available_operation else operation

    if updated_operation == "time_specific":
        print("Mode of operation is 'time_specific'. Extracting datetime from question.")

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that analyzes what date and time the user refers to.
            Extract the date and time from the question in the format: YYYY-MM-DD HH:MM:SS."""),
            ("user", """Question: {question}""")
        ])

        formatted_prompt = prompt.format_messages(
            question=question
        )

        datetime = llm.invoke(formatted_prompt).content

    updated_state = {
        **state,
        "room": updated_room,
        "operation": updated_operation,
        "datetime": datetime
    }

    print("\nKeywordAgent Output:")
    pprint(updated_state)
    return updated_state

def run_sensor_agent(state: dict):
    print("\nRunning SensorAgent")
    room = state.get("room", None)
    operation = state.get("operation", None)
    datetime = state.get("datetime", None)
    try:
        sensor = SensorAgent(room, operation, datetime)
        data = sensor.run()
    except FileNotFoundError as e:
        print("Data for input room cannot be found. Returning empty data.")
        data = {"status": "Failure"}
    
    updated_state = {
        **state,
        "sensor_data": data
    }
    print("\nSensorAgent Output:")
    pprint(updated_state)
    return updated_state

# def run_answer_agent(state: dict):
#     print("Running AnswerAgent")
#     if "sensor_data" not in state or "guidelines" not in state:
#         print("DEBUG STATE (AnswerAgent):", state)
#         raise ValueError("Missing sensor_data or guidelines in state!")

#     final = AnswerAgent().generate(state["sensor_data"], state["guidelines"])
#     updated_state = {
#         **state,
#         "response": final
#     }
#     print("Final Answer Output:", updated_state)
#     return updated_state

def run_tool_agent(state: dict):
    print("Running ToolAgent (IAQ + HVAC Advisor)")

    sensor = state.get("sensor_data", {})
    iaq = sensor.get("iaq", {})
    power = sensor.get("power", {}).get("avg_power_watts", 0)

    co2 = iaq.get("co2", 0)
    temperature = iaq.get("temperature", 0)
    humidity = iaq.get("humidity", 0)

    recommendations = []

    # Indoor Air Quality rules
    if co2 > 1000:
        recommendations.append(f"Increase ventilation to reduce CO₂ (currently {co2} ppm)")
    elif co2 < 400:
        recommendations.append(f"CO₂ levels are excellent ({co2} ppm)")

    # HVAC suggestions based on temperature
    if temperature > 27:
        recommendations.append(f"Consider cooling: Room is warm ({temperature}°C)")
    elif temperature < 18:
        recommendations.append(f"Consider heating: Room is cold ({temperature}°C)")
    else:
        recommendations.append(f"Temperature is in a comfortable range ({temperature}°C)")

    # Humidity alerts
    if humidity > 60:
        recommendations.append(f"High humidity detected ({humidity}%). Consider dehumidifier.")
    elif humidity < 30:
        recommendations.append(f"Low humidity ({humidity}%). Consider humidifier.")
    else:
        recommendations.append(f"Humidity is optimal ({humidity}%)")

    # Power draw estimation
    if power > 15000:
        recommendations.append(f"High energy usage detected ({power}W). Consider HVAC efficiency tuning.")

    return {
        **state,
        "alerts": recommendations
    }

def run_rag_agent(state: dict):
    print("\nRunning RAGAgent")
    if "sensor_data" not in state:
        print("DEBUG STATE (RAGAgent):", state)
        raise ValueError("sensor_data is missing from state!")

    rag = RAGAgent()
    iaq_topics = ["co2", "temperature", "humidity"]
    guidelines = {topic: rag.retrieve(topic) for topic in iaq_topics}

    updated_state = {
        **state,
        "guidelines": guidelines
    }
    print("\nRAGAgent Output:")
    pprint(updated_state)
    return updated_state

def run_chat_agent(state: dict):
    print("\nRunning ChatAgent")

    question = state.get("question", "")
    sensor = state.get("sensor_data", {})
    sensor_status = sensor.get("status", "Failure")
    guidelines = state.get("guidelines", {})
    room = state.get("room", None)
    operation = state.get("operation", None)
    datetime = state.get("datetime", None)
    alerts = state.get("alerts", [])
    chat_history = state.get("chat_history", [])
    history_text = "\n".join([f"User: {turn['question']}\nAssistant: {turn['answer']}" for turn in chat_history[-3:]])  # use last 3 exchanges

    # Handle unknowns before building prompt
    if room is None or operation is None:
        if room is None and operation is None:
            final_response = "Sorry, I couldn't identify which room or operation you're referring to. Please rephrase your question with more context."
        
        elif room is None:
            final_response = "I couldn't determine which room you're referring to. Please specify a valid room (e.g., Room101)."
        
        elif operation is None:
            final_response = "I couldn't determine what operation you want (latest, average, or sum). Could you clarify?"
        
        # Append to chat history
        chat_history.append({
            "question": question,
            "room": room,
            "operation": operation,
            "datetime": datetime,
            "answer": final_response
        })

        return {
            **state,
            "response": final_response,
            "chat_history": chat_history
        }
    
    if sensor_status == "Failure":
        datetime = None  # Reset datetime if sensor data is not available
    
    if operation == "time_specific" and datetime is None:
        final_response = "I couldn't determine the specific time you're referring to. Please specify a valid date and time."
        
        # Append to chat history
        chat_history.append({
            "question": question,
            "room": room,
            "operation": operation,
            "datetime": datetime,
            "answer": final_response
        })

        return {
            **state,
            "response": final_response,
            "chat_history": chat_history
        }

    # Construct a rich system + user prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a helpful assistant that analyzes room sensor data.
Use the chat history and new question to provide a consistent and context-aware response.
Be sure to answer only the relevant information based on the current question only.
In case some sensor data is not available (N/A or None), specify what data is not available in your response as well.
"""),
        ("user", """
Chat History:
{history}

#############################################################################
         
Current question: {question}

Sensor Data Based on Current Question:
- CO₂: {co2} ppm
- Temperature: {temp} °C
- Humidity: {humidity} %
- Power usage: {power} W
- Occupied: {occupied}

Guidelines Based on Current Question:
- CO₂: {g_co2}
- Temp: {g_temp}
- Humidity: {g_humidity}
""")
    ])

    formatted_prompt = prompt.format_messages(
        history=history_text,
        question=question,
        co2=sensor.get("iaq", {}).get("co2", "N/A"),
        temp=sensor.get("iaq", {}).get("temperature", "N/A"),
        humidity=sensor.get("iaq", {}).get("humidity", "N/A"),
        power=sensor.get("power", {}).get("avg_power_watts", "N/A"),
        occupied="Yes" if sensor.get("presence", {}).get("occupied", False) else "No",
        g_co2=guidelines.get("co2", "N/A"),
        g_temp=guidelines.get("temperature", "N/A"),
        g_humidity=guidelines.get("humidity", "N/A")
    )

    response = llm.invoke(formatted_prompt)
    final_response = response.content
    if alerts:
        final_response += "\n\nAlerts:\n" + "\n".join(alerts)

    # Append to chat history
    chat_history.append({
        "question": question,
        "room": room,
        "operation": operation,
        "datetime": datetime,
        "answer": final_response
    })

    updated_state = {
        **state,
        "response": final_response,
        "chat_history": chat_history
    }

    print("\nChatAgent Output:")
    pprint(updated_state)

    return updated_state

def route_after_sensor_agent(state: dict) -> str:
    if state.get("sensor_data", {}).get("status", "Failure") == "Failure":
        return "ChatAgent"  # skip RAGAgent
    return "ToolAgent"


def build_graph():
    builder = StateGraph(dict)

    builder.add_node("KeywordAgent", RunnableLambda(run_keyword_agent))
    builder.add_node("SensorAgent", RunnableLambda(run_sensor_agent))
    builder.add_node("ToolAgent", RunnableLambda(run_tool_agent))  # Inserted here
    builder.add_node("RAGAgent", RunnableLambda(run_rag_agent))
    builder.add_node("ChatAgent", RunnableLambda(run_chat_agent))

    builder.add_edge(START, "KeywordAgent")
    builder.add_edge("KeywordAgent", "SensorAgent")
    builder.add_conditional_edges("SensorAgent", route_after_sensor_agent)       # Conditional edge to ToolAgent or ChatAgent
    builder.add_edge("ToolAgent", "RAGAgent")          # before RAGAgent
    builder.add_edge("RAGAgent", "ChatAgent")
    builder.add_edge("ChatAgent", END)

    return builder.compile()