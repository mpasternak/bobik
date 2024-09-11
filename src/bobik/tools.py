from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode


@tool
def wygeneruj_liste_badan(
    wiek_pacjenta, plec_pacjenta, planowana_operacja, choroby, uczulenia
):
    """Generuje liste badan dla pacjenta o okreslonym wieku do okreslonej operacji"""
    return (
        f"Zwracam liste badan dla {wiek_pacjenta=}, {plec_pacjenta=}, {planowana_operacja=}, "
        f"{choroby=}, {uczulenia=} -- FUNKCJA NIEZAIMPLEMENTOWANA"
    )


@tool
def send_email(subject: str, body_text: str, recipients: str):
    """Call to send an e-mail with the log"""
    # print(f"send_email called, {subject=} {body_text=} {recipients=}")
    return f"Wysłałem e-mail do administratora {subject=} {recipients=} {body_text=} -- FUNKCJA NIEZAIMPLEMENTOWANA "


tools = [send_email, wygeneruj_liste_badan]

tool_node = ToolNode(tools)
