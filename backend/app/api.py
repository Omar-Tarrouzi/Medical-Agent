import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command

from app.graph import graph
from app.schemas.models import (
    StartConsultationRequest,
    PatientAnswerRequest,
    PhysicianReviewRequest,
    ConsultationStateResponse,
    ConsultationStatus,
)

# Initialisation de l'application
app = FastAPI(
    title="Systeme Multi-Agents Medical",
    description=(
        "API d'orientation clinique preliminaire. "
        "Ce systeme ne remplace pas une consultation medicale."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (pour le frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper : lecture de l'etat
def get_consultation_state(thread_id: str) -> dict:
    """Recupere l'etat LangGraph pour un thread_id donne."""
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.get_state(config)
    if not state or not state.values:
        raise HTTPException(status_code=404, detail=f"Consultation {thread_id} introuvable.")
    return state

def determine_status(state_values: dict, interrupts) -> ConsultationStatus:
    """Deduit le statut de la consultation depuis l'etat."""
    if state_values.get("final_report"):
        return ConsultationStatus.COMPLETED
    if interrupts:
        interrupt_type = interrupts[0].value.get("type") if interrupts else None
        if interrupt_type == "physician_review":
            return ConsultationStatus.AWAITING_MD
        return ConsultationStatus.QUESTIONING
    if state_values.get("diagnostic_summary"):
        return ConsultationStatus.REPORTING
    return ConsultationStatus.QUESTIONING

# Endpoints

@app.post("/sessions/start", summary="Creer une nouvelle session")
async def create_session():
    """Genere un identifiant de session unique."""
    thread_id = str(uuid.uuid4())
    return {"thread_id": thread_id, "message": "Session creee avec succes."}

@app.post("/consultation/start", summary="Demarrer une consultation")
async def start_consultation(request: StartConsultationRequest):
    """
    Lance le workflow de consultation.
    Le graphe demarre et pose immediatement la premiere question.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "initial_complaint": request.initial_complaint,
        "question_count": 0,
        "patient_qa": [],
        "messages": [],
    }

    try:
        # Lancer le graphe--il s'interrompra sur la premiere question
        result = graph.invoke(initial_state, config)
    except Exception:
        # Le graphe peut s'interrompre (interrupt)--c'est normal
        pass

    # Lire l'etat apres invocation
    state = get_consultation_state(thread_id)
    interrupts = state.tasks[0].interrupts if state.tasks else []

    current_question = None
    if interrupts:
        interrupt_data = interrupts[0].value
        if isinstance(interrupt_data, dict):
            current_question = interrupt_data.get("question")

    return {
        "thread_id": thread_id,
        "status": determine_status(state.values, interrupts),
        "current_question": current_question,
        "question_count": state.values.get("question_count", 0),
    }

@app.post("/consultation/resume", summary="Repondre a une question patient")
async def resume_consultation(request: PatientAnswerRequest):
    """
    Reprend le graphe apres la reponse d'un patient a une question.
    """
    config = {"configurable": {"thread_id": request.thread_id}}

    try:
        # Command(resume=...) reprend le graphe depuis l'interruption
        result = graph.invoke(
            Command(resume=request.answer),
            config
        )
    except Exception:
        pass

    state = get_consultation_state(request.thread_id)
    interrupts = state.tasks[0].interrupts if state.tasks else []

    current_question = None
    interrupt_type = None
    if interrupts:
        interrupt_data = interrupts[0].value
        if isinstance(interrupt_data, dict):
            interrupt_type = interrupt_data.get("type")
            current_question = interrupt_data.get("question")

    return {
        "thread_id": request.thread_id,
        "status": determine_status(state.values, interrupts),
        "question_count": state.values.get("question_count", 0),
        "current_question": current_question,
        "interrupt_type": interrupt_type,
        "diagnostic_summary": state.values.get("diagnostic_summary"),
        "interim_care": state.values.get("interim_care"),
    }

@app.post("/physician/review", summary="Soumettre l'avis du medecin")
async def submit_physician_review(request: PhysicianReviewRequest):
    """
    Soumet l'avis du medecin traitant et reprend le workflow.
    Le graphe produira ensuite le rapport final.
    """
    config = {"configurable": {"thread_id": request.thread_id}}

    physician_input = {
        "treatment": request.treatment,
        "approved": request.approved,
        "comments": request.comments,
    }

    try:
        graph.invoke(Command(resume=physician_input), config)
    except Exception:
        pass

    state = get_consultation_state(request.thread_id)
    interrupts = state.tasks[0].interrupts if state.tasks else []

    return {
        "thread_id": request.thread_id,
        "status": determine_status(state.values, interrupts),
        "physician_treatment": state.values.get("physician_treatment"),
        "final_report": state.values.get("final_report"),
    }

@app.get("/consultation/{thread_id}", summary="Etat d'une consultation")
async def get_consultation(thread_id: str):
    """Retourne l'etat complet d'une consultation."""
    state = get_consultation_state(thread_id)
    interrupts = state.tasks[0].interrupts if state.tasks else []

    current_question = None
    if interrupts:
        interrupt_data = interrupts[0].value
        if isinstance(interrupt_data, dict):
            current_question = interrupt_data.get("question")

    return ConsultationStateResponse(
        thread_id=thread_id,
        status=determine_status(state.values, interrupts),
        question_count=state.values.get("question_count", 0),
        current_question=current_question,
        diagnostic_summary=state.values.get("diagnostic_summary"),
        interim_care=state.values.get("interim_care"),
        final_report=state.values.get("final_report"),
    )

@app.get("/consultation/{thread_id}/report", summary="Rapport final")
async def get_report(thread_id: str):
    """Retourne le rapport final de la consultation."""
    state = get_consultation_state(thread_id)
    report = state.values.get("final_report")
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non encore genere.")
    return {"thread_id": thread_id, "report": report}

@app.get("/health", summary="Sante de l'API")
async def health_check():
    return {"status": "ok", "service": "medical-multiagentapi"}