from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import HealthGoalInput, GoalPlan
from ai_service import HealthPlannerAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Health Goal Planner API")

# Fix CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development purpose only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = HealthPlannerAI()


@app.get("/")
def read_root():
    return {"message": "Health Goal Planner API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/generate-plan", response_model=GoalPlan)
async def generate_plan(goal_input: HealthGoalInput):
    try:
        logger.info(f"Generating plan for goal: {goal_input.goal}")
        plan = ai_service.generate_plan(
            goal=goal_input.goal,
            current_level=goal_input.current_level,
            timeline=goal_input.timeline,
            constraints=goal_input.constraints
        )
        logger.info(f"Plan generated successfully with {len(plan.weeks)} weeks")
        return plan
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
