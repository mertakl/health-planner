import json
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from models import GoalPlan, WeeklyPlan, WeeklyTask

load_dotenv()


class HealthPlannerAI:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate_plan(self, goal: str, current_level: str, timeline: str, constraints: str = "") -> GoalPlan:
        prompt = ChatPromptTemplate.from_messages([
            ("system",
                """You are a professional health and fitness coach. Create a detailed, actionable weekly plan.
            
                Return ONLY valid JSON matching this structure:
                {{
                  "overview": "A 2-3 sentence overview of the plan",
                  "weeks": [
                    {{
                      "week": 1,
                      "focus": "Brief focus area for the week",
                      "tasks": [
                        {{
                          "title": "Task title",
                          "description": "Detailed description with specific instructions",
                          "duration": "Expected time (e.g., '30 mins', '3x per week')"
                        }}
                      ]
                    }}
                  ]
                }}
                
                Create {num_weeks} weeks. Each week should have 3-5 specific, actionable tasks.
                Make tasks progressive - start easy and increase difficulty.
                Be specific with numbers, sets, reps, distances, etc."""),
                ("human", """Goal: {goal}
                Current Level: {current_level}
                Timeline: {timeline}
                Constraints: {constraints}
                
                Generate a detailed weekly plan.""")
        ])

        # Parse timeline to weeks
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

        num_weeks = min(num_weeks, 16)  # Cap at 16 weeks

        chain = prompt | self.llm

        response = chain.invoke({
            "goal": goal,
            "current_level": current_level,
            "timeline": timeline,
            "constraints": constraints or "None",
            "num_weeks": num_weeks
        })

        # Parse response
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        data = json.loads(content)

        # Build structured plan
        weeks = []
        for week_data in data["weeks"]:
            tasks = []
            for i, task_data in enumerate(week_data["tasks"]):
                tasks.append(WeeklyTask(
                    id=str(uuid.uuid4()),
                    title=task_data["title"],
                    description=task_data["description"],
                    duration=task_data["duration"],
                    completed=False
                ))

            weeks.append(WeeklyPlan(
                week=week_data["week"],
                focus=week_data["focus"],
                tasks=tasks
            ))

        return GoalPlan(
            id=str(uuid.uuid4()),
            goal=goal,
            overview=data["overview"],
            weeks=weeks,
            created_at=datetime.now().isoformat()
        )
