from langgraph.types import interrupt, Command
from app.state import MedicalState

def physician_review_node(state: MedicalState) -> dict:
    """
    Nœud Human-in-the-Loop représentant le médecin traitant.
    Ce nœud :
    1. Suspend l’exécution et envoie la synthèse au médecin.
    2. Attend la saisie du médecin (traitement / conduite à tenir).
    3. Reprend et enregistre l’avis dans l’état.
    """

    # Construction du payload envoyé au médecin
    physician_payload = {
        "type": "physician_review",
        "title": "Revue du médecin traitant",
        "diagnostic_summary": state.get("diagnostic_summary", "Synthèse non disponible"),
        "interim_care": state.get("interim_care", "Recommandation non disponible"),
        "patient_qa": state.get("patient_qa", []),
        "initial_complaint": state.get("initial_complaint", ""),
        "instructions": (
            "Veuillez examiner la synthèse clinique préliminaire et "
            "proposer un traitement ou une conduite à tenir. "
            "Votre avis sera intégré dans le rapport final."
        )
    }

    # Suspension du graphe -- retour au médecin
    physician_input = interrupt(physician_payload)

    # À la reprise, physician_input contient le dict fourni
    # par le médecin via Command(resume={...})
    if isinstance(physician_input, dict):
        treatment = physician_input.get("treatment", "")
        approved = physician_input.get("approved", True)
        comments = physician_input.get("comments", "")

        physician_treatment = treatment
        if comments:
            physician_treatment += f"\n\nCommentaires additionnels : {comments}"
        if not approved:
            physician_treatment += "\n[Le médecin a émis des réserves sur la synthèse]"
    else:
        # Cas où physician_input est une simple chaîne
        physician_treatment = str(physician_input)

    return {"physician_treatment": physician_treatment}
