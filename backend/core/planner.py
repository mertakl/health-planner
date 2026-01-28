"""Health planner AI core logic."""
import json
import logging
import uuid
from datetime import datetime
from typing import AsyncIterator, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from backend.config import get_settings
from backend.core.plan_builder import PlanBuilder
from backend.core.streaming_parser import StreamingJSONParser
from backend.schemas.plan import GoalPlan

settings = get_settings()
logger = logging.getLogger(__name__)


class HealthPlannerAI:
    """Health and fitness planner."""

    def __init__(self):
        """Initialize the planner with LLM configuration."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            streaming=True
        )

    def _calculate_weeks(self, timeline: str) -> int:
        """Calculate number of weeks from timeline string."""
        timeline_lower = timeline.lower()

        if 'month' in timeline_lower:
            months = self._extract_number(timeline_lower, default=3)
            num_weeks = months * 4
        elif 'week' in timeline_lower:
            num_weeks = self._extract_number(timeline_lower, default=12)
        else:
            num_weeks = settings.DEFAULT_PLAN_WEEKS

        return min(num_weeks, settings.MAX_PLAN_WEEKS)

    @staticmethod
    def _extract_number(text: str, default: int) -> int:
        """Extract first number from text or return default."""
        digits = ''.join(filter(str.isdigit, text))
        return int(digits) if digits else default

    def _create_prompt(self, num_weeks: int) -> ChatPromptTemplate:
        """Create the chat prompt template for plan generation."""
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
                {{{{"type":"done"}}}}\n
                
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
            parser: StreamingJSONParser = StreamingJSONParser()
    ) -> AsyncIterator[tuple[str, Optional[GoalPlan]]]:
        """Generate a plan with streaming output."""
        num_weeks = self._calculate_weeks(timeline)
        prompt = self._create_prompt(num_weeks)
        chain = prompt | self.llm

        plan_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        # Initialize components
        builder = PlanBuilder(plan_id, goal, created_at)

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

                # Process chunk and get complete events
                events = parser.process_chunk(content)

                for event in events:
                    event_type = event.get("type")

                    if event_type == "overview":
                        builder.add_overview(event["value"])
                        yield self._sse(event), None

                    elif event_type == "week_start":
                        builder.start_week(event["week"], event["focus"])
                        yield self._sse(event), None

                    elif event_type == "task":
                        if builder.add_task(event["week"], event["task"]):
                            yield self._sse(event), None

            for event in parser.flush():
                if event["type"] == "done":
                    plan = builder.build()
                    yield self._sse({"type": "done", "plan_id": plan_id}), plan
                    return
        except Exception as e:
            logger.exception("Error during streaming generation")
            error_event = {
                "type": "error",
                "message": str(e)
            }
            yield self._sse(error_event), None

    @staticmethod
    def _sse(payload: dict) -> str:
        """Format payload as Server-Sent Event."""
        return f"data: {json.dumps(payload)}\n\n"
