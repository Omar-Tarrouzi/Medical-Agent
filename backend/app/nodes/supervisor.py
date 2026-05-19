from langchain_core.messages import SystemMessage, HumanMessage
from app.state import MedicalState
from app.llm import llm
from typing import Literal

# Prompt du superviseur
SUPERVISOR_PROMPT = """
Tu es le superviseur d'un système d'orientation clinique.
Tu coordonnes le workflow entre les agents spécialisés.

Règles de routage :
1 - Si question_count == 0 et aucune synthèse : router vers "diagnostic_agent"
2 - Si question_count < 5 : router vers "diagnostic_agent" (continuer les questions)
3 - Si question_count == 5 et pas de synthèse : router vers "diagnostic_agent" (produire synthèse)
4 - Si synthèse produite et pas de traitement médecin : router vers "physician_review"
5 - Si traitement médecin reçu et pas de rapport : router vers "report_agent"
6 - Si rapport final produit : router vers "FINISH"

Réponds UNIQUEMENT avec un mot parmi :
diagnostic_agent | physician_review | report_agent | FINISH
"""


def supervisor_node(state: MedicalState) -> dict:
    """
    Nœud Supervisor : analyse l'état et décide de la prochaine étape de manière déterministe.
    """
    question_count = state.get("question_count", 0)
    diagnostic_summary = state.get("diagnostic_summary", "")
    physician_treatment = state.get("physician_treatment", "")
    final_report = state.get("final_report", "")

    # Routage strict et déterministe
    if not diagnostic_summary or question_count < 5:
        next_step = "diagnostic_agent"
    elif not physician_treatment:
        next_step = "physician_review"
    elif not final_report:
        next_step = "report_agent"
    else:
        next_step = "FINISH"

    return {"next": next_step}
