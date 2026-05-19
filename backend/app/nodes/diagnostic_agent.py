from langchain_core.messages import SystemMessage, AIMessage
from app.state import MedicalState
from app.llm import llm
from app.tools.patient_tools import ask_patient, recommend_interim_care

DIAGNOSTIC_PROMPT = """
Tu es un agent d'orientation clinique préliminaire.
Ton rôle est de poser 5 questions au patient pour comprendre ses symptômes.

IMPORTANT :
- Pose EXACTEMENT UNE SEULE question à la fois.
- N'appelle le tool 'ask_patient' qu'UNE SEULE FOIS par réponse.
- Ne pose pas de questions au-delà de l'index 4.
"""

def diagnostic_agent_node(state: MedicalState) -> dict:
    """
    Agent de diagnostic : pose les questions et produit la synthèse clinique.
    """
    question_count = state.get("question_count", 0)
    patient_qa = list(state.get("patient_qa", []))
    messages = state.get("messages", [])
    initial_complaint = state.get("initial_complaint", "Non spécifié")
    interim_care = state.get("interim_care", "")

    updates = {}

    # 1. Traitement de TOUS les retours des tools récents (mise à jour de l'état)
    # On parcourt les messages à l'envers pour trouver tous les ToolMessages ajoutés
    new_qas = []
    for msg in reversed(messages):
        if getattr(msg, "type", "") == "tool":
            if msg.name == "ask_patient" and msg.content not in patient_qa and msg.content not in new_qas:
                new_qas.insert(0, msg.content)
        else:
            break  # On arrête dès qu'on tombe sur un AIMessage ou HumanMessage
            
    if new_qas:
        patient_qa.extend(new_qas)
        question_count += len(new_qas)
        updates["patient_qa"] = patient_qa
        updates["question_count"] = question_count

    # Construction du contexte pour le LLM
    context_parts = [
        f"Plainte initiale du patient : {initial_complaint}",
        f"Questions posées jusqu'à présent : {question_count}/5",
    ]
    if patient_qa:
        context_parts.append("Réponses patient enregistrées :")
        for qa in patient_qa:
            context_parts.append(f"- {qa}")

    context = "\n".join(context_parts)

    # 2. Invocation du LLM ou génération directe de la synthèse
    if question_count < 5:
        # On continue de poser des questions
        bound_llm = llm.bind_tools([ask_patient])
        response = bound_llm.invoke([
            SystemMessage(content=DIAGNOSTIC_PROMPT),
            *messages,
            SystemMessage(content=context)
        ])
        updates["messages"] = [response]
    else:
        # On a atteint 5 questions, on génère directement la synthèse sans relancer de questions
        if not state.get("diagnostic_summary"):
            qa_text = "\n".join(patient_qa)
            synthesis_prompt = f"""
            Sur la base de ces informations patient :
            Plainte initiale : {initial_complaint}
            Questions/Réponses :
            {qa_text}

            Produis une synthèse clinique préliminaire structurée avec :
            1. Symptômes principaux identifiés
            2. Durée et intensité
            3. Facteurs associés
            4. Orientations possibles (sans diagnostic définitif)

            Rappel : reste prudent et factuel.
            """

            synthesis_response = llm.invoke([
                SystemMessage(content="Tu es un assistant d'orientation clinique."),
                SystemMessage(content=synthesis_prompt)
            ])
            updates["diagnostic_summary"] = synthesis_response.content
            
            # Et on génère programmatiquement la recommandation
            interim = recommend_interim_care.invoke({"symptoms_summary": synthesis_response.content})
            updates["interim_care"] = interim
            
            # Ajout d'un message fictif pour satisfaire le routeur
            updates["messages"] = [AIMessage(content="Synthèse clinique et recommandations générées avec succès.")]

    return updates
