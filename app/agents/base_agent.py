from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate

from app.agents.state import MarketingAgentState

logger = structlog.get_logger()

class BaseAgent:
    """Base class for all marketing AI agents using LangChain and LangGraph"""

    def __init__(self, name: str, llm: ChatOpenAI, tools: List[Tool] = None, memory=None):
        self.name = name
        self.llm = llm
        self.tools = tools or []
        self.memory = memory or ConversationBufferWindowMemory(k=10, return_messages=True)
        self.logger = logger.bind(agent=name)

        # Create agent executor
        # Note: We need a system prompt. The subclass should provide it, 
        # but we can't call abstract method in __init__ easily if it relies on instance state.
        # We'll initialize the agent lazily or expect get_system_prompt() to be ready.
        
        # However, create_openai_functions_agent requires the prompt immediately.
        # We will call self.get_system_prompt() here.
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.get_system_prompt()
        )

        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

    async def execute(self, state: MarketingAgentState) -> MarketingAgentState:
        """Execute agent task with state management"""
        try:
            self.logger.info("executing_agent_task", state_keys=list(state.keys()))
            
            # Build input from state
            input_data = self.build_input(state)
            
            # Execute agent
            # AgentExecutor expects a dict input. We usually pass {"input": ...} or similar based on the prompt.
            # The prompt usually has {input} and {agent_scratchpad}.
            # build_input should return a dict compatible with the prompt.
            
            # If input_data is just a string, we wrap it.
            if isinstance(input_data, str):
                input_data = {"input": input_data}
                
            result = await self.executor.ainvoke(input_data)

            # Update state
            return self.update_state(state, result)

        except Exception as e:
            self.logger.error("agent_execution_failed", error=str(e))
            return self.handle_error(state, e)

    def get_system_prompt(self) -> ChatPromptTemplate:
        """Get agent-specific system prompt"""
        raise NotImplementedError

    def build_input(self, state: MarketingAgentState) -> Dict[str, Any]:
        """Build input data from shared state"""
        raise NotImplementedError

    def update_state(self, state: MarketingAgentState, result: Dict[str, Any]) -> MarketingAgentState:
        """Update shared state with agent results"""
        raise NotImplementedError

    def handle_error(self, state: MarketingAgentState, error: Exception) -> MarketingAgentState:
        """Handle agent execution errors"""
        state["errors"] = state.get("errors", [])
        state["errors"].append({
            "agent": self.name,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat()
        })
        return state
