import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.db.models import SavedPlan
from backend.schemas.plan import GoalPlan

logger = logging.getLogger(__name__)


class PlanRepository:
    """Plan Repository for  database operations."""

    def __init__(self, db: Session):
        self.db = db

    def save(
            self,
            plan: GoalPlan,
            current_level: str,
            timeline: str,
            constraints: Optional[str] = None,
            user_id: Optional[str] = None
    ) -> bool:
        """Save a plan to the database."""
        try:
            saved_plan = SavedPlan(
                id=plan.id,
                goal=plan.goal,
                current_level=current_level,
                timeline=timeline,
                constraints=constraints or "",
                overview=plan.overview,
                plan_data=plan.model_dump_json(),
                user_id=user_id,
                created_at=datetime.fromisoformat(plan.created_at)
            )
            self.db.add(saved_plan)
            self.db.commit()
            logger.info(f"Plan {plan.id} saved successfully")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save plan {plan.id}: {str(e)}")
            return False

    def update_task_status(self, plan_id: str, week_number: int,
                           task_id: str, completed: bool) -> bool:
        try:
            saved_plan = self.db.query(SavedPlan).filter(
                SavedPlan.id == plan_id
            ).with_for_update().first()

            plan = GoalPlan.model_validate_json(saved_plan.plan_data)

            for week in plan.weeks:
                if week.week == week_number:
                    for task in week.tasks:
                        if task.id == task_id:
                            task.completed = completed
                            saved_plan.plan_data = plan.model_dump_json()
                            self.db.commit()
                            return True

            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update task: {str(e)}")
            return False

    def get_by_id(self, plan_id: str) -> Optional[GoalPlan]:
        """Retrieve a plan by ID."""
        try:
            saved_plan = self.db.query(SavedPlan).filter(
                SavedPlan.id == plan_id
            ).first()

            if saved_plan:
                return GoalPlan.model_validate_json(saved_plan.plan_data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving plan {plan_id}: {str(e)}")
            return None

    def list(self) -> list[GoalPlan]:
        """List all saved plans."""
        try:
            query = self.db.query(SavedPlan)

            saved_plans = query.order_by(SavedPlan.created_at.desc()).all()

            # Convert to GoalPlan objects
            plans = []
            for saved_plan in saved_plans:
                plan_data = json.loads(saved_plan.plan_data)
                plans.append(GoalPlan(**plan_data))

            return plans

        except Exception as e:
            logger.error(f"Failed to list plans: {str(e)}")
            return []

    def delete(self, plan_id: str) -> bool:
        """Delete a plan by ID."""
        try:
            plan = self.db.query(SavedPlan).filter(
                SavedPlan.id == plan_id
            ).first()

            if plan:
                self.db.delete(plan)
                self.db.commit()
                logger.info(f"Plan {plan_id} deleted successfully")
                return True

            logger.warning(f"Plan {plan_id} not found for deletion")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting plan {plan_id}: {str(e)}")
            return False
