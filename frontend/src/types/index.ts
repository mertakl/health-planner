export interface HealthGoal {
    goal: string;
    currentLevel: string;
    timeline: string;
    constraints: string;
}

export interface WeeklyTask {
    id: string;
    title: string;
    description: string;
    duration: string;
    completed: boolean;
}

export interface WeeklyPlan {
    week: number;
    focus: string;
    tasks: WeeklyTask[];
}

export interface GoalPlan {
    id: string;
    goal: string;
    overview: string;
    weeks: WeeklyPlan[];
    createdAt: string;
}