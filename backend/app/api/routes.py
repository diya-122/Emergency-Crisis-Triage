"""
API Routes for Emergency Triage System
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.schemas import (
    EmergencyMessage, TriageResponse, EmergencyRequest,
    ConfirmationRequest, Resource, DashboardStats, RequestStatus
)
from app.services.triage_service import TriageService
from app.database import get_database

router = APIRouter()
triage_service = TriageService()


@router.post("/triage", response_model=TriageResponse)
async def triage_emergency(message: EmergencyMessage):
    """
    Process an emergency message and perform complete triage
    
    This endpoint:
    1. Extracts structured information from unstructured message
    2. Calculates explainable urgency score
    3. Matches request to available resources
    4. Returns decision support information for dispatcher
    
    **Human-in-the-loop:** AI provides recommendations, human makes final decision
    """
    try:
        response = await triage_service.process_emergency_message(message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage processing failed: {str(e)}")


@router.post("/confirm")
async def confirm_dispatch(confirmation: ConfirmationRequest):
    """
    Confirm dispatcher decision and dispatch resource
    
    **Critical human-in-the-loop checkpoint**
    
    Dispatcher reviews AI recommendations and makes final decision:
    - Approve recommended resource
    - Select different resource (override)
    - Cancel/escalate request
    """
    try:
        updated_request = await triage_service.confirm_dispatch(
            request_id=confirmation.request_id,
            selected_resource_id=confirmation.selected_resource_id,
            dispatcher_id=confirmation.dispatcher_id,
            notes=confirmation.dispatcher_notes,
            override_reason=confirmation.override_reason
        )
        return {
            "status": "confirmed",
            "request_id": updated_request.request_id,
            "dispatched": updated_request.status == RequestStatus.DISPATCHED
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Confirmation failed: {str(e)}")


@router.get("/requests", response_model=List[EmergencyRequest])
async def list_requests(
    status: Optional[RequestStatus] = None,
    limit: int = 50,
    skip: int = 0
):
    """
    List emergency requests with optional filtering
    
    Query parameters:
    - status: Filter by request status (pending, processing, dispatched, etc.)
    - limit: Maximum number of results (default: 50)
    - skip: Number of results to skip for pagination (default: 0)
    """
    try:
        query = {}
        if status:
            query["status"] = status
        
        requests = await EmergencyRequest.find(query)\
            .sort("-received_at")\
            .skip(skip)\
            .limit(limit)\
            .to_list()
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve requests: {str(e)}")


@router.get("/requests/{request_id}", response_model=EmergencyRequest)
async def get_request(request_id: str):
    """Get detailed information about a specific request"""
    request = await EmergencyRequest.find_one({"request_id": request_id})
    
    if not request:
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")
    
    return request


@router.get("/resources", response_model=List[Resource])
async def list_resources(
    status: Optional[str] = None,
    resource_type: Optional[str] = None
):
    """
    List available resources
    
    Query parameters:
    - status: Filter by status (active, inactive, deployed)
    - resource_type: Filter by resource type
    """
    try:
        query = {}
        if status:
            query["status"] = status
        if resource_type:
            query["resource_type"] = resource_type
        
        resources = await Resource.find(query).to_list()
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resources: {str(e)}")


@router.post("/resources", response_model=Resource)
async def create_resource(resource: Resource):
    """Create a new resource in the system"""
    try:
        await resource.insert()
        return resource
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create resource: {str(e)}")


@router.put("/resources/{resource_id}")
async def update_resource(resource_id: str, updates: dict):
    """Update resource information"""
    resource = await Resource.find_one({"resource_id": resource_id})
    
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
    
    try:
        for key, value in updates.items():
            if hasattr(resource, key):
                setattr(resource, key, value)
        
        resource.updated_at = datetime.utcnow()
        await resource.save()
        
        return {"status": "updated", "resource_id": resource_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update resource: {str(e)}")


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """
    Get statistics for dispatcher dashboard
    
    Returns real-time metrics:
    - Total requests and breakdowns by status
    - Average triage time
    - Urgent requests count
    - Resource availability
    """
    try:
        # Count requests by status
        total_requests = await EmergencyRequest.count()
        pending_requests = await EmergencyRequest.find({"status": RequestStatus.PENDING}).count()
        processing_requests = await EmergencyRequest.find({"status": RequestStatus.PROCESSING}).count()
        completed_requests = await EmergencyRequest.find({"status": RequestStatus.COMPLETED}).count()
        
        # Count critical/high urgency requests
        critical_requests = await EmergencyRequest.find({
            "extracted_info.urgency_level": "critical",
            "status": {"$in": ["pending", "processing"]}
        }).count()
        
        high_urgency_requests = await EmergencyRequest.find({
            "extracted_info.urgency_level": "high",
            "status": {"$in": ["pending", "processing"]}
        }).count()
        
        # Calculate average triage time (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_requests = await EmergencyRequest.find({
            "received_at": {"$gte": yesterday},
            "processing_time_seconds": {"$exists": True}
        }).to_list()
        
        if recent_requests:
            avg_triage_time = sum(r.processing_time_seconds for r in recent_requests) / len(recent_requests)
        else:
            avg_triage_time = 0.0
        
        # Count available and deployed resources
        resources_available = await Resource.find({"status": "active"}).count()
        resources_deployed = await Resource.find({"status": "deployed"}).count()
        
        return DashboardStats(
            total_requests=total_requests,
            pending_requests=pending_requests,
            processing_requests=processing_requests,
            completed_requests=completed_requests,
            average_triage_time_seconds=round(avg_triage_time, 2),
            critical_requests=critical_requests,
            high_urgency_requests=high_urgency_requests,
            resources_available=resources_available,
            resources_deployed=resources_deployed
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")


@router.get("/health")
async def health_check(db = Depends(get_database)):
    """Health check endpoint"""
    from app.database import db_manager
    
    db_healthy = await db_manager.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }
