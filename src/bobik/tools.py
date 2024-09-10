from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode


@tool
def send_email(subject: str, body_text: str, recipients: str):
    """Call to send an e-mail with the log"""
    # print(f"send_email called, {subject=} {body_text=} {recipients=}")
    return "Wysłałem e-mail do administratora serwisu. "


tools = [send_email]

tool_node = ToolNode(tools)
