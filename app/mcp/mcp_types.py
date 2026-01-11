"""
MCP Types - Type definitions for Model Context Protocol
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class MCPTool(BaseModel):
    """Definition of an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, Any]
    agent_name: Optional[str] = None

class ToolCall(BaseModel):
    """Request to call a tool"""
    tool_name: str
    parameters: Dict[str, Any]
    call_id: str
    from_agent: Optional[str] = None
    to_agent: Optional[str] = None

class ToolResult(BaseModel):
    """Result of a tool call"""
    call_id: str
    result: Any
    error: Optional[str] = None
    success: bool
    metadata: Optional[Dict[str, Any]] = None
