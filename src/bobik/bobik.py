import uuid
from typing import Union

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import tools_condition

from bobik.tools import tool_node, tools


def get_model(model, model_api_key, temperature=0.0):
    if model.startswith("gpt-"):
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=model, api_key=model_api_key, temperature=temperature)
    elif model.startswith("claude-"):
        from langchain_anthropic import ChatAnthropic

        llm = ChatAnthropic(model=model, api_key=model_api_key, temperature=temperature)
    else:
        raise NotImplementedError(f"Model {model} is supported by bobik")

    llm_with_tools = llm.bind_tools(tools)
    return llm_with_tools


def get_graph_builder(model, model_api_key, temperature=0.0) -> StateGraph:
    graph_builder = StateGraph(MessagesState)

    llm_with_tools = get_model(model, model_api_key, temperature)

    def chatbot(state: MessagesState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)

    graph_builder.set_entry_point("chatbot")
    graph_builder.add_conditional_edges("chatbot", tools_condition)

    return graph_builder


class Bobik:
    def __init__(
        self,
        system_prompt,
        thread_id=None,
        db_url="memory://",
        model="claude-3-5-sonnet-20240620",
        model_api_key=None,
        temperature=0.0,
    ):
        self.model = model
        self.model_api_key = model_api_key
        self.temperature = temperature

        self.db_url = db_url
        if not self.db_url:
            raise ValueError("Please pass db_url")

        self.thread_id = thread_id

        self.send_initial_prompt = False
        if not self.thread_id:
            # There is no chat_id, so generate one and set the flag to send the
            # initial prompt:
            self.thread_id = str(uuid.uuid4())
            self.send_initial_prompt = True

        self.graph = self.checkpointer = None

        self.system_prompt = system_prompt

    def get_checkpointer(self) -> Union[PostgresSaver, MemorySaver]:
        if self.db_url.startswith("memory"):
            return MemorySaver()

        elif self.db_url.lower().startswith("postgres"):
            from psycopg import Connection
            from psycopg.rows import dict_row

            self._db_conn = Connection.connect(
                self.db_url, autocommit=True, prepare_threshold=0, row_factory=dict_row
            )
            return PostgresSaver(self._db_conn)

        else:
            raise ValueError("PostgreSQL or memory backends supported")

    @property
    def config(self):
        return {"configurable": {"thread_id": self.thread_id}}

    def _setup(self):
        if self.checkpointer is None:
            self.checkpointer = self.get_checkpointer()

        if hasattr(self.checkpointer, "setup"):
            self.checkpointer.setup()

        if self.graph is None:
            self.graph: CompiledStateGraph = get_graph_builder(
                self.model, self.model_api_key, self.temperature
            ).compile(checkpointer=self.checkpointer)

    def say_hello(self):
        self._setup()
        return self.graph.stream(
            {"messages": [("user", self.system_prompt)]},
            self.config,
            stream_mode="values",
        )

    def get_messages(self):
        self._setup()
        return self.checkpointer.list(config=self.config)

    def send_message(self, msg: Union[str, None] = None):

        self._setup()

        if self.send_initial_prompt:
            self.send_initial_prompt = False
            self.say_hello()

        if not msg:
            return

        return self.graph.stream(
            {"messages": [("user", msg)]}, self.config, stream_mode="values"
        )
