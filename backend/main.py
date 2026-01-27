from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import HealthGoalInput, GoalPlan
from ai_service import HealthPlannerAI

app = FastAPI(title="Health Goal Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = HealthPlannerAI()


@app.get("/")
def read_root():
    return {"message": "Health Goal Planner API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/generate-plan", response_model=GoalPlan)
async def generate_plan(goal_input: HealthGoalInput):
    try:
        plan = ai_service.generate_plan(
            goal=goal_input.goal,
            current_level=goal_input.current_level,
            timeline=goal_input.timeline,
            constraints=goal_input.constraints
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
