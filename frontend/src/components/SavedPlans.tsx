import {Button} from "./ui/button.tsx";
import {Card, CardContent, CardHeader, CardTitle} from "./ui/card.tsx";
import type {GoalPlan} from "../types";
import React from "react";

interface SavedPlansProps {
    plans: GoalPlan[];
    onSelect: (plan: GoalPlan) => void;
    onDelete: (id: string) => void;
    selectedPlanId?: string;
}

export const SavedPlans: React.FC<SavedPlansProps> = ({
                                                          plans,
                                                          onSelect,
                                                          onDelete,
                                                          selectedPlanId
                                                      }) => {
    if (plans.length === 0) {
        return null;
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Saved Plans ({plans.length})</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
                {plans.map(plan => (
                    <div
                        key={plan.id}
                        className={`flex items-center justify-between border p-3 rounded transition-colors ${
                            selectedPlanId === plan.id
                                ? 'border-blue-500 bg-blue-50'
                                : 'hover:bg-gray-50'
                        }`}
                    >
                        <div
                            className="cursor-pointer flex-1"
                            onClick={() => onSelect(plan)}
                        >
                            <p className="font-medium">{plan.goal}</p>
                            <p className="text-xs text-gray-500">
                                {new Date(plan.createdAt).toLocaleDateString()}
                            </p>
                            {plan.weeks.length > 0 && (
                                <p className="text-xs text-gray-400 mt-1">
                                    {plan.weeks.length} weeks
                                </p>
                            )}
                        </div>
                        <Button
                            variant="destructive"
                            onClick={(e) => {
                                e.stopPropagation();
                                if (window.confirm('Are you sure you want to delete this plan?')) {
                                    onDelete(plan.id);
                                }
                            }}>
                            Delete
                        </Button>
                    </div>
                ))}
            </CardContent>
        </Card>
    );
};
