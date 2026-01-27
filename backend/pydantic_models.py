from typing import Optional

from pydantic import BaseModel


class WeeklyTask(BaseModel):
    id: str
    title: str
    description: str
    duration: str
    completed: bool = False


class WeeklyPlan(BaseModel):
    week: int
    focus: str
    tasks: list[WeeklyTask]


class GoalPlan(BaseModel):
    id: str
    goal: str
    overview: str
    weeks: list[WeeklyPlan]
    created_at: str


class HealthGoalInput(BaseModel):
    goal: str
    current_level: str
    timeline: str
    constraints: str = ""
    user_id: Optional[str] = None
