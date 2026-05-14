from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node, llm_with_tools
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node
from app.tools.patient_tools import ask_patient, recommend_interim_care

# --Builder---------------------------------------------------------------
builder = StateGraph(MedicalState)

# --Enregistrement des nœuds----------------------------------------------
builder.add_node("supervisor", supervisor_node)
builder.add_node("diagnostic_agent", diagnostic_agent_node)
builder.add_node("physician_review", physician_review_node)
builder.add_node("report_agent", report_agent_node)

# Nœud d’exécution des tools (ask_patient, recommend_interim_care)
tools_node = ToolNode(tools=[ask_patient, recommend_interim_care])
builder.add_node("tools", tools_node)

# --Point d’entrée--------------------------------------------------------
builder.add_edge(START, "supervisor")

# --Transitions du Supervisor---------------------------------------------
def route_supervisor(state: MedicalState) -> str:
    """
    Lit le champ 'next' de l’état et route vers le bon nœud.
    """
    destination = state.get("next", "diagnostic_agent")
    if destination == "FINISH":
        return END
    return destination

builder.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "diagnostic_agent": "diagnostic_agent",
        "physician_review": "physician_review",
        "report_agent": "report_agent",
        END: END,
    }
)

# --Transitions DiagnosticAgent------------------------------------------
def route_diagnostic(state: MedicalState) -> str:
    """
    Si le DiagnosticAgent a émis des tool_calls, aller vers 'tools'.
    Sinon, retourner au supervisor.
    """
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    if (last_message and
        hasattr(last_message, "tool_calls") and
        last_message.tool_calls):
        return "tools"
    return "supervisor"

builder.add_conditional_edges(
    "diagnostic_agent",
    route_diagnostic,
    {
        "tools": "tools",
        "supervisor": "supervisor",
    }
)

# Après exécution des tools : retour au DiagnosticAgent
builder.add_edge("tools", "diagnostic_agent")

# Physician Review et ReportAgent retournent toujours au Supervisor
builder.add_edge("physician_review", "supervisor")
builder.add_edge("report_agent", "supervisor")

# --Compilation avec checkpointer (persistance en mémoire)---------------
checkpointer = MemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["physician_review"]  # Interruption avant la revue médecin
)
