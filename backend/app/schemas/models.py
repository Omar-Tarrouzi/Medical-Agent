from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ConsultationStatus(str, Enum):
    PENDING = "pending"
    QUESTIONING = "questioning"
    AWAITING_MD = "awaiting_physician"
    REPORTING = "reporting"
    COMPLETED = "completed"


class StartConsultationRequest(BaseModel):
    initial_complaint: str = Field(
        ...,
        description="Description initiale du problème de santé par le patient",
        example="J’ai de la fièvre depuis deux jours et une toux sèche.",
    )
    patient_name: Optional[str] = Field(
        None, description="Nom du patient (anonymisé)"
    )
    patient_age: Optional[int] = Field(
        None, ge=0, le=150, description="Âge du patient"
    )


class PatientAnswerRequest(BaseModel):
    thread_id: str = Field(..., description="Identifiant unique de la consultation")
    answer: str = Field(..., description="Réponse du patient à la question posée")


class PhysicianReviewRequest(BaseModel):
    thread_id: str = Field(..., description="Identifiant unique de la consultation")
    treatment: str = Field(
        ..., description="Traitement ou conduite à tenir proposé par le médecin"
    )
    approved: bool = Field(
        True, description="Le médecin valide-t-il la synthèse ?"
    )
    comments: Optional[str] = Field(
        None, description="Commentaires additionnels"
    )


class ConsultationStateResponse(BaseModel):
    thread_id: str
    status: ConsultationStatus
    question_count: int = 0
    current_question: Optional[str] = None
    diagnostic_summary: Optional[str] = None
    interim_care: Optional[str] = None
    final_report: Optional[str] = None
