from langchain_core.messages import SystemMessage, HumanMessage
from app.state import MedicalState
from app.llm import llm
from typing import Literal

# Prompt du superviseur
SUPERVISOR_PROMPT = """
Tu es le superviseur d’un système d’orientation clinique.
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
    Nœud Supervisor : analyse l’état et décide de la prochaine étape.
    """

    # Lfrom langchain_core.messages import SystemMessage, HumanMessage
from app.state import MedicalState
from app.llm import llm
from typing import Literal

# Prompt du superviseur
SUPERVISOR_PROMPT = """
Tu es le superviseur d’un système d’orientation clinique.
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
    Nœud Supervisor : analyse l’état et décide de la prochaine étape.
    """

    # Lecture des champs clés de l’état
    question_count = state.get("question_count", 0)
    diagnostic_summary = state.get("diagnostic_summary", "")
    physician_treatment = state.get("physician_treatment", "")
    final_report = state.get("final_report", "")

    # Construction du contexte pour le LLM
    context = f"""
    Etat actuel du workflow :
    - Nombre de questions posées : {question_count}/5
    - Synthèse clinique produite : {"OUI" if diagnostic_summary else "NON"}
    - Traitement médecin reçu : {"OUI" if physician_treatment else "NON"}
    - Rapport final produit : {"OUI" if final_report else "NON"}

    Quelle est la prochaine étape ?
    """

    # Appel du LLM avec prompt système + contexte humain
    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=context)
    ])

    next_step = response.content.strip().lower()

    # Validation de la réponse
    valid_steps = ["diagnostic_agent", "physician_review", "report_agent", "finish"]

    if next_step not in valid_steps:
        # Fallback déterministe
        if not diagnostic_summary or question_count < 5:
            next_step = "diagnostic_agent"
        elif not physician_treatment:
            next_step = "physician_review"
        elif not final_report:
            next_step = "report_agent"
        else:
            next_step = "FINISH"

    return {"next": next_step.upper() if next_step == "finish" else next_step}

    context = f"""
    Etat actuel du workflow :
    - Nombre de questions posées : {question_count}/5
    - Synthèse clinique produite : {"OUI" if diagnostic_summary else "NON"}
    - Traitement médecin reçu : {"OUI" if physician_treatment else "NON"}
    - Rapport final produit : {"OUI" if final_report else "NON"}

    Quelle est la prochaine étape ?
    """

    # Appel du LLM avec prompt système + contexte humain
    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=context)
    ])

    next_step = response.content.strip().lower()

    # Validation de la réponse
    valid_steps = ["diagnostic_agent", "physician_review", "report_agent", "finish"]

    if next_step not in valid_steps:
        # Fallback déterministe
        if not diagnostic_summary or question_count < 5:
            next_step = "diagnostic_agent"
        elif not physician_treatment:
            next_step = "physician_review"
        elif not final_report:
            next_step = "report_agent"
        else:
            next_step = "FINISH"

    return {"next": next_step.upper() if next_step == "finish" else next_step}
