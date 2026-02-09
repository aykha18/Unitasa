"""
CRM Integration Framework - Core system for managing CRM integrations
Extends existing MCP system for CRM-specific functionality
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import httpx
from sqlalchemy.orm import Session

from app.models.crm_integration import (
    CRMConnector, CRMConnection, CRMSyncLog, CRMFieldMapping,
    CRMType, AuthMethod, ConnectionStatus, SyncStatus
)
from app.mcp.client import AgentMCPClient
from app.mcp.mcp_types import MCPTool, ToolCall, ToolResult
from app.core.database import get_db

logger = logging.getLogger(__name__)


class CRMAuthConfig:
    """Configuration for CRM authentication"""
    
    def __init__(self, auth_method: AuthMethod, config: Dict[str, Any]):
        self.auth_method = auth_method
        self.config = config
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_method == AuthMethod.API_KEY:
            return {"Authorization": f"Bearer {self.config.get('api_key')}"}
        elif self.auth_method == AuthMethod.OAUTH2:
            return {"Authorization": f"Bearer {self.config.get('access_token')}"}
        elif self.auth_method == AuthMethod.BASIC_AUTH:
            import base64
            credentials = f"{self.config.get('username')}:{self.config.get('password')}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        return {}


class CRMObjectMapping:
    """Standard object mapping for CRM integrations"""
    
    CONTACT_FIELDS = {
        "id": "id",
        "first_name": "first_name", 
        "last_name": "last_name",
        "email": "email",
        "phone": "phone",
        "company": "company",
        "job_title": "job_title",
        "created_at": "created_at",
        "updated_at": "updated_at"
    }
    
    COMPANY_FIELDS = {
        "id": "id",
        "name": "name",
        "website": "website",
        "industry": "industry",
        "size": "company_size",
        "revenue": "revenue",
        "location": "location",
        "created_at": "created_at",
        "updated_at": "updated_at"
    }
    
    DEAL_FIELDS = {
        "id": "id",
        "title": "title",
        "value": "value",
        "stage": "stage",
        "status": "status",
        "contact_id": "contact_id",
        "company_id": "company_id",
        "owner_id": "owner_id",
        "created_at": "created_at",
        "updated_at": "updated_at"
    }
    
    ACTIVITY_FIELDS = {
        "id": "id",
        "type": "type",
        "subject": "subject",
        "description": "description",
        "contact_id": "contact_id",
        "deal_id": "deal_id",
        "due_date": "due_date",
        "completed": "completed",
        "created_at": "created_at",
        "updated_at": "updated_at"
    }


class BaseCRMAdapter(ABC):
    """Base class for CRM adapters"""
    
    def __init__(self, connection: CRMConnection):
        self.connection = connection
        self.connector = connection.connector
        self.auth_config = CRMAuthConfig(
            self.connector.auth_method,
            connection.auth_config
        )
        self.client = httpx.AsyncClient(
            base_url=self.connector.base_url,
            headers=self.auth_config.get_headers(),
            timeout=30.0
        )
    
    @abstractmethod
    async def test_connection(self) -> Tuple[bool, str]:
        """Test the CRM connection"""
        pass
    
    @abstractmethod
    async def get_contacts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get contacts from CRM"""
        pass
    
    @abstractmethod
    async def get_companies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get companies from CRM"""
        pass
    
    @abstractmethod
    async def get_deals(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get deals from CRM"""
        pass
    
    @abstractmethod
    async def get_activities(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get activities from CRM"""
        pass
    
    @abstractmethod
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a contact in CRM"""
        pass
    
    @abstractmethod
    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a company in CRM"""
        pass
    
    @abstractmethod
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deal in CRM"""
        pass
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class PipedriveAdapter(BaseCRMAdapter):
    """Pipedrive CRM adapter"""
    
    async def test_connection(self) -> Tuple[bool, str]:
        """Test Pipedrive connection"""
        try:
            response = await self.client.get("/v1/users/me")
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    async def get_contacts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get contacts from Pipedrive"""
        try:
            response = await self.client.get(
                "/v1/persons",
                params={"limit": limit, "start": offset}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Pipedrive contacts: {e}")
            return []
    
    async def get_companies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get companies from Pipedrive"""
        try:
            response = await self.client.get(
                "/v1/organizations",
                params={"limit": limit, "start": offset}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Pipedrive companies: {e}")
            return []
    
    async def get_deals(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get deals from Pipedrive"""
        try:
            response = await self.client.get(
                "/v1/deals",
                params={"limit": limit, "start": offset}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Pipedrive deals: {e}")
            return []
    
    async def get_activities(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get activities from Pipedrive"""
        try:
            response = await self.client.get(
                "/v1/activities",
                params={"limit": limit, "start": offset}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get Pipedrive activities: {e}")
            return []
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in Pipedrive"""
        try:
            response = await self.client.post("/v1/persons", json=contact_data)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {})
        except Exception as e:
            logger.error(f"Failed to create Pipedrive contact: {e}")
            raise
    
    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in Pipedrive"""
        try:
            response = await self.client.post("/v1/organizations", json=company_data)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {})
        except Exception as e:
            logger.error(f"Failed to create Pipedrive company: {e}")
            raise
    
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal in Pipedrive"""
        try:
            response = await self.client.post("/v1/deals", json=deal_data)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {})
        except Exception as e:
            logger.error(f"Failed to create Pipedrive deal: {e}")
            raise


class HubSpotAdapter(BaseCRMAdapter):
    """HubSpot CRM adapter"""
    
    async def test_connection(self) -> Tuple[bool, str]:
        """Test HubSpot connection"""
        try:
            response = await self.client.get("/crm/v3/objects/contacts", params={"limit": 1})
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    async def get_contacts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get contacts from HubSpot"""
        try:
            response = await self.client.get(
                "/crm/v3/objects/contacts",
                params={"limit": limit, "after": offset}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Failed to get HubSpot contacts: {e}")
            return []
    
    async def get_companies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get companies from HubSpot"""
        try:
            response = await self.client.get(
                "/crm/v3/objects/companies",
                params={"limit": limit, "after": offset}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Failed to get HubSpot companies: {e}")
            return []
    
    async def get_deals(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get deals from HubSpot"""
        try:
            response = await self.client.get(
                "/crm/v3/objects/deals",
                params={"limit": limit, "after": offset}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Failed to get HubSpot deals: {e}")
            return []
    
    async def get_activities(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get activities from HubSpot"""
        try:
            response = await self.client.get(
                "/crm/v3/objects/tasks",
                params={"limit": limit, "after": offset}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Failed to get HubSpot activities: {e}")
            return []
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in HubSpot"""
        try:
            payload = {"properties": contact_data}
            response = await self.client.post("/crm/v3/objects/contacts", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create HubSpot contact: {e}")
            raise
    
    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in HubSpot"""
        try:
            payload = {"properties": company_data}
            response = await self.client.post("/crm/v3/objects/companies", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create HubSpot company: {e}")
            raise
    
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal in HubSpot"""
        try:
            payload = {"properties": deal_data}
            response = await self.client.post("/crm/v3/objects/deals", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create HubSpot deal: {e}")
            raise


class NeuraCRMAdapter(BaseCRMAdapter):
    """
    NeuraCRM adapter - Internal/Simulated CRM for testing and default usage.
    This adapter mocks CRM operations to allow testing without external credentials.
    """
    
    async def test_connection(self) -> Tuple[bool, str]:
        """Test NeuraCRM connection (Always success for simulation)"""
        return True, "NeuraCRM connection successful (Simulated)"
    
    async def get_contacts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get simulated contacts"""
        return [
            {
                "id": "nc_101",
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice.smith@example.com",
                "company": "Tech Corp",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "nc_102",
                "first_name": "Bob",
                "last_name": "Jones",
                "email": "bob.jones@example.com",
                "company": "Innovation Inc",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def get_companies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get simulated companies"""
        return [
            {
                "id": "nc_co_1",
                "name": "Tech Corp",
                "industry": "Software",
                "revenue": 1000000,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "nc_co_2",
                "name": "Innovation Inc",
                "industry": "Manufacturing",
                "revenue": 5000000,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def get_deals(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get simulated deals"""
        return [
            {
                "id": "nc_dl_1",
                "title": "Enterprise License Deal",
                "value": 50000,
                "status": "negotiation",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "nc_dl_2",
                "title": "Startup Package",
                "value": 5000,
                "status": "closed_won",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def get_activities(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get simulated activities"""
        return [
            {
                "id": "nc_act_1",
                "type": "call",
                "subject": "Intro Call",
                "completed": True,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate creating contact"""
        return {**contact_data, "id": f"nc_{int(datetime.utcnow().timestamp())}"}
    
    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate creating company"""
        return {**company_data, "id": f"nc_co_{int(datetime.utcnow().timestamp())}"}
    
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate creating deal"""
        return {**deal_data, "id": f"nc_dl_{int(datetime.utcnow().timestamp())}"}


class CRMIntegrationFramework:
    """Main CRM Integration Framework"""
    
    def __init__(self, db: Session):
        self.db = db
        self.adapters = {
            CRMType.PIPEDRIVE: PipedriveAdapter,
            CRMType.HUBSPOT: HubSpotAdapter,
            CRMType.NEURACRM: NeuraCRMAdapter,  # Internal/Simulated CRM
            # Add more adapters as needed
        }
        self.mcp_client = None
    
    async def initialize_mcp_client(self):
        """Initialize MCP client for CRM integrations"""
        if not self.mcp_client:
            self.mcp_client = AgentMCPClient("crm_integration_framework")
            await self.mcp_client.discover_tools()
    
    def get_adapter(self, connection: CRMConnection) -> BaseCRMAdapter:
        """Get appropriate adapter for CRM connection"""
        adapter_class = self.adapters.get(connection.connector.crm_type)
        if not adapter_class:
            raise ValueError(f"No adapter available for CRM type: {connection.connector.crm_type}")
        return adapter_class(connection)
    
    async def test_connection(self, connection_id: int) -> Tuple[bool, str]:
        """Test a CRM connection"""
        connection = self.db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
        if not connection:
            return False, "Connection not found"
        
        adapter = self.get_adapter(connection)
        try:
            success, message = await adapter.test_connection()
            
            # Update connection health
            if success:
                connection.update_health_status("healthy")
                connection.connection_status = ConnectionStatus.CONNECTED
            else:
                connection.update_health_status("error", message)
                connection.connection_status = ConnectionStatus.ERROR
            
            self.db.commit()
            return success, message
        finally:
            await adapter.close()
    
    async def sync_objects(self, connection_id: int, object_type: str, 
                          sync_direction: str = "import") -> Dict[str, Any]:
        """Sync objects from/to CRM"""
        connection = self.db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
        if not connection:
            raise ValueError("Connection not found")
        
        # Create sync log
        sync_log = CRMSyncLog(
            connection_id=connection_id,
            sync_type="manual",
            sync_direction=sync_direction,
            object_type=object_type,
            status=SyncStatus.IN_PROGRESS,
            started_at=datetime.utcnow()
        )
        self.db.add(sync_log)
        self.db.commit()
        
        adapter = self.get_adapter(connection)
        try:
            if object_type == "contacts":
                objects = await adapter.get_contacts()
            elif object_type == "companies":
                objects = await adapter.get_companies()
            elif object_type == "deals":
                objects = await adapter.get_deals()
            elif object_type == "activities":
                objects = await adapter.get_activities()
            else:
                raise ValueError(f"Unsupported object type: {object_type}")
            
            # Update sync log
            sync_log.records_processed = len(objects)
            sync_log.mark_completed(SyncStatus.SUCCESS)
            
            # Update connection stats
            connection.record_sync_attempt(True, len(objects))
            
            self.db.commit()
            
            return {
                "success": True,
                "objects": objects,
                "count": len(objects),
                "sync_log_id": sync_log.id
            }
            
        except Exception as e:
            sync_log.mark_completed(SyncStatus.FAILED, str(e))
            connection.record_sync_attempt(False, 0, str(e))
            self.db.commit()
            raise
        finally:
            await adapter.close()
    
    async def create_object(self, connection_id: int, object_type: str, 
                           object_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create object in CRM"""
        connection = self.db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
        if not connection:
            raise ValueError("Connection not found")
        
        adapter = self.get_adapter(connection)
        try:
            if object_type == "contact":
                result = await adapter.create_contact(object_data)
            elif object_type == "company":
                result = await adapter.create_company(object_data)
            elif object_type == "deal":
                result = await adapter.create_deal(object_data)
            else:
                raise ValueError(f"Unsupported object type: {object_type}")
            
            return {"success": True, "object": result}
            
        finally:
            await adapter.close()
    
    def get_connection_health(self, connection_id: int) -> Dict[str, Any]:
        """Get connection health status"""
        connection = self.db.query(CRMConnection).filter(CRMConnection.id == connection_id).first()
        if not connection:
            raise ValueError("Connection not found")
        
        return {
            "connection_id": connection_id,
            "status": connection.connection_status.value,
            "health_status": connection.health_status,
            "is_healthy": connection.is_healthy(),
            "last_sync_at": connection.last_sync_at,
            "last_health_check_at": connection.last_health_check_at,
            "error_count": connection.error_count,
            "last_error": connection.last_error,
            "sync_success_rate": connection.get_sync_success_rate(),
            "total_syncs": connection.total_syncs,
            "records_synced": connection.records_synced
        }
    
    def get_sync_history(self, connection_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get sync history for connection"""
        sync_logs = self.db.query(CRMSyncLog).filter(
            CRMSyncLog.connection_id == connection_id
        ).order_by(CRMSyncLog.created_at.desc()).limit(limit).all()
        
        return [log.to_dict() for log in sync_logs]


# MCP Tools for CRM Integration
async def register_crm_integration_tools():
    """Register CRM integration tools with MCP system"""
    from app.mcp.tools import get_tool_registry
    
    registry = await get_tool_registry()
    
    # Test CRM Connection tool
    test_connection_tool = MCPTool(
        name="test_crm_connection",
        description="Test a CRM connection to verify it's working",
        parameters={
            "type": "object",
            "properties": {
                "connection_id": {"type": "integer", "description": "CRM connection ID"}
            },
            "required": ["connection_id"]
        },
        agent_name="crm_integration_framework"
    )
    
    # Sync CRM Objects tool
    sync_objects_tool = MCPTool(
        name="sync_crm_objects",
        description="Sync objects from CRM (contacts, companies, deals, activities)",
        parameters={
            "type": "object",
            "properties": {
                "connection_id": {"type": "integer", "description": "CRM connection ID"},
                "object_type": {"type": "string", "enum": ["contacts", "companies", "deals", "activities"]},
                "sync_direction": {"type": "string", "enum": ["import", "export"], "default": "import"}
            },
            "required": ["connection_id", "object_type"]
        },
        agent_name="crm_integration_framework"
    )
    
    # Create CRM Object tool
    create_object_tool = MCPTool(
        name="create_crm_object",
        description="Create an object in CRM (contact, company, deal)",
        parameters={
            "type": "object",
            "properties": {
                "connection_id": {"type": "integer", "description": "CRM connection ID"},
                "object_type": {"type": "string", "enum": ["contact", "company", "deal"]},
                "object_data": {"type": "object", "description": "Object data to create"}
            },
            "required": ["connection_id", "object_type", "object_data"]
        },
        agent_name="crm_integration_framework"
    )
    
    # Get Connection Health tool
    get_health_tool = MCPTool(
        name="get_crm_connection_health",
        description="Get health status and metrics for a CRM connection",
        parameters={
            "type": "object",
            "properties": {
                "connection_id": {"type": "integer", "description": "CRM connection ID"}
            },
            "required": ["connection_id"]
        },
        agent_name="crm_integration_framework"
    )
    
    # Register tools
    await registry.register_tool(test_connection_tool)
    await registry.register_tool(sync_objects_tool)
    await registry.register_tool(create_object_tool)
    await registry.register_tool(get_health_tool)
    
    logger.info("Registered CRM integration tools with MCP system")
