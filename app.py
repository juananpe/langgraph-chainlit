from dotenv import load_dotenv
load_dotenv()

from typing import Literal, Optional
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

import chainlit as cl
from chainlit.types import ThreadDict

# Diccionario de usuarios (en producción, usa una base de datos)
USERS = {
    "admin": {
        "password": "admin123",
        "name": "Administrador",
        "role": "admin"
    },
    "guapo": {
        "password": "guapo123",
        "name": "Mikel Garcia",
        "role": "user"
    },
    "feo": {
        "password": "feo123",
        "name": "Mikel Lonbide",
        "role": "user"
    }
}


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """
    Callback de autenticación para Chainlit.
    Verifica las credenciales del usuario.
    """
    # Buscar el usuario en el diccionario
    user_data = USERS.get(username)
    
    if user_data and user_data["password"] == password:
        # Credenciales correctas - crear objeto User
        return cl.User(
            identifier=username,
            metadata={
                "name": user_data["name"],
                "role": user_data["role"]
            }
        )
    else:
        # Credenciales incorrectas
        return None

# Define the Tavily search tool
tavily_search = TavilySearchResults(max_results=3)
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

# Create SQLite checkpointer for persistent memory
import aiosqlite
import asyncio

# Initialize the checkpointer
checkpointer = None
graph = None

async def init_graph():
    """Initialize the graph with async checkpointer."""
    global graph, checkpointer
    
    # Create connection and checkpointer
    conn = await aiosqlite.connect("checkpoints.db")
    checkpointer = AsyncSqliteSaver(conn)
    await checkpointer.setup()
    
    # Compile the graph with checkpointer
    graph = builder.compile(checkpointer=checkpointer)
    return graph


@cl.on_chat_start
async def on_chat_start():
    """Initialize the graph with async checkpointer when chat starts."""
    global graph
    
    # Initialize graph if not already done
    if graph is None:
        await init_graph()
    
    # Obtener el usuario autenticado
    user = cl.user_session.get("user")
    
    if user:
        # Usuario autenticado - usar su identifier único
        thread_id = f"user_{user.identifier}"
        user_name = user.metadata.get("name", user.identifier)
        
        # Mensaje de bienvenida personalizado
        await cl.Message(
            content=f"¡Hola {user_name}! 👋\n\n"
            f"Soy tu asistente personal con memoria persistente. "
            f"Recordaré todas nuestras conversaciones, incluso si cierras y vuelves a abrir el navegador.\n\n"
            f"Tu historial de conversaciones está guardado de forma segura y es privado."
        ).send()
    else:
        # Usuario no autenticado (no debería ocurrir con auth habilitado)
        thread_id = "anonymous"
        await cl.Message(
            content="¡Hola! Soy tu asistente con memoria persistente."
        ).send()
    
    cl.user_session.set("thread_id", thread_id)


@cl.on_message
async def on_message(msg: cl.Message):
    """Handle incoming messages from the user."""
    global graph
    
    # Make sure graph is initialized
    if graph is None:
        await init_graph()
    
    # Get the persistent thread_id from user session
    thread_id = cl.user_session.get("thread_id")
    if not thread_id:
        # Fallback: use a default thread for all anonymous users
        thread_id = "default_user"
        cl.user_session.set("thread_id", thread_id)
    
    config = {"configurable": {"thread_id": thread_id}}
    
    final_answer = cl.Message(content="")
    
    try:
        # Stream the response with simplified callback handler
        async for event in graph.astream(
            {"messages": [HumanMessage(content=msg.content)]}, 
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()], **config)
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
