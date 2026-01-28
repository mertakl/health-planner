import axios from 'axios';
import type {HealthGoal} from '../types';


const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const generatePlanStreaming = async (
    goal: HealthGoal,
    onEvent: (event: any) => void
): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/plans/generate`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            goal: goal.goal,
            current_level: goal.currentLevel,
            timeline: goal.timeline,
            constraints: goal.constraints,
        }),
    });

    if (!response.body) {
        throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const {value, done} = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, {stream: true});

        const events = buffer.split('\n\n');
        buffer = events.pop()!;

        for (const evt of events) {
            if (!evt.startsWith('data:')) continue;

            const json = evt.replace(/^data:\s*/, '');
            const parsed = JSON.parse(json);

            onEvent(parsed);
        }
    }
};


export const listPlans = async () => {
    const response = await api.get('/api/plans');
    return response.data;
};


export const updateTaskStatus = async (
    planId: string,
    weekNumber: number,
    taskId: string,
    completed: boolean
): Promise<void> => {
    const response = await api.patch(
        `api/plans/${planId}/weeks/${weekNumber}/tasks/${taskId}`, {completed});
    if (!response.status || response.status < 200 || response.status >= 300) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
}


export const deletePlan = async (planId: string) => {
    await api.delete(`/api/plans/${planId}`);
};