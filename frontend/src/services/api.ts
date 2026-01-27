import axios from 'axios';
import type {HealthGoal, GoalPlan} from '../types';


const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const generatePlan = async (goal: HealthGoal): Promise<GoalPlan> => {
    const response = await api.post('/api/generate-plan', {
        goal: goal.goal,
        current_level: goal.currentLevel,
        timeline: goal.timeline,
        constraints: goal.constraints,
    });
    return response.data;
};

export const healthCheck = async (): Promise<boolean> => {
    try {
        await api.get('/health');
        return true;
    } catch {
        return false;
    }
};