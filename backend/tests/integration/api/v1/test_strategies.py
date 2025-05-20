import pytest

from app.data_models.scenario import GoalEnum

@pytest.mark.asyncio
async def test_strategies_basic(client):
    resp = await client.get('/api/v1/strategies')
    assert resp.status_code == 200
    data = resp.json()
    assert 'strategies' in data
    assert isinstance(data['strategies'], list)
    assert data['recommended'] == []

@pytest.mark.asyncio
async def test_strategies_with_goal(client):
    resp = await client.get(f'/api/v1/strategies?goal={GoalEnum.MAXIMIZE_SPENDING.value}')
    assert resp.status_code == 200
    data = resp.json()
    assert set(data['recommended']) == {'CD', 'GM', 'LS'}
