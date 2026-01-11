"""
Example demonstrating CRM integration through MCP
Shows how agents can use CRM tools for lead generation and management
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.agents.base_agent import BaseAgent
from app.agents.state import MarketingAgentState
from app.mcp.crm_client import CRMIntegrationMixin


class CRMAgent(BaseAgent, CRMIntegrationMixin):
    """Agent with CRM integration capabilities"""

    def __init__(self, llm: ChatOpenAI):
        # Initialize CRM mixin
        self.crm_organization_id = 8  # Default organization
        
        # Initialize BaseAgent
        # We don't have specific tools defined here yet, but we can add them if needed
        # For now, we'll pass an empty list or the CRM tools if we can wrap them
        super().__init__("crm_agent", llm, [])

    def get_system_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are a CRM Specialist Agent.
Your role is to analyze leads, identify opportunities, and manage CRM data.
You have access to CRM tools to fetch and update information.
"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def build_input(self, state: MarketingAgentState) -> Dict[str, Any]:
        return {
            "input": "Analyze CRM data"
        }

    def update_state(self, state: MarketingAgentState, result: Dict[str, Any]) -> MarketingAgentState:
        # Simple update for now
        return state

    async def analyze_lead_opportunities(self) -> Dict[str, Any]:
        """Analyze current leads and identify opportunities"""
        try:
            # Get dashboard data
            dashboard = await self.get_crm_dashboard(self.crm_organization_id)

            # Get recent leads
            recent_leads = await self.get_crm_leads(
                organization_id=self.crm_organization_id,
                limit=20
            )

            # Analyze lead quality and opportunities
            high_value_leads = [lead for lead in recent_leads if lead.get('score', 0) > 80]
            new_leads = [lead for lead in recent_leads if lead.get('status') == 'new']

            analysis = {
                "dashboard_summary": dashboard,
                "total_leads": len(recent_leads),
                "high_value_leads": len(high_value_leads),
                "new_leads": len(new_leads),
                "opportunities": []
            }

            # Identify opportunities
            for lead in high_value_leads[:5]:  # Top 5 high-value leads
                analysis["opportunities"].append({
                    "lead_id": lead["id"],
                    "title": lead["title"],
                    "contact": lead["contact_name"],
                    "score": lead["score"],
                    "recommendation": "High-priority follow-up needed"
                })

            return analysis

        except Exception as e:
            return {"error": f"Failed to analyze lead opportunities: {str(e)}"}

    async def generate_leads_from_opportunities(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate new leads based on identified opportunities"""
        results = {
            "generated_leads": [],
            "errors": []
        }

        for opp in opportunities:
            try:
                # Create a follow-up lead based on the opportunity
                lead_title = f"Follow-up: {opp['title']}"

                new_lead = await self.create_crm_lead(
                    title=lead_title,
                    contact_name=opp.get('contact'),
                    source="ai_generated",
                    organization_id=self.crm_organization_id
                )

                results["generated_leads"].append({
                    "original_opportunity": opp,
                    "new_lead": new_lead
                })

            except Exception as e:
                results["errors"].append({
                    "opportunity": opp,
                    "error": str(e)
                })

        return results

    async def sync_contacts_with_campaign(self, campaign_contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sync campaign contacts with CRM"""
        results = {
            "synced_contacts": [],
            "created_contacts": [],
            "errors": []
        }

        for contact_data in campaign_contacts:
            try:
                # Check if contact exists
                existing_contacts = await self.search_crm_contacts(
                    contact_data.get('email', ''),
                    organization_id=self.crm_organization_id,
                    limit=1
                )

                if existing_contacts:
                    # Contact exists, just record it
                    results["synced_contacts"].append(existing_contacts[0])
                else:
                    # Create new contact
                    new_contact = await self.create_crm_contact(
                        name=contact_data['name'],
                        email=contact_data.get('email'),
                        phone=contact_data.get('phone'),
                        company=contact_data.get('company'),
                        organization_id=self.crm_organization_id
                    )
                    results["created_contacts"].append(new_contact)

            except Exception as e:
                results["errors"].append({
                    "contact_data": contact_data,
                    "error": str(e)
                })

        return results

    async def create_deals_from_leads(self, lead_ids: List[int]) -> Dict[str, Any]:
        """Convert qualified leads to deals"""
        results = {
            "created_deals": [],
            "errors": []
        }

        for lead_id in lead_ids:
            try:
                # Get lead details
                leads = await self.get_crm_leads(
                    organization_id=self.crm_organization_id,
                    limit=1
                )
                lead = next((l for l in leads if l['id'] == lead_id), None)

                if not lead:
                    results["errors"].append({
                        "lead_id": lead_id,
                        "error": "Lead not found"
                    })
                    continue

                # Create deal from lead
                deal_title = f"Deal: {lead['title']}"
                estimated_value = 10000  # Default estimated value

                new_deal = await self.create_crm_deal(
                    title=deal_title,
                    value=estimated_value,
                    contact_id=lead.get('contact_id'),
                    stage_id=1,  # Prospect stage
                    organization_id=self.crm_organization_id,
                    description=f"Converted from lead: {lead['title']}"
                )

                results["created_deals"].append({
                    "lead": lead,
                    "deal": new_deal
                })

            except Exception as e:
                results["errors"].append({
                    "lead_id": lead_id,
                    "error": str(e)
                })

        return results


class LeadGenerationAgent(CRMAgent):
    """Specialized agent for lead generation with CRM integration"""

    def __init__(self):
        super().__init__("lead_gen_agent", "Lead Generation Agent")

    async def run_lead_generation_workflow(self) -> Dict[str, Any]:
        """Complete lead generation workflow with CRM integration"""
        workflow_results = {
            "step": "lead_generation_workflow",
            "timestamp": datetime.now().isoformat(),
            "results": {}
        }

        try:
            # Step 1: Analyze current opportunities
            print("Step 1: Analyzing lead opportunities...")
            opportunities = await self.analyze_lead_opportunities()
            workflow_results["results"]["opportunities_analysis"] = opportunities

            # Step 2: Generate follow-up leads
            if "opportunities" in opportunities and opportunities["opportunities"]:
                print("Step 2: Generating follow-up leads...")
                lead_generation = await self.generate_leads_from_opportunities(
                    opportunities["opportunities"]
                )
                workflow_results["results"]["lead_generation"] = lead_generation

            # Step 3: Sync with external campaign data (mock data for example)
            print("Step 3: Syncing campaign contacts...")
            mock_campaign_contacts = [
                {"name": "Alice Johnson", "email": "alice@techcorp.com", "company": "TechCorp"},
                {"name": "Bob Wilson", "email": "bob@innovate.com", "company": "Innovate Inc"},
                {"name": "Carol Davis", "email": "carol@startup.io", "company": "StartupIO"}
            ]

            contact_sync = await self.sync_contacts_with_campaign(mock_campaign_contacts)
            workflow_results["results"]["contact_sync"] = contact_sync

            # Step 4: Convert high-quality leads to deals
            if "generated_leads" in workflow_results["results"].get("lead_generation", {}):
                generated_leads = workflow_results["results"]["lead_generation"]["generated_leads"]
                if generated_leads:
                    print("Step 4: Converting leads to deals...")
                    lead_ids = [lead["new_lead"]["id"] for lead in generated_leads]
                    deal_conversion = await self.create_deals_from_leads(lead_ids)
                    workflow_results["results"]["deal_conversion"] = deal_conversion

            workflow_results["status"] = "completed"

        except Exception as e:
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)

        return workflow_results


async def demonstrate_crm_integration():
    """Demonstrate CRM integration capabilities"""
    print("🚀 Demonstrating CRM Integration through MCP")
    print("=" * 50)

    # Create CRM-integrated agent
    agent = LeadGenerationAgent()

    try:
        # Initialize the agent
        await agent.initialize()
        print("✓ Agent initialized")

        # Run the lead generation workflow
        print("\n📊 Running Lead Generation Workflow...")
        results = await agent.run_lead_generation_workflow()

        print("\n📈 Workflow Results:")
        print(json.dumps(results, indent=2, default=str))

        # Additional CRM operations
        print("\n🔍 Additional CRM Operations:")

        # Get dashboard
        dashboard = await agent.get_crm_dashboard()
        print(f"📊 Dashboard: {dashboard['metrics']['total_leads']} leads, {dashboard['metrics']['total_deals']} deals")

        # Search contacts
        contacts = await agent.search_crm_contacts("john", limit=3)
        print(f"👥 Found {len(contacts)} contacts matching 'john'")

        # Get recent deals
        deals = await agent.get_crm_deals(limit=3)
        print(f"💼 Recent deals: {len(deals)} found")

        print("\n✅ CRM Integration Demo Completed Successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await agent.cleanup()


async def test_crm_tools_individually():
    """Test individual CRM tools"""
    print("🧪 Testing Individual CRM Tools")
    print("=" * 30)

    agent = CRMAgent("test_agent", "Test Agent")

    try:
        await agent.initialize()

        # Test 1: Dashboard
        print("1. Testing Dashboard...")
        dashboard = await agent.get_crm_dashboard()
        print(f"   ✓ Dashboard loaded: {len(dashboard.get('metrics', {}))} metrics")

        # Test 2: Contact Search
        print("2. Testing Contact Search...")
        contacts = await agent.search_crm_contacts("test", limit=5)
        print(f"   ✓ Found {len(contacts)} contacts")

        # Test 3: Lead Creation
        print("3. Testing Lead Creation...")
        new_lead = await agent.create_crm_lead(
            title="Test Lead - MCP Integration",
            contact_name="Test User",
            contact_email="test@example.com",
            source="mcp_test"
        )
        print(f"   ✓ Created lead: {new_lead.get('title')}")

        # Test 4: Contact Creation
        print("4. Testing Contact Creation...")
        new_contact = await agent.create_crm_contact(
            name="MCP Test Contact",
            email="mcp.test@example.com",
            company="MCP Corp"
        )
        print(f"   ✓ Created contact: {new_contact.get('name')}")

        # Test 5: Deal Creation
        print("5. Testing Deal Creation...")
        new_deal = await agent.create_crm_deal(
            title="MCP Test Deal",
            value=5000.0,
            contact_id=new_contact.get('id'),
            description="Created via MCP integration test"
        )
        print(f"   ✓ Created deal: {new_deal.get('title')} (${new_deal.get('value')})")

        print("\n✅ All individual CRM tools tested successfully!")

    except Exception as e:
        print(f"❌ Individual tool test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await agent.cleanup()


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_crm_integration())

    print("\n" + "="*50)
    print("Running individual tool tests...")
    asyncio.run(test_crm_tools_individually())
