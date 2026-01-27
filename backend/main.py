import logging
from contextlib import asynccontextmanager
from typing import Annotated, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from ai_service import HealthPlannerAI
from db_session import get_session, create_db_and_tables
from pydantic_models import HealthGoalInput, GoalPlan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Health Goal Planner API")

# Fix CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development purpose only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = HealthPlannerAI()

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
def read_root():
    return {"message": "Health Goal Planner API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/generate-plan-stream")
async def generate_plan_stream(goal_input: HealthGoalInput):
    """Generate plan with streaming response (saves to database when complete)."""
    try:
        logger.info(f"Generating streaming plan for goal: {goal_input.goal}")

        return StreamingResponse(
            ai_service.generate_plan_streaming(
                goal=goal_input.goal,
                current_level=goal_input.current_level,
                timeline=goal_input.timeline,
                constraints=goal_input.constraints
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error generating streaming plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans/{plan_id}", response_model=GoalPlan)
async def get_plan(plan_id: str):
    """Retrieve a saved plan by ID."""
    plan = ai_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.get("/api/plans")
async def list_plans(user_id: Optional[str] = None, limit: int = 10):
    """List saved plans."""
    plans = ai_service.list_plans(user_id=user_id, limit=limit)
    return {"plans": plans}


@app.delete("/api/plans/{plan_id}")
async def delete_plan(plan_id: str):
    """Delete a saved plan."""
    success = ai_service.delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
