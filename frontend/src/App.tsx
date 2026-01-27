import {useState} from 'react';
import {GoalForm} from './components/GoalForm';
import {Card, CardContent, CardHeader, CardTitle} from './components/ui/card';
import type {GoalPlan, HealthGoal} from "./types";


function App() {
    const [loading, setLoading] = useState(false);
    const [plan, setPlan] = useState<GoalPlan | null>(null);

    const handleGoalSubmit = async (goal: HealthGoal) => {
        setLoading(true);
        // TODO: API call
        console.log('Goal submitted:', goal);
        setTimeout(() => {
            setLoading(false);
        }, 2000);
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

                <div className="grid md:grid-cols-2 gap-6">
                    <GoalForm onSubmit={handleGoalSubmit} loading={loading}/>

                    <Card>
                        <CardHeader>
                            <CardTitle>Your Personalized Plan</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {plan ? (
                                <p>Plan will render here</p>
                            ) : (
                                <p className="text-gray-500">
                                    Fill out the form to generate your personalized health plan
                                </p>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

export default App;