export async function runSimulation(data: any) {
  return fetch('/api/v1/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json());
}
