from langchain_core.tools import tool
from langgraph.types import interrupt

# Les 5 questions médicales standardisées
QUESTIONS = [
    "Depuis combien de temps avez-vous ces symptômes ? (heures, jours, semaines)",
    "Sur une échelle de 1 à 10, comment évaluez-vous l'intensité de votre gêne ?",
    "Avez-vous de la fièvre ? Si oui, quelle température avez-vous relevée ?",
    "Avez-vous d'autres symptômes associés ? (maux de tête, nausées, toux, etc.)",
    "Prenez-vous actuellement des médicaments ? Avez-vous des allergies connues ?"
]


@tool
def ask_patient(question_index: int) -> str:
    """
    Pose une question au patient et attend sa réponse via une interruption.

    Args:
        question_index: Index de la question (0 à 4)

    Returns:
        La réponse saisie par le patient
    """

    if question_index < 0 or question_index >= len(QUESTIONS):
        return "Index de question invalide."

    question_text = QUESTIONS[question_index]

    # interrupt() suspend l'exécution du graphe et retourne
    # le contrôle à l'opérateur (patient). La valeur retournée
    # est la réponse fournie lors de la reprise.
    patient_answer = interrupt({
        "type": "patient_question",
        "question_index": question_index,
        "question": question_text,
        "instructions": "Répondez à la question médicale ci-dessus."
    })

    return f"Q: {question_text} | R: {patient_answer}"


@tool
def recommend_interim_care(symptoms_summary: str) -> str:
    """
    Génère une recommandation de soins intermédiaire prudente.

    Args:
        symptoms_summary: Résumé des symptômes du patient

    Returns:
        Recommandation intermédiaire
    """
    # Cette logique peut être enrichie avec des règles métier
    recommendations = []

    summary_lower = symptoms_summary.lower()

    # Recommandations générales systématiques
    recommendations.append("Repos et bonne hydratation recommandés.")

    # Détection de signaux d'alarme (red flags)
    red_flags = [
        "difficul", "respir", "douleur thorac", "perte connaissance",
        "paralys", "convuls", "sang", "hemor"
    ]
    if any(rf in summary_lower for rf in red_flags):
        recommendations.append(
            "ALERTE : Symptômes nécessitant une consultation médicale urgente."
        )
        recommendations.append(
            "Rendez-vous immédiatement aux urgences ou appelez le 15/18."
        )
    else:
        recommendations.append(
            "Surveillance de l'évolution des symptômes recommandée."
        )
        recommendations.append(
            "Consultez un médecin rapidement si aggravation ou persistance > 48h."
        )

    recommendations.append(
        "RAPPEL : Cette recommandation ne remplace pas l'avis d'un professionnel de santé."
    )

    return " ".join(recommendations)
