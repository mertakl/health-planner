import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.plan import PlanCreate, PlanResponse, TaskStatusUpdate, GoalPlan
from backend.services.plan_service import PlanService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plans", tags=["plans"])


def get_plan_service(db: Session = Depends(get_db)) -> PlanService:
    """Dependency to get plan service."""
    return PlanService(db)


@router.post("/generate", response_class=StreamingResponse)
async def generate_plan(
        plan_request: PlanCreate,
        service: PlanService = Depends(get_plan_service)
):
    """Generate a personalized health plan with streaming."""
    try:
        return StreamingResponse(
            service.generate_and_save_plan(plan_request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )
    except Exception as e:
        logger.exception("Error generating plan")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{plan_id}/weeks/{week_number}/tasks/{task_id}")
async def update_task_status(
        plan_id: str,
        week_number: int,
        task_id: str,
        task_update: TaskStatusUpdate,
        service: PlanService = Depends(get_plan_service)
):
    """Update the completion status of a specific task."""
    try:
        success = await service.update_task_status(
            plan_id=plan_id,
            week_number=week_number,
            task_id=task_id,
            completed=task_update.completed
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Plan or task not found"
            )

        return {"success": True, "message": "Task updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error updating task status")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[GoalPlan])
def list_plans(service: PlanService = Depends(get_plan_service)):
    """List saved plans."""
    return service.list_plans()


@router.delete("/{plan_id}")
def delete_plan(
        plan_id: str,
        service: PlanService = Depends(get_plan_service)
):
    """Delete a plan."""
    success = service.delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "success": True,
        "message": "Plan deleted successfully"
    }
