from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState
from app.agent.nodes import author_node, orchestrator_node, researcher_node


agentflow = StateGraph(AgentState)
agentflow.add_node("orchestrator", orchestrator_node)
agentflow.add_node("researcher", researcher_node)
agentflow.add_node("author", author_node)
agentflow.add_edge(START, "orchestrator")
agentflow.add_conditional_edges(
	"orchestrator",
	lambda state: state["route"],
	{"researcher": "researcher", "author": "author", "end": END},
)
agentflow.add_edge("researcher", END)
agentflow.add_edge("author", END)

app = agentflow.compile()
