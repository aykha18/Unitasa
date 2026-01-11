from typing import Dict, Any, Literal
import structlog
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from app.agents.state import MarketingAgentState, create_initial_state
from app.agents.lead_generation import LeadGenerationAgent
from app.agents.content_creator import ContentCreatorAgent

logger = structlog.get_logger()

class MarketingOrchestrator:
    """
    Orchestrates the marketing agent workflow using LangGraph.
    Coordinated multiple agents to execute complex marketing campaigns.
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.lead_agent = LeadGenerationAgent(llm)
        self.content_agent = ContentCreatorAgent(llm)
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(MarketingAgentState)
        
        # Add agent nodes
        workflow.add_node("client_analysis", self.client_analysis_agent.execute)
        workflow.add_node("lead_generation", self.lead_agent.execute)
        workflow.add_node("content_creation", self.content_agent.execute)
        
        # Set entry point
        workflow.set_entry_point("client_analysis")

        # Add edges
        workflow.add_edge("client_analysis", "lead_generation")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "lead_generation",
            self._route_after_lead_gen,
            {
                "content_creation": "content_creation",
                "end": END
            }
        )
        
        # Add edges
        workflow.add_edge("content_creation", END)
        
        return workflow

    def _route_after_lead_gen(self, state: MarketingAgentState) -> Literal["content_creation", "end"]:
        """Determine next step after lead generation"""
        # If we have qualified leads, proceed to content creation
        if state.get("qualified_leads") and len(state["qualified_leads"]) > 0:
            logger.info("leads_found_proceeding_to_content", count=len(state["qualified_leads"]))
            return "content_creation"
            
        # Otherwise end campaign
        logger.info("no_qualified_leads_ending_campaign")
        return "end"

    async def run_campaign(self, campaign_config: Dict[str, Any]):
        """Run a full marketing campaign"""
        logger.info("starting_campaign", config=campaign_config)
        
        initial_state = create_initial_state(campaign_config)
        
        # Execute workflow
        # astream returns an async iterator of state updates
        final_state = initial_state
        async for output in self.app.astream(initial_state):
            for key, value in output.items():
                logger.info("workflow_step_completed", step=key)
                # In LangGraph, the output chunk IS the state update (or the full state depending on config)
                # But typically we want the final state.
                # We'll just track the last output.
                # Note: output[key] is the result of the node 'key'.
                # Since our nodes return the full state (updated), we can update final_state.
                if isinstance(value, dict):
                    final_state.update(value)
                    
        return final_state
