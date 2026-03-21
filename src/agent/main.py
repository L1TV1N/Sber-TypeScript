from functools import cache

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent import chain
from agent.state import AgentState


def agent_node(state: AgentState) -> AgentState:
    result = chain.invoke(
        {
            "file_name": state.get("file_name", ""),
            "file_extension": state.get("file_extension", ""),
            "target_json_example": state.get("target_json_example", ""),
            "extracted_preview": state.get("extracted_preview", ""),
        }
    )

    return {
        "answer": result,
        "meta": {"status": "ok"},
    }


workflow = StateGraph(AgentState)
workflow.add_node(agent_node.__name__, agent_node)
workflow.set_entry_point(agent_node.__name__)
workflow.set_finish_point(agent_node.__name__)


@cache
def get_graph_agent() -> CompiledStateGraph:
    return workflow.compile()