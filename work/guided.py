from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_groq.chat_models import ChatGroq
# from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

checkpointer = InMemorySaver()
model = init_chat_model("google_genai:gemini-2.0-flash",
                        temperature=0)

# model = init_chat_model(
#     "google_vertexai:gemini-2.5-flash", temperature=0
# )
# model = ChatGroq(model="openai/gpt-oss-120b")

class GuidedState(TypedDict):
    user_input: str
    response: str


def stream_graph_updates(state: GuidedState) -> GuidedState:
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit","exit",'e','q']:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except:
        # fallback if input() is not available            
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break

def guided(state: GuidedState) -> GuidedState:

    user_input = state['user_input']

    # form a prompt
    prompt = f"""
    You are a patient AI tutor guiding a user interactively. 
    Explain the following as a step-by-step guide, then ask a follow-up question.
    - Don't use (*) asterisk, you use it quite often never use it.

   Topic/Question: {user_input}
    Format your reply as:
    1. Explanation
    2. Step-by-step breakdown
    3. Follow-up question"""

    response = model.invoke(prompt).content
    state['response'] = response
    return state

# Create a graph
graph = StateGraph(GuidedState)

# add nodes
graph.add_node("guided", guided)
graph.add_node()
# add edges
graph.add_edge(START,"guided")
graph.add_edge("guided",END)

# compile
workflow = graph.compile(checkpointer=checkpointer)

# execute

initial_state = {
    'user_input': "why is galaxy in space not in water?"
}


final_state = workflow.invoke(initial_state)
print(final_state['response'])