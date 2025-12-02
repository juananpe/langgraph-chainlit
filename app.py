from dotenv import load_dotenv
load_dotenv()

from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch

import chainlit as cl

# Define the Tavily search tool
tavily_search = TavilySearch(max_results=3)
tools = [tavily_search]

# Set up the model (only one needed!)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

# Bind tools to the model
model = model.bind_tools(tools)

# Create the tool node
tool_node = ToolNode(tools=tools)

from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState


def should_continue(state: MessagesState) -> Literal["tools", END]:
    """Determine whether to continue with tools or end."""
    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, we end (reply to the user)
    return END


async def call_model(state: MessagesState):
    """Call the model that can use tools and provide final answers."""
    messages = state["messages"]
    response = await model.ainvoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Build the graph (simplified - no final node needed)
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)

# Add edges
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
)
builder.add_edge("tools", "agent")

# Compile the graph
graph = builder.compile()


@cl.on_message
async def on_message(msg: cl.Message):
    """Handle incoming messages from the user."""
    config = {"configurable": {"thread_id": cl.context.session.id}}
    
    final_answer = cl.Message(content="")
    
    try:
        # Stream the response
        async for event in graph.astream(
            {"messages": [HumanMessage(content=msg.content)]}, 
            config=RunnableConfig(**config)
        ):
            # Check if this is the final agent response
            if "agent" in event and "messages" in event["agent"]:
                message = event["agent"]["messages"][-1]
                if hasattr(message, 'content') and message.content:
                    await final_answer.stream_token(message.content)
    except Exception as e:
        # Handle any streaming errors gracefully
        await final_answer.stream_token(f"I encountered an error: {str(e)}")
    
    await final_answer.send()
