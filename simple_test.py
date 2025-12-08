#!/usr/bin/env python3
"""
Simple Test Script for Multi-Client Social Media System
"""

import asyncio
import json
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

class SimpleTester:
    """Simple test harness"""

    def __init__(self):
        self.session = requests.Session()

    async def test_api_health(self):
        """Test if APIs are responding"""
        print("Testing API Health...")

        try:
            # Test root endpoint
            response = self.session.get(f"{API_BASE_URL}/")
            print(f"Root endpoint: {response.status_code}")

            # Test client onboarding endpoint (should return 405 for GET)
            response = self.session.get(f"{API_BASE_URL}/api/v1/clients/onboard")
            print(f"Client onboarding GET: {response.status_code} (expected 405)")

            # Test social accounts endpoint
            response = self.session.get(f"{API_BASE_URL}/api/v1/social/accounts")
            print(f"Social accounts: {response.status_code}")

            print("API health check completed!")
            return True

        except Exception as e:
            print(f"API health check failed: {e}")
            return False

    async def test_client_onboarding(self):
        """Test client onboarding with minimal data"""
        print("\nTesting Client Onboarding...")

        test_client = {
            "company_info": {
                "company_name": "Test Company",
                "industry": "Technology",
                "brand_voice": "professional"
            },
            "target_audience": {
                "primary_persona": "Developer",
                "pain_points": ["manual processes"],
                "goals": ["automation"]
            },
            "content_preferences": {
                "key_messages": ["We build great software"],
                "competitors": ["Other Company"],
                "unique_value_props": ["Better quality"]
            },
            "social_media_accounts": {
                "platforms": ["twitter"],
                "existing_handles": {"twitter": "@testcompany"}
            }
        }

        try:
            response = self.session.post(
                f"{API_BASE_URL}/api/v1/clients/onboard",
                json=test_client
            )

            print(f"Onboarding response: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Success! Client ID: {result.get('client_id')}")
                print(f"Status: {result.get('onboarding_status')}")
                return result.get('client_id')
            else:
                print(f"Failed: {response.text}")
                return None

        except Exception as e:
            print(f"Client onboarding test failed: {e}")
            return None

    async def test_content_generation(self):
        """Test content generation"""
        print("\nTesting Content Generation...")

        try:
            # Test posting content
            post_data = {
                "content": "Testing Unitasa's AI marketing automation! #MarketingAutomation #AI",
                "platforms": ["twitter"],
                "scheduled_at": None,
                "campaign_id": None
            }

            response = self.session.post(
                f"{API_BASE_URL}/api/v1/social/posts",
                json=post_data
            )

            print(f"Content posting response: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Post result: {result.get('message')}")
            else:
                print(f"Failed: {response.text}")

        except Exception as e:
            print(f"Content generation test failed: {e}")

    async def run_tests(self):
        """Run all tests"""
        print("STARTING SIMPLE SYSTEM TESTS")
        print("="*40)
        print(f"Time: {datetime.utcnow().isoformat()}")
        print(f"API URL: {API_BASE_URL}")

        # Test 1: API Health
        api_healthy = await self.test_api_health()

        if not api_healthy:
            print("APIs not responding. Make sure backend is running on port 8000")
            return

        # Test 2: Client Onboarding
        client_id = await self.test_client_onboarding()

        # Test 3: Content Generation
        await self.test_content_generation()

        print("\n" + "="*40)
        print("TESTS COMPLETED!")
        print("\nNext steps:")
        print("1. Check backend logs for detailed results")
        print("2. Visit frontend at http://localhost:3001")
        print("3. Connect real social accounts via OAuth")
        print("4. Set environment variables for API access")


async def main():
    tester = SimpleTester()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())