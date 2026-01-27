import json
import logging
import os
import uuid
from datetime import datetime
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from db_models import SavedPlan
from db_session import SessionLocal
from pydantic_models import GoalPlan, WeeklyTask, WeeklyPlan

load_dotenv()

logger = logging.getLogger(__name__)


class HealthPlannerAI:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
            streaming=True
        )

    def _calculate_weeks(self, timeline: str) -> int:
        """Calculate number of weeks from timeline string."""
        timeline_lower = timeline.lower()
        if 'month' in timeline_lower:
            months = int(''.join(filter(str.isdigit, timeline_lower))) if any(
                c.isdigit() for c in timeline_lower) else 3
            num_weeks = months * 4
        elif 'week' in timeline_lower:
            num_weeks = int(''.join(filter(str.isdigit, timeline_lower))) if any(
                c.isdigit() for c in timeline_lower) else 12
        else:
            num_weeks = 12

        return min(num_weeks, 16)

    def _create_prompt(self, num_weeks: int) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            (
                "system",
                f"""
                You are a professional health and fitness coach.
                
                You MUST stream your response as newline-delimited JSON objects.
                Each line must be a COMPLETE and VALID JSON object.
                DO NOT wrap in markdown.
                DO NOT explain anything.
                DO NOT output anything except JSON.
                
                Event types and schemas:
                
                1. Overview (send once):
                {{{{"type":"overview","value":"2-3 sentence overview"}}}}
                
                2. Week start (send before tasks of that week):
                {{{{"type":"week_start","week":1,"focus":"Weekly focus"}}}}
                
                3. Task (send each task separately):
                {{{{
                  "type":"task",
                  "week":1,
                  "task": {{{{
                    "title":"Task title",
                    "description":"Clear instructions",
                    "duration":"30 mins"
                  }}}}
                }}}}
                
                4. Done (send once at the end):
                {{{{"type":"done"}}}}
                
                Rules:
                - Create exactly {num_weeks} weeks
                - Each week must have 3–5 tasks
                - Tasks should be progressive and actionable
                - Be specific with numbers, reps, time, etc.
                
                Start streaming immediately.
                """
            ),
            (
                "human",
                """
                    Goal: {goal}
                    Current Level: {current_level}
                    Timeline: {timeline}
                    Constraints: {constraints}
                """
            )
        ])

    async def generate_plan_streaming(
            self,
            goal: str,
            current_level: str,
            timeline: str,
            constraints: str = "",
            user_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Streams structured JSON events and saves the plan on completion.
        """
        num_weeks = self._calculate_weeks(timeline)
        prompt = self._create_prompt(num_weeks)
        chain = prompt | self.llm

        plan_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        # Full plan
        overview: Optional[str] = None
        weeks: dict[int, WeeklyPlan] = {}

        # Initialize buffer
        buffer = ""

        try:
            async for chunk in chain.astream({
                "goal": goal,
                "current_level": current_level,
                "timeline": timeline,
                "constraints": constraints or "None",
            }):
                content = chunk.content
                if not content:
                    continue

                # Append incoming token to buffer
                buffer += content

                # Process buffer only when a complete line (newline) is found
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning(f"Incomplete JSON line skipped: {line}")
                        continue

                    event_type = event.get("type")

                    # Handle events
                    if event_type == "overview":
                        overview = event["value"]
                        yield self._sse(event)

                    elif event_type == "week_start":
                        week_num = event["week"]
                        weeks[week_num] = WeeklyPlan(
                            week=week_num,
                            focus=event["focus"],
                            tasks=[]
                        )
                        yield self._sse(event)

                    elif event_type == "task":
                        week_num = event["week"]
                        task_data = event["task"]

                        # Make sure week exists
                        if week_num in weeks:
                            weeks[week_num].tasks.append(
                                WeeklyTask(
                                    id=str(uuid.uuid4()),
                                    title=task_data["title"],
                                    description=task_data["description"],
                                    duration=task_data["duration"],
                                    completed=False
                                )
                            )
                            # Stream the task
                            yield self._sse(event)

                    elif event_type == "done":
                        # Final validation
                        if not overview or not weeks:
                            logger.error("Attempted to save incomplete plan")
                        else:
                            plan = GoalPlan(
                                id=plan_id,
                                goal=goal,
                                overview=overview,
                                weeks=list(weeks.values()),
                                created_at=created_at
                            )

                            self._save_plan(
                                plan=plan,
                                current_level=current_level,
                                timeline=timeline,
                                constraints=constraints,
                                user_id=user_id
                            )

                        # Complete
                        yield self._sse({
                            "type": "done",
                            "plan_id": plan_id
                        })
                        return

        except Exception as e:
            logger.exception("Error during streaming generation")
            yield self._sse({
                "type": "error",
                "message": str(e)
            })

    def _save_plan(
            self,
            plan: GoalPlan,
            current_level: str,
            timeline: str,
            constraints: str,
            user_id: Optional[str] = None
    ):
        """Save plan to database."""
        db = SessionLocal()
        try:
            saved_plan = SavedPlan(
                id=plan.id,
                goal=plan.goal,
                current_level=current_level,
                timeline=timeline,
                constraints=constraints,
                overview=plan.overview,
                plan_data=plan.model_dump_json(),
                user_id=user_id
            )
            db.add(saved_plan)
            db.commit()
            logger.info(f"Plan {plan.id} saved successfully")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving plan: {str(e)}")
            raise
        finally:
            db.close()

    def get_plan(self, plan_id: str) -> Optional[GoalPlan]:
        """Retrieve a saved plan by ID."""
        db = SessionLocal()
        try:
            saved_plan = db.query(SavedPlan).filter(SavedPlan.id == plan_id).first()
            if saved_plan:
                return GoalPlan.model_validate_json(saved_plan.plan_data)
            return None
        finally:
            db.close()

    def list_plans(self, user_id: Optional[str] = None, limit: int = 10) -> list[dict]:
        """List saved plans (optionally filtered by user)."""
        db = SessionLocal()
        try:
            query = db.query(SavedPlan)
            if user_id:
                query = query.filter(SavedPlan.user_id == user_id)

            plans = query.order_by(SavedPlan.created_at.desc()).limit(limit).all()

            return [
                {
                    "id": plan.id,
                    "goal": plan.goal,
                    "overview": plan.overview,
                    "created_at": plan.created_at.isoformat(),
                    "timeline": plan.timeline
                }
                for plan in plans
            ]
        finally:
            db.close()

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a saved plan."""
        db = SessionLocal()
        try:
            plan = db.query(SavedPlan).filter(SavedPlan.id == plan_id).first()
            if plan:
                db.delete(plan)
                db.commit()
                return True
            return False
        finally:
            db.close()

    def _sse(self, payload: dict) -> str:
        return f"data: {json.dumps(payload)}\n\n"
