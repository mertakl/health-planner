from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class SavedPlan(SQLModel, table=True):
    __tablename__ = "health_plans"  # optional, but fine if you want a custom name

    id: str = Field(primary_key=True)
    goal: str
    current_level: Optional[str] = None
    timeline: Optional[str] = None
    constraints: Optional[str] = None
    overview: Optional[str] = None
    plan_data: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


