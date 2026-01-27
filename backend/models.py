from pydantic import BaseModel
from typing import List, Optional

class HealthGoalInput(BaseModel):
    goal: str
    current_level: str
    timeline: str
    constraints: Optional[str] = ""

class WeeklyTask(BaseModel):
    id: str
    title: str
    description: str
    duration: str
    completed: bool = False

class WeeklyPlan(BaseModel):
    week: int
    focus: str
    tasks: List[WeeklyTask]

class GoalPlan(BaseModel):
    id: str
    goal: str
    overview: str
    weeks: List[WeeklyPlan]
    created_at: str