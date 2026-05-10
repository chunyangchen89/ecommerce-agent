import logging

from langgraph.graph import END, StateGraph

from app.agent.state import AgentState, IntentType
from app.agent.intent_router import intent_router_node
from app.agent.nl2sql import nl2sql_node
from app.agent.rag import rag_node
from app.agent.synthesize import synthesize_node

logger = logging.getLogger(__name__)


def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", IntentType.HYBRID)
    if intent == IntentType.NL2SQL:
        return "nl2sql"
    elif intent == IntentType.RAG:
        return "rag"
    else:
        return "nl2sql"  # hybrid: NL2SQL first, then RAG


def route_after_nl2sql(state: AgentState) -> str:
    intent = state.get("intent", IntentType.HYBRID)
    if intent == IntentType.HYBRID:
        return "rag"
    return "synthesize"


def build_agent_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("intent_router", intent_router_node)
    graph.add_node("nl2sql", nl2sql_node)
    graph.add_node("rag", rag_node)
    graph.add_node("synthesize", synthesize_node)

    # Set entry
    graph.set_entry_point("intent_router")

    # Intent router → nl2sql or rag
    graph.add_conditional_edges(
        "intent_router",
        route_by_intent,
        {"nl2sql": "nl2sql", "rag": "rag"},
    )

    # NL2SQL → rag (hybrid) or synthesize (nl2sql only)
    graph.add_conditional_edges(
        "nl2sql",
        route_after_nl2sql,
        {"rag": "rag", "synthesize": "synthesize"},
    )

    # RAG → synthesize
    graph.add_edge("rag", "synthesize")

    # Synthesize → END
    graph.add_edge("synthesize", END)

    return graph.compile()
