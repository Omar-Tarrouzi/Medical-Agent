from langchain_core.messages import SystemMessage, AIMessage
from langgraph.prebuilt import ToolNode
from app.state import MedicalState
from app.llm import llm
from app.tools.patient_tools import ask_patient, recommend_interim_care

DIAGNOSTIC_PROMPT = """
Tu es un agent d’orientation clinique préliminaire.
Ton rôle :
1. Poser 5 questions successives au patient via le tool 'ask_patient'.
2. Analyser les réponses pour produire une synthèse clinique.
3. Générer une recommandation intermédiaire via 'recommend_interim_care'.

IMPORTANT :
- N’établis JAMAIS de diagnostic définitif.
- Reste factuel et prudent dans ta synthèse.
- Utilise le tool 'ask_patient' avec l’index correct (0 à 4).
- Après 5 questions, produis la synthèse et la recommandation.
"""

# LLM avec les tools liés
llm_with_tools = llm.bind_tools([ask_patient, recommend_interim_care])

def diagnostic_agent_node(state: MedicalState) -> dict:
    """
    Agent de diagnostic : pose les questions et produit la synthèse clinique.
    """

    question_count = state.get("question_count", 0)
    patient_qa = state.get("patient_qa", [])
    messages = state.get("messages", [])
    initial_complaint = state.get("initial_complaint", "Non spécifié")

    # Construction du contexte
    context_parts = [
        f"Plainte initiale du patient : {initial_complaint}",
        f"Questions posées jusqu’à présent : {question_count}/5",
    ]
    if patient_qa:
        context_parts.append("Réponses patient enregistrées :")
        for qa in patient_qa:
            context_parts.append(f"- {qa}")

    context = "\n".join(context_parts)

    # Invocation du LLM avec les tools
    response = llm_with_tools.invoke([
        SystemMessage(content=DIAGNOSTIC_PROMPT),
        *messages,
        SystemMessage(content=context)
    ])

    updates = {"messages": [response]}

    # Traitement des appels d’outils
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "ask_patient":
                # La question sera posée via interrupt()
                # question_count sera incrémenté par le tool executor
                pass
            elif tool_call["name"] == "recommend_interim_care":
                # Le résultat sera capturé dans tool_messages
                pass

    # Mise à jour du compteur et synthèse
    new_qa = state.get("patient_qa", [])

    # Si on a toutes les réponses, produire la synthèse
    if question_count >= 5 and not state.get("diagnostic_summary"):
        qa_text = "\n".join(new_qa)
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
            SystemMessage(content="Tu es un assistant d’orientation clinique."),
            SystemMessage(content=synthesis_prompt)
        ])
        updates["diagnostic_summary"] = synthesis_response.content

    return updates
