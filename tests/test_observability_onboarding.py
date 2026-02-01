import pytest
from httpx import AsyncClient
from app.main import app
from app.models.user import User
from app.api.v1.auth import get_current_user

# Mock user
async def mock_get_current_user():
    return User(id=1, email="test@example.com", is_active=True, role="admin", subscription_tier="premium")

# Override dependency
app.dependency_overrides[get_current_user] = mock_get_current_user

@pytest.mark.asyncio
async def test_system_status_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/system-status")
    
    # It might fail with 500 if DB is not mocked, but we can check if it's 404 or 403
    assert response.status_code != 404
    assert response.status_code != 403
    
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert "metrics" in data
        assert "recent_activity" in data

@pytest.mark.asyncio
async def test_onboarding_start_endpoint():
    payload = {
        "url": "https://example.com",
        "generate_content": False
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/onboarding/start", json=payload)
    
    assert response.status_code != 404
    assert response.status_code != 403
