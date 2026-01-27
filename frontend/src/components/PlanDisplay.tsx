import React from 'react';
import {Card, CardContent, CardHeader, CardTitle} from './ui/card';
import type {GoalPlan} from '../types';

interface PlanDisplayProps {
    plan: GoalPlan;
}

export const PlanDisplay: React.FC<PlanDisplayProps> = ({plan}) => {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Your Personalized Plan</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                <div>
                    <h3 className="font-semibold text-lg mb-2">Overview</h3>
                    <p className="text-gray-600">{plan.overview}</p>
                </div>

                <div className="space-y-4">
                    {plan.weeks.map((week) => (
                        <div key={week.week} className="border rounded-lg p-4">
                            <div className="flex items-center justify-between mb-3">
                                <h4 className="font-semibold">Week {week.week}</h4>
                                <span className="text-sm text-gray-500">{week.focus}</span>
                            </div>

                            <div className="space-y-2">
                                {week.tasks.map((task) => (
                                    <div key={task.id} className="bg-gray-50 p-3 rounded">
                                        <div className="flex items-start">
                                            <input
                                                type="checkbox"
                                                checked={task.completed}
                                                className="mt-1 mr-3"
                                                readOnly
                                            />
                                            <div className="flex-1">
                                                <p className="font-medium">{task.title}</p>
                                                <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                                                <p className="text-xs text-gray-500 mt-1">{task.duration}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
};