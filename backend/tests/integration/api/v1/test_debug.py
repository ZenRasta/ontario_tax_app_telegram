import pytest

@pytest.mark.asyncio
async def test_debug_strategies_endpoint(client):
    resp = await client.get('/api/v1/debug/strategies')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert 'GM' in data
    assert len(data) > 0
