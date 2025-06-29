export async function runSimulation(data: Record<string, any>) {
  return fetch('/api/v1/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      request_id: crypto.randomUUID(),
      ...data
    })
  }).then(r => r.json());
}
