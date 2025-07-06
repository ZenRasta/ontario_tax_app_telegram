
import { ExplainRequest } from './types/api';

const API_PREFIX = import.meta.env.VITE_API_PREFIX ?? '/v1';

// POST /v1/compare
export async function runSimulation(data: Record<string, any>) {
  return fetch(`${API_PREFIX}/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id: crypto.randomUUID(), ...data }),
  }).then(r => r.json());
}

// POST /v1/explain
export async function getExplanation(payload: ExplainRequest) {
  return fetch(`${API_PREFIX}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(r => r.json());
}
