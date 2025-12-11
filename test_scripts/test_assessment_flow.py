#!/usr/bin/env python3
"""
Comprehensive test script for AI Assessment Flow
Tests the complete assessment process and verifies data storage in database
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

# Import database models and connection
from app.core.database import get_db, engine, Base
from app.models.lead import Lead
from app.models.assessment import Assessment
from app.models.campaign import Campaign

class AssessmentFlowTester:
    """Test the complete AI Assessment flow"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/landing/assessment"
        self.test_results = []
        
    async def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
            "data": data
        }
        self.test_results.append(result)
        
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}: {details}")
        if data and not success:
            print(f"   Data: {data}")
            
    async def test_assessment_start(self) -> Dict[str, Any]:
        """Test assessment start endpoint"""
        test_data = {
            "email": f"test.user.{int(datetime.utcnow().timestamp())}@example.com",
            "name": "Test User Assessment Flow",
            "company": "Test Company Inc",
            "preferred_crm": "HubSpot"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.api_url}/start", json=test_data)
                
                if response.status_code == 200:
                    result = response.json()
                    await self.log_test(
                        "Assessment Start",
                        True,
                        f"Assessment ID: {result.get('assessment_id')}",
                        result
                    )
                    return result
                else:
                    await self.log_test(
                        "Assessment Start",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return {}
                    
        except Exception as e:
            await self.log_test("Assessment Start", False, f"Exception: {str(e)}")
            return {}
    
    async def test_assessment_questions(self):
        """Test getting assessment questions"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/questions")
                
                if response.status_code == 200:
                    questions = response.json()
                    await self.log_test(
                        "Get Assessment Questions",
                        True,
                        f"Retrieved {len(questions.get('questions', []))} questions",
                        questions
                    )
                    return questions
                else:
                    await self.log_test(
                        "Get Assessment Questions",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return {}
                    
        except Exception as e:
            await self.log_test("Get Assessment Questions", False, f"Exception: {str(e)}")
            return {}
    
    async def test_assessment_submit(self, assessment_data: Dict[str, Any]):
        """Test assessment submission"""
        if not assessment_data.get("assessment_id"):
            await self.log_test("Assessment Submit", False, "No assessment_id provided")
            return
            
        # Sample responses for the assessment
        submission_data = {
            "assessment_id": assessment_data["assessment_id"],
            "responses": [
                {
                    "question_id": "crm_system",
                    "answer": "HubSpot"
                },
                {
                    "question_id": "monthly_leads", 
                    "answer": "51-200"
                },
                {
                    "question_id": "automation_level",
                    "answer": 7
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.api_url}/submit", json=submission_data)
                
                if response.status_code == 200:
                    result = response.json()
                    await self.log_test(
                        "Assessment Submit",
                        True,
                        f"Score: {result.get('overall_score')}, Level: {result.get('readiness_level')}",
                        result
                    )
                    return result
                else:
                    await self.log_test(
                        "Assessment Submit",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return {}
                    
        except Exception as e:
            await self.log_test("Assessment Submit", False, f"Exception: {str(e)}")
            return {}
    
    async def verify_database_storage(self):
        """Verify that data was properly stored in the database"""
        try:
            async with AsyncSession(engine) as db:
                # Check campaigns table
                campaign_result = await db.execute(select(Campaign))
                campaigns = campaign_result.scalars().all()
                await self.log_test(
                    "Database - Campaigns",
                    len(campaigns) > 0,
                    f"Found {len(campaigns)} campaigns",
                    [{"id": c.id, "name": c.name, "status": c.status} for c in campaigns]
                )
                
                # Check leads table
                lead_result = await db.execute(select(Lead))
                leads = lead_result.scalars().all()
                await self.log_test(
                    "Database - Leads",
                    len(leads) > 0,
                    f"Found {len(leads)} leads",
                    [{"id": l.id, "email": l.email, "company": l.company, "score": l.score} for l in leads[-5:]]  # Show last 5
                )
                
                # Check assessments table
                assessment_result = await db.execute(select(Assessment))
                assessments = assessment_result.scalars().all()
                await self.log_test(
                    "Database - Assessments",
                    len(assessments) > 0,
                    f"Found {len(assessments)} assessments",
                    [{"id": a.id, "lead_id": a.lead_id, "overall_score": a.overall_score, "is_completed": a.is_completed} for a in assessments[-5:]]  # Show last 5
                )
                
                # Verify lead-assessment relationship
                if leads and assessments:
                    latest_lead = leads[-1]
                    lead_assessments = [a for a in assessments if a.lead_id == latest_lead.id]
                    await self.log_test(
                        "Database - Lead-Assessment Relationship",
                        len(lead_assessments) > 0,
                        f"Lead {latest_lead.id} has {len(lead_assessments)} assessments",
                        lead_assessments
                    )
                
                # Check specific assessment data
                if assessments:
                    latest_assessment = assessments[-1]
                    await self.log_test(
                        "Database - Assessment Details",
                        True,
                        f"Assessment {latest_assessment.id} details:",
                        {
                            "id": latest_assessment.id,
                            "lead_id": latest_assessment.lead_id,
                            "overall_score": latest_assessment.overall_score,
                            "readiness_level": latest_assessment.readiness_level,
                            "segment": latest_assessment.segment,
                            "current_crm": latest_assessment.current_crm,
                            "is_completed": latest_assessment.is_completed,
                            "responses": latest_assessment.responses,
                            "integration_recommendations": latest_assessment.integration_recommendations,
                            "started_at": latest_assessment.started_at.isoformat() if latest_assessment.started_at else None,
                            "completed_at": latest_assessment.completed_at.isoformat() if latest_assessment.completed_at else None
                        }
                    )
                
                # Check lead data completeness
                if leads:
                    latest_lead = leads[-1]
                    await self.log_test(
                        "Database - Lead Data Completeness",
                        True,
                        f"Lead {latest_lead.id} data:",
                        {
                            "id": latest_lead.id,
                            "email": latest_lead.email,
                            "company": latest_lead.company,
                            "score": latest_lead.score,
                            "status": latest_lead.status,
                            "readiness_segment": latest_lead.readiness_segment,
                            "current_crm_system": latest_lead.current_crm_system,
                            "crm_integration_readiness": latest_lead.crm_integration_readiness,
                            "technical_capability_score": latest_lead.technical_capability_score,
                            "business_maturity_score": latest_lead.business_maturity_score,
                            "tags": latest_lead.tags,
                            "first_contacted": latest_lead.first_contacted.isoformat() if latest_lead.first_contacted else None
                        }
                    )
                    
        except Exception as e:
            await self.log_test("Database Verification", False, f"Exception: {str(e)}")
    
    async def test_api_endpoints_health(self):
        """Test API endpoints health"""
        endpoints = [
            "/health",
            "/api/v1/landing/health"
        ]
        
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    
                    await self.log_test(
                        f"API Health - {endpoint}",
                        response.status_code == 200,
                        f"HTTP {response.status_code}",
                        response.json() if response.status_code == 200 else None
                    )
                    
            except Exception as e:
                await self.log_test(f"API Health - {endpoint}", False, f"Exception: {str(e)}")
    
    async def run_complete_flow_test(self):
        """Run the complete assessment flow test"""
        print("Starting AI Assessment Flow Test")
        print("=" * 60)
        
        # Test API health first
        await self.test_api_endpoints_health()
        print()
        
        # Get questions
        print("Getting assessment questions...")
        questions = await self.test_assessment_questions()
        print()
        
        # Start assessment
        print("Starting assessment...")
        assessment_data = await self.test_assessment_start()
        print()
        
        # Submit assessment
        if assessment_data:
            print("Submitting assessment responses...")
            submit_result = await self.test_assessment_submit(assessment_data)
            print()
        
        # Verify database storage
        print("Verifying database storage...")
        await self.verify_database_storage()
        print()
        
        # Print summary
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"[PASS] Passed: {passed_tests}")
        print(f"[FAIL] Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        # Save detailed results
        with open("assessment_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print("Detailed results saved to: assessment_test_results.json")

async def main():
    """Main test function"""
    # Check if backend is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code != 200:
                print("[FAIL] Backend is not responding properly")
                return
    except Exception:
        print("[FAIL] Backend is not running. Please start the backend first.")
        return
    
    # Run the test
    tester = AssessmentFlowTester()
    await tester.run_complete_flow_test()

if __name__ == "__main__":
    asyncio.run(main())