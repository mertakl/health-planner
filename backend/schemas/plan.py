from typing import Optional

from pydantic import BaseModel, Field, field_validator


class WeeklyTask(BaseModel):
    """A single task within a weekly plan."""

    id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    duration: str = Field(..., min_length=1, max_length=200)
    completed: bool = False


class WeeklyPlan(BaseModel):
    """Weekly plan containing focus area and tasks."""

    week: int = Field(..., ge=1, le=52)
    focus: str = Field(..., min_length=1, max_length=500)
    tasks: list[WeeklyTask] = Field(default_factory=list)


class GoalPlan(BaseModel):
    """Complete goal plan with all weeks."""

    id: str
    goal: str = Field(..., min_length=1, max_length=500)
    overview: str = Field(..., min_length=1)
    weeks: list[WeeklyPlan] = Field(..., min_items=1)
    created_at: str  # ISO format datetime

    @field_validator('weeks')
    @classmethod
    def validate_weeks(cls, v: list[WeeklyPlan]) -> list[WeeklyPlan]:
        """Ensure weeks are sequential."""
        if not v:
            raise ValueError("Plan must have at least one week")

        week_numbers = [week.week for week in v]
        if week_numbers != list(range(1, len(v) + 1)):
            raise ValueError("Week numbers must be sequential starting from 1")

        return v


class PlanCreate(BaseModel):
    """Request schema for creating a new plan."""

    goal: str = Field(..., min_length=10, max_length=500,
                      description="The health or fitness goal")
    current_level: str = Field(..., min_length=3, max_length=255,
                               description="Current fitness/health level")
    timeline: str = Field(..., min_length=3, max_length=255,
                          description="Desired timeline (e.g., '3 months', '12 weeks')")
    constraints: Optional[str] = Field(None, max_length=1000,
                                       description="Any limitations or constraints")
    user_id: Optional[str] = Field(None, max_length=255)


class PlanSummary(BaseModel):
    """Summary of a saved plan for listing."""

    id: str
    goal: str
    overview: str
    timeline: str
    created_at: str

    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    """Schema for updating task completion status."""
    completed: bool


class PlanResponse(BaseModel):
    """Response schema for plan retrieval."""

    plan: GoalPlan

    class Config:
        from_attributes = True


class StreamEvent(BaseModel):
    """Base schema for streaming events."""

    type: str


class OverviewEvent(StreamEvent):
    """Overview event in stream."""

    type: str = "overview"
    value: str


class WeekStartEvent(StreamEvent):
    """Week start event in stream."""

    type: str = "week_start"
    week: int
    focus: str


class TaskEvent(StreamEvent):
    """Task event in stream."""

    type: str = "task"
    week: int
    task: dict


class DoneEvent(StreamEvent):
    """Completion event in stream."""

    type: str = "done"
    plan_id: str


class ErrorEvent(StreamEvent):
    """Error event in stream."""

    type: str = "error"
    message: str
