import {useState} from 'react';

import type {GoalPlan, Task} from '../types';
import {Card, CardHeader, CardTitle, CardContent} from "./ui/card.tsx";

interface PlanDisplayProps {
    plan: GoalPlan;
    onTaskToggle?: (weekNumber: number, taskId: string, completed: boolean) => void;
    isStreaming?: boolean;
}

export const PlanDisplay: React.FC<PlanDisplayProps> = ({
                                                            plan,
                                                            onTaskToggle,
                                                            isStreaming = false
                                                        }) => {
    const [updatingTasks, setUpdatingTasks] = useState<Set<string>>(new Set());
    const [expandedWeeks, setExpandedWeeks] = useState<Set<number>>(new Set([1]));

    const handleCheckboxChange = async (
        weekNumber: number,
        task: Task,
        newCompleted: boolean
    ) => {
        if (!onTaskToggle || !plan.id) return;

        const taskKey = `${weekNumber}-${task.id}`;
        setUpdatingTasks(prev => new Set(prev).add(taskKey));

        try {
            await onTaskToggle(weekNumber, task.id, newCompleted);
        } catch (error) {
            console.error('Failed to update task status:', error);
        } finally {
            setUpdatingTasks(prev => {
                const newSet = new Set(prev);
                newSet.delete(taskKey);
                return newSet;
            });
        }
    };

    const toggleWeek = (weekNumber: number) => {
        setExpandedWeeks(prev => {
            const newSet = new Set(prev);
            if (newSet.has(weekNumber)) {
                newSet.delete(weekNumber);
            } else {
                newSet.add(weekNumber);
            }
            return newSet;
        });
    };

    const expandAll = () => {
        setExpandedWeeks(new Set(plan.weeks.map(w => w.week)));
    };

    const collapseAll = () => {
        setExpandedWeeks(new Set());
    };

    const calculateProgress = () => {
        const totalTasks = plan.weeks.reduce((sum, week) => sum + week.tasks.length, 0);
        const completedTasks = plan.weeks.reduce(
            (sum, week) => sum + week.tasks.filter(t => t.completed).length,
            0
        );
        return totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    };

    const progress = calculateProgress();

    return (
        <Card className="h-fit">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                        Your Personalized Plan
                        {isStreaming && (
                            <span className="flex items-center gap-2 text-sm font-normal text-blue-500">
                                <span className="animate-pulse">●</span>
                                Generating...
                            </span>
                        )}
                    </CardTitle>
                    {plan.weeks.length > 1 && (
                        <div className="flex gap-2">
                            <button
                                onClick={expandAll}
                                className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Expand All
                            </button>
                            <span className="text-gray-300">|</span>
                            <button
                                onClick={collapseAll}
                                className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Collapse All
                            </button>
                        </div>
                    )}
                </div>
            </CardHeader>
            <CardContent>
                {/* Progress Bar */}
                {plan.id && plan.weeks.length > 0 && (
                    <div className="mb-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">
                                Overall Progress
                            </span>
                            <span className="text-sm font-semibold text-blue-600">
                                {progress}%
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div
                                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2.5 rounded-full transition-all duration-500"
                                style={{width: `${progress}%`}}
                            />
                        </div>
                    </div>
                )}

                {/* Scrollable Content */}
                <div className="space-y-6 max-h-[calc(100vh-300px)] overflow-y-auto pr-2 custom-scrollbar">
                    {/* Overview */}
                    {plan.overview && (
                        <div
                            className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-100">
                            <h3 className="font-semibold text-lg mb-2 text-gray-900 flex items-center gap-2">
                                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor"
                                     viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                                Overview
                            </h3>
                            <p className="text-gray-700 leading-relaxed">{plan.overview}</p>
                        </div>
                    )}

                    {/* Weekly Plans */}
                    {plan.weeks.length > 0 && (
                        <div className="space-y-3">
                            {plan.weeks.map((week) => {
                                const isExpanded = expandedWeeks.has(week.week);
                                const weekProgress = week.tasks.length > 0
                                    ? Math.round((week.tasks.filter(t => t.completed).length / week.tasks.length) * 100)
                                    : 0;

                                return (
                                    <div
                                        key={week.week}
                                        className="border border-gray-200 rounded-lg overflow-hidden bg-white hover:shadow-md transition-shadow"
                                    >
                                        {/* Week Header */}
                                        <button
                                            onClick={() => toggleWeek(week.week)}
                                            className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div
                                                    className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center font-semibold text-blue-700">
                                                    {week.week}
                                                </div>
                                                <div className="text-left">
                                                    <h4 className="font-semibold text-gray-900">
                                                        Week {week.week}
                                                    </h4>
                                                    {week.focus && (
                                                        <p className="text-sm text-gray-600">
                                                            {week.focus}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                {week.tasks.length > 0 && (
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-16 bg-gray-200 rounded-full h-2">
                                                            <div
                                                                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                                                style={{width: `${weekProgress}%`}}
                                                            />
                                                        </div>
                                                        <span
                                                            className="text-xs text-gray-600 font-medium min-w-[3rem]">
                                                            {week.tasks.filter(t => t.completed).length}/{week.tasks.length}
                                                        </span>
                                                    </div>
                                                )}
                                                <svg
                                                    className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                          d="M19 9l-7 7-7-7"/>
                                                </svg>
                                            </div>
                                        </button>

                                        {/* Week Tasks */}
                                        {isExpanded && week.tasks.length > 0 && (
                                            <div className="px-4 pb-4 space-y-2">
                                                {week.tasks.map((task) => {
                                                    const taskKey = `${week.week}-${task.id}`;
                                                    const isUpdating = updatingTasks.has(taskKey);
                                                    const canToggle = !isStreaming && plan.id && onTaskToggle;

                                                    return (
                                                        <div
                                                            key={task.id}
                                                            className={`bg-gray-50 p-3 rounded-lg hover:bg-gray-100 transition-colors ${
                                                                task.completed ? 'opacity-75' : ''
                                                            }`}
                                                        >
                                                            <div className="flex items-start gap-3">
                                                                <input
                                                                    type="checkbox"
                                                                    checked={task.completed}
                                                                    onChange={(e) =>
                                                                        handleCheckboxChange(
                                                                            week.week,
                                                                            task,
                                                                            e.target.checked
                                                                        )
                                                                    }
                                                                    disabled={!canToggle || isUpdating}
                                                                    className="mt-1 w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
                                                                />
                                                                <div className="flex-1 min-w-0">
                                                                    <p className={`font-medium text-gray-900 ${
                                                                        task.completed ? 'line-through text-gray-500' : ''
                                                                    }`}>
                                                                        {task.title}
                                                                    </p>
                                                                    <p className="text-sm text-gray-600 mt-1">
                                                                        {task.description}
                                                                    </p>
                                                                    {task.duration && (
                                                                        <div className="flex items-center gap-1 mt-2">
                                                                            <svg className="w-4 h-4 text-gray-400"
                                                                                 fill="none" stroke="currentColor"
                                                                                 viewBox="0 0 24 24">
                                                                                <path strokeLinecap="round"
                                                                                      strokeLinejoin="round"
                                                                                      strokeWidth={2}
                                                                                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                                                            </svg>
                                                                            <span className="text-xs text-gray-500">
                                                                                {task.duration}
                                                                            </span>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                                {isUpdating && (
                                                                    <div
                                                                        className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"/>
                                                                )}
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}

                                        {isExpanded && week.tasks.length === 0 && (
                                            <div className="px-4 pb-4 text-center text-gray-500 text-sm">
                                                No tasks yet
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {/* Empty State */}
                    {!plan.overview && plan.weeks.length === 0 && (
                        <div className="text-center py-12">
                            <div className="animate-pulse">
                                <div
                                    className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor"
                                         viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                                    </svg>
                                </div>
                                <p className="text-gray-500">Waiting for plan generation...</p>
                            </div>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
};