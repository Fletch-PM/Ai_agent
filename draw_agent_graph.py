from app.agent.graph import app as AgentFlow


if __name__ == "__main__":
    agent_flow = AgentFlow

    # Create a graph using the StateGraph class and draw it as a PNG.
    png_data = agent_flow.get_graph().draw_mermaid_png()

    with open("Agent_graph.png", "wb") as graph_file:
        graph_file.write(png_data)

    print("Saved Agent_graph.png")
