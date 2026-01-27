import {Button} from "./ui/button.tsx";
import {Card, CardContent, CardHeader, CardTitle} from "./ui/card.tsx";
import type {GoalPlan} from "../types";
import React from "react";

interface SavedPlansProps {
    plans: GoalPlan[];
    onSelect: (plan: GoalPlan) => void;
    onDelete: (id: string) => void;
}

export const SavedPlans: React.FC<SavedPlansProps> = ({plans, onSelect, onDelete}) => {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Saved Plans</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
                {plans.map(plan => (
                    <div
                        key={plan.id}
                        className="flex items-center justify-between border p-3 rounded"
                    >
                        <div
                            className="cursor-pointer"
                            onClick={() => onSelect(plan)}
                        >
                            <p className="font-medium">{plan.goal}</p>
                            <p className="text-xs text-gray-500">
                                {new Date(plan.createdAt).toLocaleDateString()}
                            </p>
                        </div>
                        <Button
                            variant="destructive"
                            onClick={() => onDelete(plan.id)}
                        >
                            Delete
                        </Button>
                    </div>
                ))}
            </CardContent>
        </Card>
    );
};
