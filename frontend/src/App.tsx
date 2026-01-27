import {useState} from 'react';
import {GoalForm} from './components/GoalForm';
import {PlanDisplay} from './components/PlanDisplay';
import type {HealthGoal, GoalPlan} from './types';
import {generatePlan} from './services/api';

function App() {
    const [loading, setLoading] = useState(false);
    const [plan, setPlan] = useState<GoalPlan | null>(null);
    const [error, setError] = useState<string>('');

    const handleGoalSubmit = async (goal: HealthGoal) => {
        setLoading(true);
        setError('');

        try {
            const generatedPlan = await generatePlan(goal);
            setPlan(generatedPlan);
        } catch (err) {
            setError('Failed to generate plan. Please try again.');
            console.error(err);
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
            </div>
        </div>
    );
}

export default App;