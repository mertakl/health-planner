import {useEffect, useState} from 'react';
import {GoalForm} from './components/GoalForm';
import {PlanDisplay} from './components/PlanDisplay';
import type {GoalPlan, HealthGoal} from './types';
import {deletePlan, generatePlanStreaming, listPlans} from './services/api';
import {SavedPlans} from "./components/SavedPlans.tsx";

function App() {
    const [loading, setLoading] = useState(false);
    const [plan, setPlan] = useState<GoalPlan | null>(null);
    const [savedPlans, setSavedPlans] = useState<GoalPlan[]>([]);
    const [error, setError] = useState<string>('');


    useEffect(() => {
        listPlans().then(setSavedPlans).catch(console.error);
    }, []);

    const handleGoalSubmit = async (goal: HealthGoal) => {
        setLoading(true);
        setError('');
        setPlan({
            id: '',
            goal: goal.goal,
            overview: '',
            weeks: [],
            createdAt: new Date().toISOString(),
        });

        try {
            await generatePlanStreaming(goal, (event) => {
                setPlan(prev => {
                    if (!prev) return prev;

                    switch (event.type) {
                        case 'overview':
                            return {
                                ...prev,
                                overview: event.value,
                            };

                        case 'week_start':
                            return {
                                ...prev,
                                weeks: [
                                    ...prev.weeks,
                                    {
                                        week: event.week,
                                        focus: event.focus,
                                        tasks: [],
                                    },
                                ],
                            };

                        case 'task':
                            return {
                                ...prev,
                                weeks: prev.weeks.map(w =>
                                    w.week === event.week
                                        ? {...w, tasks: [...w.tasks, event.task]}
                                        : w
                                ),
                            };

                        case 'done':
                            return {
                                ...prev,
                                id: event.plan_id,
                            };

                        default:
                            return prev;
                    }
                });
            });
        } catch (err) {
            console.error(err);
            setError('Failed to generate plan. Please try again.');
        } finally {
            setLoading(false);
        }
    };


    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-6xl mx-auto p-6">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">
                        Health Goal Planner
                    </h1>
                    <p className="text-lg text-gray-600">
                        Transform your health aspirations into actionable weekly plans
                    </p>
                </div>

                {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
                        {error}
                    </div>
                )}

                <div className="grid md:grid-cols-2 gap-6">
                    <GoalForm onSubmit={handleGoalSubmit} loading={loading}/>
                    {plan && <PlanDisplay plan={plan}/>}
                </div>
                {savedPlans.length > 0 && (
                    <div className="grid md:grid-cols-1 gap-2 pt-5">
                        <SavedPlans
                            plans={savedPlans}
                            onSelect={setPlan}
                            onDelete={async (id) => {
                                await deletePlan(id);
                                setSavedPlans(plans => plans.filter(p => p.id !== id));
                            }}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;