from typing import Annotated, Optional
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages


class MedicalState(TypedDict, total=False):
    """
    État partagé entre tous les agents du graphe médical.
    Chaque champ représente une donnée qui évolue au fil du workflow.
    Le superviseur lit le champ `next` pour décider quel agent appeler.
    """

    # -- Messages (conversation complète) -------------------------------
    # add_messages est un reducer : il accumule les messages plutôt que de les écraser.
    messages: Annotated[list, add_messages]

    # -- Routage --------------------------------------------------------
    # Le Supervisor écrit dans ce champ pour indiquer quel agent doit être exécuté ensuite.
    next: Literal[
        "diagnostic_agent",
        "physician_review",
        "report_agent",
        "FINISH",
    ]

    # -- Données patient ------------------------------------------------
    # Nombre de questions posées au patient (max 5)
    question_count: int

    # Symptôme initial saisi par le patient
    initial_complaint: str

    # Liste des questions/réponses (format: "Q: ... / R: ...")
    patient_qa: list[str]

    # -- Synthèse clinique ----------------------------------------------
    # Résumé produit par le DiagnosticAgent
    diagnostic_summary: str

    # -- Recommandation intermédiaire -----------------------------------
    # Produite par le tool recommend_interim_care
    interim_care: str

    # -- Validation médecin ---------------------------------------------
    # Traitement ou conduite à tenir proposé par le médecin
    physician_treatment: str

    # -- Rapport final --------------------------------------------------
    # Produit par le ReportAgent
    final_report: str
