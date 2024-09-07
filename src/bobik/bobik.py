import uuid

from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import tools_condition

from bobik.prompt import get_prompt
from bobik.tools import tool_node, tools
from bobik.util import print_events


def get_model():
    # llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.0)
    llm_with_tools = llm.bind_tools(tools)
    return llm_with_tools


def get_graph_builder():
    # # Define a new graph
    graph_builder = StateGraph(MessagesState)

    llm_with_tools = get_model()

    def chatbot(state: MessagesState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)

    graph_builder.set_entry_point("chatbot")
    graph_builder.add_conditional_edges("chatbot", tools_condition)

    return graph_builder


def main(db_url="postgres://localhost/mpasternak"):
    with PostgresSaver.from_conn_string(db_url) as checkpointer:
        checkpointer.setup()

        graph = get_graph_builder().compile(checkpointer=checkpointer)

        chat_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": chat_id}}

        # Pierwszy, powitalny komunikat
        events = graph.stream(
            {"messages": [("user", get_prompt())]}, config, stream_mode="values"
        )
        print_events(events)

        while True:
            user_input = input("Query:")
            events = graph.stream(
                {"messages": [("user", user_input)]}, config, stream_mode="values"
            )
            print_events(events)


if __name__ == "__main__":
    main()
