#!/usr/bin/env python3
"""
Test Script for Multi-Client Social Media Management System
Tests self-marketing and client onboarding workflows
"""

import asyncio
import json
import requests
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3001"

class SocialMediaSystemTester:
    """Test harness for the social media management system"""

    def __init__(self):
        self.session = requests.Session()

    async def test_self_marketing(self):
        """Test 1: Self-marketing - Unitasa promoting its own features"""
        print("\n" + "="*60)
        print("🧪 TEST 1: SELF-MARKETING (Unitasa Promoting Itself)")
        print("="*60)

        try:
            # Step 1: Generate content for Unitasa features
            print("\n📝 Step 1: Generating content for Unitasa features...")

            # Use the existing content generator to create posts
            features_to_promote = [
                "automated_social_posting",
                "ai_readiness_assessment",
                "crm_follow_ups"
            ]

            generated_content = []
            for feature in features_to_promote:
                print(f"  • Generating content for: {feature}")

                # In a real test, this would call the content generation API
                # For now, simulate the content generation
                content = await self.simulate_content_generation(feature, "twitter")
                generated_content.extend(content)

            print(f"  ✅ Generated {len(generated_content)} pieces of content")

        except Exception as e:
            print(f"❌ Self-marketing test failed: {e}")
            import traceback
            traceback.print_exc()
            return

            # Step 2: Post to social media (Twitter)
            print("\n📤 Step 2: Posting to social media...")

            # Check if Twitter account is connected
            accounts_response = self.session.get(f"{API_BASE_URL}/api/v1/social/accounts")
            if accounts_response.status_code == 200:
                accounts = accounts_response.json().get('accounts', [])
                twitter_accounts = [acc for acc in accounts if acc['platform'] == 'twitter']

                if twitter_accounts:
                    print(f"  ✅ Found {len(twitter_accounts)} connected Twitter account(s)")

                    # Post content to Twitter
                    for i, content_item in enumerate(generated_content[:2]):  # Post first 2 items
                        print(f"  📤 Posting content {i+1}/2...")

                        post_data = {
                            "content": content_item['content'],
                            "platforms": ["twitter"],
                            "scheduled_at": None,
                            "campaign_id": None
                        }

                        post_response = self.session.post(
                            f"{API_BASE_URL}/api/v1/social/posts",
                            json=post_data
                        )

                        if post_response.status_code == 200:
                            result = post_response.json()
                            print(f"    ✅ Posted successfully: {result['message']}")
                            for platform_result in result.get('results', []):
                                if platform_result['success']:
                                    print(f"       🔗 URL: {platform_result['url']}")
                        else:
                            print(f"    ❌ Post failed: {post_response.text}")

                else:
                    print("  ⚠️  No Twitter accounts connected. Setting up demo mode...")
                    await self.setup_demo_twitter_account()

            else:
                print(f"  ❌ Failed to check accounts: {accounts_response.status_code}")
                await self.setup_demo_twitter_account()

            print("\n🎉 Self-marketing test completed!")

        except Exception as e:
            print(f"❌ Self-marketing test failed: {e}")
            import traceback
            traceback.print_exc()

    async def test_client_onboarding(self):
        """Test 2: Client onboarding and content generation"""
        print("\n" + "="*60)
        print("🧪 TEST 2: CLIENT ONBOARDING & CONTENT GENERATION")
        print("="*60)

        try:
            # Step 1: Onboard a test client
            print("\n👥 Step 1: Onboarding test client...")

            test_client_data = {
                "company_info": {
                    "company_name": "TechFlow Solutions",
                    "brand_name": "TechFlow",
                    "industry": "SaaS",
                    "company_size": "Mid-Market (50-200 employees)",
                    "founding_year": 2018,
                    "headquarters": "San Francisco, CA",
                    "website": "https://techflow.com",
                    "mission_statement": "Empowering businesses with intelligent automation solutions",
                    "brand_voice": "professional"
                },
                "target_audience": {
                    "primary_persona": "IT Manager",
                    "secondary_personas": ["CTO", "VP of Engineering"],
                    "pain_points": [
                        "Manual processes slowing down development",
                        "Integration complexity between tools",
                        "Lack of visibility into system performance"
                    ],
                    "goals": [
                        "Streamline development workflows",
                        "Improve system reliability",
                        "Reduce operational overhead"
                    ],
                    "demographics": {
                        "age_range": "35-50",
                        "company_size": "Mid-Market",
                        "geography": ["United States", "Europe"]
                    }
                },
                "brand_assets": {
                    "logo_url": "https://techflow.com/logo.png",
                    "brand_colors": ["#0066CC", "#FFFFFF", "#333333"],
                    "brand_fonts": ["Inter", "Helvetica"],
                    "visual_style": "modern_minimalist",
                    "existing_content": [
                        "https://techflow.com/blog/automation-best-practices",
                        "https://techflow.com/case-studies/devops-transformation"
                    ]
                },
                "content_preferences": {
                    "key_messages": [
                        "Intelligent automation for modern development teams",
                        "Streamline workflows, boost productivity",
                        "Enterprise-grade reliability with developer-friendly tools"
                    ],
                    "competitors": ["Atlassian", "GitLab", "Jenkins"],
                    "unique_value_props": [
                        "AI-powered workflow optimization",
                        "Seamless third-party integrations",
                        "Real-time performance insights"
                    ],
                    "content_tone": "professional",
                    "taboo_topics": ["pricing comparisons", "negative competitor mentions"],
                    "required_mentions": ["AI-powered", "enterprise-grade", "developer-friendly"]
                },
                "social_media_accounts": {
                    "platforms": ["LinkedIn", "Twitter"],
                    "existing_handles": {
                        "LinkedIn": "@techflow-solutions",
                        "Twitter": "@techflow"
                    },
                    "posting_frequency": {
                        "LinkedIn": "3-5 posts/week",
                        "Twitter": "5-8 posts/week"
                    },
                    "peak_times": {
                        "LinkedIn": ["09:00", "14:00", "16:00"],
                        "Twitter": ["10:00", "15:00", "17:00"]
                    },
                    "competitor_handles": ["@atlassian", "@gitlab", "@jenkinsci"]
                },
                "performance_data": {
                    "current_metrics": {
                        "linkedin_followers": 2500,
                        "twitter_followers": 1800,
                        "website_traffic": 15000
                    },
                    "past_campaigns": [
                        {
                            "name": "DevOps Automation Launch",
                            "platform": "LinkedIn",
                            "reach": 12500,
                            "engagements": 450,
                            "conversions": 23
                        }
                    ],
                    "successful_content": [
                        "DevOps automation case study - 15% engagement rate",
                        "CI/CD pipeline optimization guide - 200 shares",
                        "Kubernetes integration tutorial - 300 saves"
                    ],
                    "failed_content": [
                        "Generic product updates - low engagement",
                        "Technical deep-dives without context - limited reach"
                    ]
                }
            }

            # Call the onboarding API
            onboarding_response = self.session.post(
                f"{API_BASE_URL}/api/v1/clients/onboard",
                json=test_client_data
            )

            if onboarding_response.status_code == 200:
                onboarding_result = onboarding_response.json()
                client_id = onboarding_result['client_id']
                print(f"  ✅ Client onboarded successfully!")
                print(f"     Client ID: {client_id}")
                print(f"     Knowledge Base: {'Ready' if onboarding_result['knowledge_base_ready'] else 'Pending'}")
                print(f"     Content Quality Score: {onboarding_result['estimated_content_quality']}/5.0")
                print(f"     Sample Content Generated: {onboarding_result['sample_content_generated']}")

                # Step 2: Generate client-specific content
                print("\n🎨 Step 2: Generating client-specific content...")
                await self.generate_client_content(client_id, "workflow_automation", "LinkedIn")

                # Step 3: Test client profile retrieval
                print("\n📊 Step 3: Retrieving client profile...")
                profile_response = self.session.get(
                    f"{API_BASE_URL}/api/v1/clients/{client_id}/profile"
                )

                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    print("  ✅ Client profile retrieved")
                    print(f"     Brand Voice: {profile['brand_profile']['brand_voice']}")
                    print(f"     Primary Persona: {profile['audience_profile']['primary_persona']['name']}")
                    print(f"     Content Pillars: {len(profile['content_strategy']['content_pillars'])}")
                    print(f"     Platform Strategy: {list(profile['platform_strategy']['platforms'].keys())}")
                else:
                    print(f"  ❌ Failed to retrieve profile: {profile_response.status_code}")

            else:
                print(f"  ❌ Client onboarding failed: {onboarding_response.status_code}")
                print(f"     Error: {onboarding_response.text}")

            print("\n🎉 Client onboarding test completed!")

        except Exception as e:
            print(f"❌ Client onboarding test failed: {e}")
            import traceback
            traceback.print_exc()

    async def generate_client_content(self, client_id: str, topic: str, platform: str):
        """Generate content for a specific client"""
        try:
            # This would call the client-adaptive content generator
            # For now, simulate the process
            print(f"  • Generating content for topic '{topic}' on {platform}...")

            # Simulate content generation with client-specific adaptation
            simulated_content = [
                {
                    "platform": platform,
                    "content_type": "educational",
                    "content": f"🚀 How TechFlow Solutions is revolutionizing {topic} with AI-powered automation. Learn how we're helping development teams streamline their workflows and boost productivity. #DevOps #Automation",
                    "hashtags": ["#DevOps", "#Automation", "#TechFlow"],
                    "engagement_prediction": "High"
                },
                {
                    "platform": platform,
                    "content_type": "thought_leadership",
                    "content": f"💡 The future of development: AI-driven {topic} that adapts to your team's needs. At TechFlow, we're building intelligent solutions that understand context and deliver results. What's your biggest workflow challenge? #FutureOfWork #AI",
                    "hashtags": ["#FutureOfWork", "#AI", "#DevOps"],
                    "engagement_prediction": "Medium-High"
                }
            ]

            print(f"    ✅ Generated {len(simulated_content)} pieces of client-adapted content")
            for i, content in enumerate(simulated_content, 1):
                print(f"       {i}. {content['content'][:80]}...")

            return simulated_content

        except Exception as e:
            print(f"    ❌ Content generation failed: {e}")
            return []

    async def setup_demo_twitter_account(self):
        """Setup a demo Twitter account for testing"""
        print("  🔧 Setting up demo Twitter account...")

        # In a real scenario, this would guide through OAuth
        # For demo purposes, we'll simulate having an account
        print("    📝 Demo Mode: Simulating Twitter account connection")
        print("    🔗 In production, visit: http://localhost:3001/social")
        print("    🏷️  Then connect your Twitter account via OAuth")

        # Simulate posting in demo mode
        demo_content = "🚀 AI agents that run your marketing for you! Transform your marketing automation with Unitasa. #MarketingAutomation #AI"

        print(f"    📤 Demo post: {demo_content}")
        print("    ✅ Demo post 'successful' (simulated)")

    async def simulate_content_generation(self, feature: str, platform: str):
        """Simulate content generation for testing"""
        # This simulates what the content generator would produce
        feature_content = {
            "automated_social_posting": {
                "content": "🚀 Tired of manual social media posting? Our AI agents handle scheduling, posting, and optimization across X, LinkedIn, Instagram & more. Save 15+ hours/week! #MarketingAutomation #AI",
                "hashtags": ["#MarketingAutomation", "#AI", "#SocialMedia"],
                "type": "benefit_focused"
            },
            "ai_readiness_assessment": {
                "content": "🧠 Ready for AI marketing? Take our 30-second assessment and get a personalized automation roadmap. No commitment required! #AI #MarketingStrategy",
                "hashtags": ["#AI", "#MarketingStrategy", "#Automation"],
                "type": "call_to_action"
            },
            "crm_follow_ups": {
                "content": "💼 Transform your lead nurturing with AI-powered CRM follow-ups. Never miss a sales opportunity again! #CRM #LeadGeneration #SalesAutomation",
                "hashtags": ["#CRM", "#LeadGeneration", "#SalesAutomation"],
                "type": "benefit_focused"
            }
        }

        content_data = feature_content.get(feature, {
            "content": f"🚀 Discover how Unitasa's {feature.replace('_', ' ')} can transform your marketing! #Unitasa #AI",
            "hashtags": ["#Unitasa", "#AI", "#Marketing"],
            "type": "educational"
        })

        return [{
            "feature": feature,
            "platform": platform,
            "content": content_data["content"],
            "hashtags": content_data["hashtags"],
            "type": content_data["type"],
            "generated_at": datetime.utcnow().isoformat()
        }]

    async def run_all_tests(self):
        """Run all system tests"""
        print("🎯 STARTING MULTI-CLIENT SOCIAL MEDIA SYSTEM TESTS")
        print("="*60)
        print(f"📅 Test Time: {datetime.utcnow().isoformat()}")
        print(f"🌐 API Base URL: {API_BASE_URL}")
        print(f"🖥️  Frontend URL: {FRONTEND_URL}")

        # Test 1: Self-marketing
        await self.test_self_marketing()

        # Test 2: Client onboarding
        await self.test_client_onboarding()

        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETED!")
        print("="*60)
        print("\n📋 NEXT STEPS:")
        print("1. 🔗 Visit http://localhost:3001/social to connect real social accounts")
        print("2. 📊 Check analytics at http://localhost:3001/analytics")
        print("3. 👥 Onboard more clients via the API")
        print("4. 🤖 Monitor automated posting performance")
        print("\n💡 TIP: Set environment variables for real API access:")
        print("   TWITTER_CLIENT_ID=your_twitter_client_id")
        print("   TWITTER_CLIENT_SECRET=your_twitter_client_secret")


async def main():
    """Main test runner"""
    tester = SocialMediaSystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # Configure logging
    import logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    asyncio.run(main())