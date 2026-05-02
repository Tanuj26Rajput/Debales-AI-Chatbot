from langgraph.graph import StateGraph, END
from typing import TypedDict
from rag.retriever import get_retriever
from bot_tools.serp_tool import search_tool
from bot_utils.router import route_query
from bot_utils.llm import model

retriever = get_retriever()

# state
class AgentState(TypedDict):
    query: str
    context: str
    result: str
    route: str

def router_node(state: AgentState):
    # decide whether this question needs RAG, Google, or both.
    route = route_query(state["query"])
    print(f"[router] route selected: {route}")
    return {"route": route}

def rag_node(state: AgentState) -> AgentState:
    print("[rag] searching Debales knowledge base...")
    # gives us relevant chunks 
    docs = retriever.vectorstore.max_marginal_relevance_search(
        state["query"],
        k=5,
        fetch_k=10
    )
    context_parts = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content.strip()
    
        context_parts.append(
            f"[Doc {i+1} | Source: {source}]\n{content}"
        )

    context = "\n\n".join(context_parts)
    state["context"] = context
    print(f"[rag] retrieved {len(docs)} document chunks")
    return state

def serp_node(state: AgentState) -> AgentState:
    print("[serp] rewriting query for Google search...")
    # rewrite usually gives cleaner search 
    prompt = f"""
Rewrite the following query into a clear, specific, and search-engine-friendly question.

Rules:
- Make it precise
- Keep it concise
- Do NOT change intent

Query: {state["query"]}

Rewritten Query:
"""
    rewrite_query = model.invoke(prompt)
    print(f"[serp] searching Google for: {rewrite_query.content.strip()}")
    result = search_tool(rewrite_query.content)
    state["context"] = result
    print("[serp] search complete")
    return state

def both_node(state: AgentState) -> AgentState:
    print("[both] searching Debales knowledge base and Google...")
    print("[both:rag] searching Debales knowledge base...")
    # Mixed questions get Debales context first, then outside context from search.
    docs = retriever.vectorstore.max_marginal_relevance_search(
        state["query"],
        k=5,
        fetch_k=10
    )
    context_parts = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content.strip()

        context_parts.append(
            f"[Doc {i+1} | Source: {source}]\n{content}"
        )

    rag_context = "\n\n".join(context_parts)
    print(f"[both:rag] retrieved {len(docs)} document chunks")

    # SERP
    print("[both:serp] rewriting query for Google search...")
    prompt = f"""
Rewrite the following query into a clear, specific, and search-engine-friendly question.

Rules:
- Make it precise
- Keep it concise
- Do NOT change intent

Query: {state["query"]}

Rewritten Query:
"""
    rewrite_query = model.invoke(prompt)
    print(f"[both:serp] searching Google for: {rewrite_query.content.strip()}")
    serp_context = search_tool(rewrite_query.content)
    print("[both:serp] search complete")

    combined = f"""
    RAG Context:
    {rag_context}

    SERP Context:
    {serp_context}
    """

    state["context"] = combined
    print("[both] combined RAG and SERP context")
    return state

def final_node(state):
    query = state["query"]
    context = state.get("context", "")
    print("[final] generating final answer from retrieved context...")

    # The final prompt 
    prompt = f"""
You are an AI assistant.

Follow these rules:
- Use ONLY the provided context
- Combine information if multiple sources exist
- If answer is not present, say "I don't know"
- Keep answer clear and structured

Question: {query}

Context:
{context}

Answer:
"""

    answer = model.invoke(prompt)

    print("[final] answer generated")
    return {"result": answer.content}

def build_graph():
    graph = StateGraph(AgentState)

    # nodes
    graph.add_node("router", router_node)
    graph.add_node("rag", rag_node)
    graph.add_node("serp", serp_node)
    graph.add_node("both", both_node)
    graph.add_node("final", final_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
    "router",
    lambda state: state["route"],
    {
        "rag": "rag",
        "serp": "serp",
        "both": "both",   
    }
)

    graph.add_edge("rag", "final")
    graph.add_edge("serp", "final")
    graph.add_edge("both", "final")
    graph.add_edge("final", END)

    return graph.compile()
