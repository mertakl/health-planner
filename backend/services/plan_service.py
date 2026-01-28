"""Service layer for plan operations."""
import logging
from typing import AsyncIterator, Optional, List

from sqlalchemy.orm import Session

from backend.core.planner import HealthPlannerAI
from backend.db.repositories.plan_repository import PlanRepository
from backend.schemas.plan import GoalPlan, PlanCreate, PlanResponse

logger = logging.getLogger(__name__)


class PlanService:
    """Service for managing health plans."""

    def __init__(self, db: Session):
        """Initialize"""
        self.db = db
        self.planner = HealthPlannerAI()
        self.repository = PlanRepository(db)

    async def generate_and_save_plan(
            self,
            plan_request: PlanCreate
    ) -> AsyncIterator[str]:
        """Stream plan."""
        plan_to_save: Optional[GoalPlan] = None

        async for sse_event, plan in self.planner.generate_plan_streaming(
                goal=plan_request.goal,
                current_level=plan_request.current_level,
                timeline=plan_request.timeline,
                constraints=plan_request.constraints or ""
        ):
            yield sse_event

            # If final event assign the plan to save
            if plan:
                plan_to_save = plan

        # Save the plan
        if plan_to_save:
            success = self.repository.save(
                plan=plan_to_save,
                current_level=plan_request.current_level,
                timeline=plan_request.timeline,
                constraints=plan_request.constraints,
                user_id=plan_request.user_id
            )

            if not success:
                logger.error(f"Failed to save plan {plan_to_save.id}")
            else:
                logger.info(f"Plan {plan_to_save.id} saved successfully")

    def get_plan(self, plan_id: str) -> Optional[GoalPlan]:
        """Retrieve a plan by ID."""
        return self.repository.get_by_id(plan_id)

    def list_plans(self) -> List[PlanResponse]:
        """List plans."""
        plans = self.repository.list()
        return plans

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan."""
        return self.repository.delete(plan_id)
