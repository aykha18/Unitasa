from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.crm_integration import (
    CRMConnector, CRMConnection, CRMType, AuthMethod, 
    IntegrationStatus, ConnectionStatus
)
from app.core.crm_integration_framework import CRMIntegrationFramework

logger = logging.getLogger(__name__)

class CRMMarketplaceService:
    """Service for managing CRM integration marketplace"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_available_connectors(self, include_beta: bool = False) -> List[Dict[str, Any]]:
        """Get list of available CRM connectors"""
        query = self.db.query(CRMConnector)
        
        if not include_beta:
            query = query.filter(CRMConnector.status != IntegrationStatus.BETA)
            
        connectors = query.all()
        return [c.to_dict() for c in connectors]
        
    def get_connector_details(self, connector_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed info for a connector"""
        connector = self.db.query(CRMConnector).filter(CRMConnector.id == connector_id).first()
        if not connector:
            return None
        return connector.to_dict()

    async def create_demo_connection(self, crm_type: str, user_email: str) -> Dict[str, Any]:
        """Create a demo connection for testing"""
        # Find connector
        connector = self.db.query(CRMConnector).filter(CRMConnector.crm_type == crm_type).first()
        if not connector:
            # If NeuraCRM doesn't exist in DB, create it dynamically for simulation
            if crm_type == "neuracrm" or crm_type == CRMType.NEURACRM:
                connector = CRMConnector(
                    crm_type=CRMType.NEURACRM,
                    name="NeuraCRM",
                    display_name="NeuraCRM (Simulated)",
                    description="Internal simulated CRM for testing and development",
                    auth_method=AuthMethod.API_KEY,
                    status=IntegrationStatus.AVAILABLE,
                    base_url="https://api.neuracrm.com"
                )
                self.db.add(connector)
                self.db.commit()
            else:
                raise ValueError(f"CRM type {crm_type} not found")

        # Create connection
        connection = CRMConnection(
            connector_id=connector.id,
            connection_name=f"Demo {connector.display_name}",
            connection_status=ConnectionStatus.CONNECTED,
            auth_config={"api_key": "demo_key", "demo_mode": True},
            sync_config={"demo_mode": True},
            health_status="healthy",
            last_health_check_at=datetime.utcnow()
        )
        
        self.db.add(connection)
        self.db.commit()
        
        return {
            "success": True,
            "message": "Demo connection established",
            "connection_id": connection.id,
            "demo_data": {"contacts": 5, "companies": 2}
        }

    def get_integration_health_overview(self) -> Dict[str, Any]:
        """Get overview of integration health"""
        total_connections = self.db.query(CRMConnection).count()
        healthy_connections = self.db.query(CRMConnection).filter(CRMConnection.health_status == "healthy").count()
        
        return {
            "total_connections": total_connections,
            "healthy_connections": healthy_connections,
            "error_rate": 0 if total_connections == 0 else (total_connections - healthy_connections) / total_connections,
            "status": "operational"
        }

