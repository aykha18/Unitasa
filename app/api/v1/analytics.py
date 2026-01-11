"""
Analytics API endpoints for landing page and CRM integration tracking
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.analytics_service import AnalyticsService
from app.core.lead_nurturing_integration import LeadNurturingIntegration
from app.core.dashboard_service import DashboardService
from app.core.landing_page_monitoring import LandingPageMonitor
from app.models.lead import Lead
from app.models.campaign import Campaign
from app.core.metrics import measure_api_request

router = APIRouter(tags=["analytics"])


@router.get("/landing-page-metrics")
@measure_api_request("GET", "/analytics/landing-page-metrics")
async def get_landing_page_metrics(
    time_range_hours: int = Query(24, ge=1, le=8760, description="Time range in hours (1 hour to 1 year)"),
    campaign_id: Optional[int] = Query(None, description="Optional campaign ID to filter metrics"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive landing page metrics"""
    try:
        analytics = AnalyticsService(db)
        metrics = await analytics.get_landing_page_metrics(
            time_range_hours=time_range_hours,
            campaign_id=campaign_id
        )
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get landing page metrics: {str(e)}")


@router.get("/crm-integration-analytics")
@measure_api_request("GET", "/analytics/crm-integration-analytics")
async def get_crm_integration_analytics(
    time_range_hours: int = Query(24, ge=1, le=8760, description="Time range in hours"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get CRM integration engagement analytics"""
    try:
        analytics = AnalyticsService(db)
        analytics_data = await analytics.get_crm_integration_analytics(time_range_hours)
        return {
            "success": True,
            "data": analytics_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get CRM integration analytics: {str(e)}")


@router.get("/conversion-funnel")
@measure_api_request("GET", "/analytics/conversion-funnel")
async def get_conversion_funnel_analysis(
    time_range_hours: int = Query(24, ge=1, le=8760, description="Time range in hours"),
    campaign_id: Optional[int] = Query(None, description="Optional campaign ID to filter analysis"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get conversion funnel analysis with integration focus"""
    try:
        analytics = AnalyticsService(db)
        funnel_data = await analytics.get_conversion_funnel_analysis(
            time_range_hours=time_range_hours,
            campaign_id=campaign_id
        )
        return {
            "success": True,
            "data": funnel_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversion funnel analysis: {str(e)}")


@router.get("/weekly-report")
@measure_api_request("GET", "/analytics/weekly-report")
async def get_weekly_metrics_report(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate comprehensive weekly metrics report"""
    try:
        analytics = AnalyticsService(db)
        report = await analytics.get_weekly_metrics_report()
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weekly report: {str(e)}")


@router.get("/campaign/{campaign_id}/performance")
@measure_api_request("GET", "/analytics/campaign/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: int,
    time_range_hours: int = Query(24, ge=1, le=8760, description="Time range in hours"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get performance metrics for a specific campaign"""
    try:
        # Verify campaign exists
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        analytics = AnalyticsService(db)
        
        # Get campaign-specific metrics
        landing_metrics = await analytics.get_landing_page_metrics(
            time_range_hours=time_range_hours,
            campaign_id=campaign_id
        )
        
        funnel_analysis = await analytics.get_conversion_funnel_analysis(
            time_range_hours=time_range_hours,
            campaign_id=campaign_id
        )
        
        # Get campaign performance summary
        performance_summary = campaign.get_landing_page_performance_summary()
        
        return {
            "success": True,
            "data": {
                "campaign_info": {
                    "id": campaign.id,
                    "name": campaign.name,
                    "type": campaign.campaign_type,
                    "status": campaign.status,
                    "created_at": campaign.created_at.isoformat(),
                    "landing_page_url": campaign.landing_page_url,
                    "crm_focus": campaign.crm_integration_focus
                },
                "landing_page_metrics": landing_metrics,
                "conversion_funnel": funnel_analysis,
                "performance_summary": performance_summary,
                "targets_met": campaign.is_meeting_targets()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign performance: {str(e)}")


@router.post("/campaign/{campaign_id}/update-metrics")
@measure_api_request("POST", "/analytics/campaign/{campaign_id}/update-metrics")
async def update_campaign_metrics(
    campaign_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update campaign metrics with latest data"""
    try:
        # Verify campaign exists
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        analytics = AnalyticsService(db)
        success = await analytics.update_campaign_metrics(campaign_id)
        
        if success:
            return {
                "success": True,
                "message": f"Campaign {campaign_id} metrics updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update campaign metrics")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update campaign metrics: {str(e)}")


@router.get("/lead/{lead_id}/journey")
@measure_api_request("GET", "/analytics/lead/{lead_id}/journey")
async def get_lead_journey(
    lead_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed journey analytics for a specific lead"""
    try:
        # Verify lead exists
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get lead's events
        from app.models.event import Event
        events = db.query(Event).filter(
            Event.properties['lead_id'].astext == str(lead_id)
        ).order_by(Event.timestamp.asc()).all()
        
        # Get lead's assessments
        assessments = lead.assessments
        
        # Build journey timeline
        journey_events = []
        
        for event in events:
            journey_events.append({
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "event_name": event.event_name,
                "properties": event.properties,
                "context": event.context
            })
        
        # Add assessment milestones
        for assessment in assessments:
            journey_events.append({
                "timestamp": assessment.created_at.isoformat(),
                "event_type": "assessment",
                "event_name": "assessment_started",
                "properties": {
                    "assessment_id": assessment.id,
                    "assessment_type": assessment.assessment_type
                }
            })
            
            if assessment.completed_at:
                journey_events.append({
                    "timestamp": assessment.completed_at.isoformat(),
                    "event_type": "assessment",
                    "event_name": "assessment_completed",
                    "properties": {
                        "assessment_id": assessment.id,
                        "overall_score": assessment.overall_score,
                        "readiness_level": assessment.readiness_level,
                        "segment": assessment.segment
                    }
                })
        
        # Sort by timestamp
        journey_events.sort(key=lambda x: x["timestamp"])
        
        return {
            "success": True,
            "data": {
                "lead_info": {
                    "id": lead.id,
                    "name": lead.full_name,
                    "email": lead.email,
                    "company": lead.company,
                    "created_at": lead.created_at.isoformat(),
                    "current_segment": lead.readiness_segment,
                    "crm_readiness": lead.crm_integration_readiness,
                    "preferred_crm": lead.preferred_crm
                },
                "journey_timeline": journey_events,
                "summary": {
                    "total_events": len(journey_events),
                    "assessments_completed": len([a for a in assessments if a.is_completed]),
                    "current_stage": lead.readiness_segment,
                    "engagement_level": "high" if len(journey_events) > 10 else "medium" if len(journey_events) > 5 else "low"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lead journey: {str(e)}")


@router.get("/dashboard")
@measure_api_request("GET", "/analytics/dashboard")
async def get_analytics_dashboard(
    time_range_hours: int = Query(24, ge=1, le=8760, description="Time range in hours"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive real-time dashboard data for landing page analytics"""
    try:
        dashboard_service = DashboardService(db)
        dashboard_data = await dashboard_service.get_real_time_dashboard(time_range_hours)
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.get("/dashboard/summary")
@measure_api_request("GET", "/analytics/dashboard/summary")
async def get_dashboard_summary(
    time_range_hours: int = Query(24, ge=1, le=8760, description="Time range in hours"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get concise dashboard summary for quick overview"""
    try:
        dashboard_service = DashboardService(db)
        summary = await dashboard_service.get_performance_summary(time_range_hours)
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")


@router.post("/track-event")
@measure_api_request("POST", "/analytics/track-event")
async def track_custom_event(
    event_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Track a custom analytics event"""
    try:
        analytics = AnalyticsService(db)
        
        event_type = event_data.get("event_type")
        lead_id = event_data.get("lead_id")
        
        if not event_type or not lead_id:
            raise HTTPException(status_code=400, detail="event_type and lead_id are required")
        
        # Route to appropriate tracking method
        success = False
        
        if event_type == "lead_capture":
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                success = await analytics.track_lead_capture(
                    lead=lead,
                    source=event_data.get("source", "landing_page"),
                    campaign_id=event_data.get("campaign_id")
                )
        
        elif event_type == "crm_integration_engagement":
            success = await analytics.track_crm_integration_engagement(
                lead_id=lead_id,
                crm_type=event_data.get("crm_type", "unknown"),
                engagement_type=event_data.get("engagement_type", "unknown"),
                **{k: v for k, v in event_data.items() if k not in ["event_type", "lead_id", "crm_type", "engagement_type"]}
            )
        
        elif event_type == "conversion":
            success = await analytics.track_conversion_event(
                lead_id=lead_id,
                conversion_type=event_data.get("conversion_type", "unknown"),
                value=event_data.get("value"),
                **{k: v for k, v in event_data.items() if k not in ["event_type", "lead_id", "conversion_type", "value"]}
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported event_type: {event_type}")
        
        if success:
            return {
                "success": True,
                "message": "Event tracked successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to track event")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track custom event: {str(e)}")


@router.post("/reports/generate")
@measure_api_request("POST", "/analytics/reports/generate")
async def generate_report(
    report_type: str = Query(..., description="Report type: daily or weekly"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate and return a comprehensive report"""
    try:
        from app.core.metrics_collector import generate_report_now
        
        if report_type not in ["daily", "weekly"]:
            raise HTTPException(status_code=400, detail="Report type must be 'daily' or 'weekly'")
        
        report = await generate_report_now(report_type)
        
        if report:
            return {
                "success": True,
                "data": report,
                "message": f"{report_type.title()} report generated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to generate {report_type} report")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.post("/metrics/collect")
@measure_api_request("POST", "/analytics/metrics/collect")
async def collect_metrics_manually(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger metrics collection"""
    try:
        from app.core.metrics_collector import collect_metrics_now
        
        await collect_metrics_now()
        
        return {
            "success": True,
            "message": "Metrics collection completed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect metrics: {str(e)}")


@router.get("/health")
@measure_api_request("GET", "/analytics/health")
async def get_analytics_health(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics system health status"""
    try:
        dashboard_service = DashboardService(db)
        
        # Get basic health metrics
        health_data = await dashboard_service.get_performance_summary(time_range_hours=1)
        
        # Check database connectivity
        db_healthy = True
        try:
            db.execute("SELECT 1").scalar()
        except Exception:
            db_healthy = False
        
        # Check recent data availability
        from app.models.event import Event
        recent_events = db.query(func.count(Event.id)).filter(
            Event.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).scalar() or 0
        
        data_flow_healthy = recent_events > 0
        
        overall_health = "healthy" if (
            db_healthy and 
            data_flow_healthy and 
            health_data["health_status"] in ["excellent", "good"]
        ) else "degraded" if db_healthy else "unhealthy"
        
        return {
            "success": True,
            "data": {
                "overall_health": overall_health,
                "components": {
                    "database": "healthy" if db_healthy else "unhealthy",
                    "data_flow": "healthy" if data_flow_healthy else "degraded",
                    "performance": health_data["health_status"]
                },
                "metrics": {
                    "recent_events": recent_events,
                    "health_score": health_data["health_score"],
                    "alerts_count": health_data["alerts_count"]
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics health: {str(e)}")


@router.get("/monitoring/health")
@measure_api_request("GET", "/analytics/monitoring/health")
async def get_comprehensive_health(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive health report including landing page and CRM integration monitoring"""
    try:
        monitor = LandingPageMonitor(db)
        health_report = await monitor.get_comprehensive_health_report()
        
        return {
            "success": True,
            "data": health_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comprehensive health: {str(e)}")


@router.get("/monitoring/alerts")
@measure_api_request("GET", "/analytics/monitoring/alerts")
async def get_performance_alerts(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current performance alerts"""
    try:
        monitor = LandingPageMonitor(db)
        alerts = await monitor.check_performance_alerts()
        
        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "alerts_count": len(alerts),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance alerts: {str(e)}")


@router.post("/monitoring/health-check")
@measure_api_request("POST", "/analytics/monitoring/health-check")
async def run_health_check(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger a comprehensive health check"""
    try:
        monitor = LandingPageMonitor(db)
        health_report = await monitor.run_health_check_cycle()
        
        return {
            "success": True,
            "data": health_report,
            "message": "Health check completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run health check: {str(e)}")
