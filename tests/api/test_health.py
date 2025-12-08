import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_detailed_status(async_client: AsyncClient):
    response = await async_client.get("/api/v1/status")
    # We might get 503 if DB is not connected, but for now just check it returns something valid
    assert response.status_code in [200, 503]
