import {useState, useEffect, useCallback} from 'react';
import {GoalForm} from './components/GoalForm';
import {PlanDisplay} from './components/PlanDisplay';
import {SavedPlans} from './components/SavedPlans';


import type {HealthGoal, GoalPlan} from './types';
import {ErrorAlert} from "./components/ui/error-alert.tsx";
import {
    generatePlanStreaming,
    listPlans,
    updateTaskStatus,
    deletePlan
} from "./services/api.ts";

function App() {
    const [loading, setLoading] = useState(false);
    const [plan, setPlan] = useState<GoalPlan | null>(null);
    const [savedPlans, setSavedPlans] = useState<GoalPlan[]>([]);
    const [error, setError] = useState<string>('');

    // Load saved plans
    useEffect(() => {
        loadSavedPlans();
    }, []);

    const loadSavedPlans = useCallback(async () => {
        try {
            const plans = await listPlans();
            setSavedPlans(plans);
        } catch (err) {
            console.error('Failed to load saved plans:', err);
        }
    }, []);

    const handleGoalSubmit = async (goal: HealthGoal) => {
        setLoading(true);
        setError('');
        // Initialize empty plan
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
                            const weekExists = prev.weeks.some(w => w.week === event.week);
                            if (weekExists) return prev;

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
                            loadSavedPlans();
                            return {
                                ...prev,
                                id: event.plan_id,
                            };

                        case 'error':
                            setError(event.message || 'An error occurred');
                            return prev;

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

    const handleTaskToggle = async (
        weekNumber: number,
        taskId: string,
        completed: boolean
    ) => {
        if (!plan?.id) return;

        // Optimistic update
        const updatePlanTasks = (p: GoalPlan) => ({
            ...p,
            weeks: p.weeks.map(w =>
                w.week === weekNumber
                    ? {
                        ...w,
                        tasks: w.tasks.map(t =>
                            t.id === taskId ? {...t, completed} : t
                        )
                    }
                    : w
            ),
        });

        setPlan(prev => prev ? updatePlanTasks(prev) : prev);
        setSavedPlans(prev => prev.map(p => p.id === plan.id ? updatePlanTasks(p) : p));

        try {
            await updateTaskStatus(plan.id, weekNumber, taskId, completed);
        } catch (err) {
            console.error('Failed to update task:', err);

            // Revert on error
            setPlan(prev => prev ? updatePlanTasks({...prev, weeks: prev.weeks}) : prev);
            setSavedPlans(prev => prev.map(p =>
                p.id === plan.id ? updatePlanTasks(p) : p
            ));
            setError('Failed to update task. Please try again.');
        }
    };

    const handlePlanSelect = useCallback((selectedPlan: GoalPlan) => {
        setPlan(selectedPlan);
        setError('');
    }, []);

    const handlePlanDelete = async (id: string) => {
        try {
            await deletePlan(id);
            setSavedPlans(plans => plans.filter(p => p.id !== id));

            if (plan?.id === id) {
                setPlan(null);
            }
        } catch (err) {
            console.error('Failed to delete plan:', err);
            setError('Failed to delete plan. Please try again.');
        }
    };

    const handleNewPlan = useCallback(() => {
        setPlan(null);
        setError('');
    }, []);

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">

                <header className="mb-8 text-center">
                    <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-3 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                        Health Goal Planner
                    </h1>
                    <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                        Transform your health aspirations into actionable weekly plans
                    </p>
                </header>


                {error && <ErrorAlert message={error} onDismiss={() => setError('')}/>}


                <div className="grid lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-1">
                        <GoalForm
                            onSubmit={handleGoalSubmit}
                            loading={loading}
                            onNewPlan={plan ? handleNewPlan : undefined}
                        />
                    </div>

                    <div className="lg:col-span-2">
                        {plan ? (
                            <PlanDisplay
                                plan={plan}
                                onTaskToggle={handleTaskToggle}
                                isStreaming={loading}
                            />
                        ) : (
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                                <div className="max-w-sm mx-auto">
                                    <div
                                        className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor"
                                             viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                        No Plan Selected
                                    </h3>
                                    <p className="text-gray-600">
                                        Create a new plan or select an existing one from below
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Saved Plans Section */}
                {savedPlans.length > 0 && (
                    <div className="mt-8">
                        <SavedPlans
                            plans={savedPlans}
                            onSelect={handlePlanSelect}
                            onDelete={handlePlanDelete}
                            selectedPlanId={plan?.id}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;