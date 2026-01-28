import React, {useState} from 'react';
import {Button} from './ui/button';
import {Card, CardContent, CardHeader, CardTitle} from './ui/card';
import type {HealthGoal} from "../types";


interface GoalFormProps {
    onSubmit: (goal: HealthGoal) => void;
    loading: boolean;
    onNewPlan?: () => void;
}

export const GoalForm: React.FC<GoalFormProps> = ({onSubmit, loading, onNewPlan}) => {
    const [formData, setFormData] = useState<HealthGoal>({
        goal: '',
        currentLevel: '',
        timeline: '',
        constraints: ''
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Tell Us About Your Goal</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            What's your health goal?
                        </label>
                        <textarea
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            rows={3}
                            placeholder="e.g., I want to lose 1 kg and build muscle"
                            value={formData.goal}
                            onChange={(e) => setFormData({...formData, goal: e.target.value})}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Current fitness level
                        </label>
                        <input
                            type="text"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="e.g., Beginner, no regular exercise"
                            value={formData.currentLevel}
                            onChange={(e) => setFormData({...formData, currentLevel: e.target.value})}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Timeline
                        </label>
                        <input
                            type="text"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="e.g., 3 months"
                            value={formData.timeline}
                            onChange={(e) => setFormData({...formData, timeline: e.target.value})}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Any constraints? (optional)
                        </label>
                        <input
                            type="text"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="e.g., No gym access, knee injury"
                            value={formData.constraints}
                            onChange={(e) => setFormData({...formData, constraints: e.target.value})}
                        />
                    </div>

                    <Button type="submit" disabled={loading} className="w-full">
                        {loading ? 'Generating Plan...' : 'Generate My Plan'}
                    </Button>
                    {onNewPlan && (
                        <Button
                            type="button"
                            onClick={onNewPlan}
                            variant="outline"
                            className="flex-1"
                        >
                            New Plan
                        </Button>
                    )}
                </form>
            </CardContent>
        </Card>
    );
};