"""Plan builder for constructing plans from streaming events."""
import logging
import uuid
from typing import Optional

from backend.schemas.plan import GoalPlan, WeeklyPlan, WeeklyTask

logger = logging.getLogger(__name__)


class PlanBuilder:
    """Builds a complete plan from streaming events."""

    def __init__(self, plan_id: str, goal: str, created_at: str):
        """Initialize"""
        self.plan_id = plan_id
        self.goal = goal
        self.created_at = created_at
        self.overview: Optional[str] = None
        self.weeks: dict[int, WeeklyPlan] = {}

    def add_overview(self, overview: str) -> None:
        """Set the plan overview."""
        self.overview = overview
        logger.debug(f"Overview added to plan {self.plan_id}")

    def start_week(self, week_num: int, focus: str) -> None:
        """Initialize a new week."""
        self.weeks[week_num] = WeeklyPlan(
            week=week_num,
            focus=focus,
            tasks=[]
        )
        logger.debug(f"Week {week_num} started in plan {self.plan_id}")

    def add_task(self, week_num: int, task_data: dict) -> bool:
        """Add a task to a specific week."""
        if week_num not in self.weeks:
            logger.warning(
                f"Attempted to add task to non-existent week {week_num} "
                f"in plan {self.plan_id}"
            )
            return False

        try:
            task = WeeklyTask(
                id=str(uuid.uuid4()),
                title=task_data["title"],
                description=task_data["description"],
                duration=task_data["duration"],
                completed=False
            )
            self.weeks[week_num].tasks.append(task)
            logger.debug(
                f"Task '{task.title}' added to week {week_num} "
                f"in plan {self.plan_id}"
            )
            return True
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid task data: {e}")
            return False

    def build(self) -> Optional[GoalPlan]:
        """Build the final GoalPlan object."""
        if not self.overview:
            logger.error(
                f"Cannot build plan {self.plan_id}: missing overview"
            )
            return None

        if not self.weeks:
            logger.error(
                f"Cannot build plan {self.plan_id}: no weeks defined"
            )
            return None

        # Make sure each week has tasks
        for week_num, week in self.weeks.items():
            if not week.tasks:
                logger.error(
                    f"Cannot build plan {self.plan_id}: "
                    f"week {week_num} has no tasks"
                )
                return None

        try:
            plan = GoalPlan(
                id=self.plan_id,
                goal=self.goal,
                overview=self.overview,
                weeks=list(self.weeks.values()),
                created_at=self.created_at
            )
            logger.info(f"Plan {self.plan_id} built successfully")
            return plan
        except ValueError as e:
            logger.error(f"Plan validation failed: {e}")
            return None

    def get_stats(self) -> dict:
        """Get current building statistics."""
        total_tasks = sum(len(week.tasks) for week in self.weeks.values())
        return {
            "plan_id": self.plan_id,
            "has_overview": self.overview is not None,
            "weeks_count": len(self.weeks),
            "total_tasks": total_tasks,
            "complete": self.overview is not None and len(self.weeks) > 0
        }
