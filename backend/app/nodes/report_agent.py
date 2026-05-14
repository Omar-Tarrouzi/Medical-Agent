from langchain_core.messages import SystemMessage
from app.state import MedicalState
from app.llm import llm
from datetime import datetime

REPORT_PROMPT = """
Tu es l’agent de génération de rapports cliniques.
Tu produis un rapport final structuré, clair et professionnel.
Le rapport doit inclure obligatoirement la mention :
"Ce système ne remplace pas une consultation médicale."

Structure du rapport :
1. En-tête (date, référence)
2. Motif de consultation
3. Synthèse clinique préliminaire
4. Recommandation intermédiaire
5. Avis du médecin traitant
6. Conclusion et recommandations finales
7. Avertissement légal
"""

def report_agent_node(state: MedicalState) -> dict:
    """
    Génère le rapport final structuré de la consultation.
    """
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    report_data = f"""
    Date : {now}
    Plainte initiale : {state.get("initial_complaint", "N/A")}
    Nombre de questions : {state.get("question_count", 0)}/5

    Questions/Réponses patient :
    {chr(10).join(state.get("patient_qa", []) or ["Aucune réponse enregistrée"])}

    Synthèse clinique préliminaire :
    {state.get("diagnostic_summary", "Non disponible")}

    Recommandation intermédiaire :
    {state.get("interim_care", "Non disponible")}

    Avis du médecin traitant :
    {state.get("physician_treatment", "Non disponible")}
    """

    # Appel du LLM pour générer le rapport
    response = llm.invoke([
        SystemMessage(content=REPORT_PROMPT),
        SystemMessage(content=f"Génère le rapport à partir de ces informations :\n{report_data}")
    ])

    final_report = response.content

    # Vérification de la mention obligatoire
    mandatory_mention = "Ce système ne remplace pas une consultation médicale."
    if mandatory_mention not in final_report:
        final_report += f"\n\n---\n{mandatory_mention}"

    return {"final_report": final_report}
