"""
Data models and schemas for the Emergency Crisis Triage System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from beanie import Document


class MessageSource(str, Enum):
    """Source of the emergency message"""
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    CHAT = "chat"
    PHONE = "phone"
    EMAIL = "email"
    OTHER = "other"


class NeedType(str, Enum):
    """Types of emergency needs"""
    MEDICAL_AID = "medical_aid"
    FOOD = "food"
    WATER = "water"
    SHELTER = "shelter"
    EVACUATION = "evacuation"
    RESCUE = "rescue"
    BLANKETS = "blankets"
    CLOTHING = "clothing"
    SANITATION = "sanitation"
    PSYCHOLOGICAL_SUPPORT = "psychological_support"
    OTHER = "other"


class UrgencyLevel(str, Enum):
    """Urgency classification levels"""
    CRITICAL = "critical"  # Life-threatening, immediate response required
    HIGH = "high"          # Urgent, response within 1 hour
    MEDIUM = "medium"      # Important, response within 4 hours
    LOW = "low"            # Standard priority, response within 24 hours


class ResourceType(str, Enum):
    """Types of available resources"""
    AMBULANCE = "ambulance"
    MEDICAL_TEAM = "medical_team"
    FOOD_SUPPLIES = "food_supplies"
    WATER_SUPPLIES = "water_supplies"
    SHELTER_TEAM = "shelter_team"
    RESCUE_TEAM = "rescue_team"
    TRANSPORT = "transport"
    SUPPLIES = "supplies"


class RequestStatus(str, Enum):
    """Status of emergency requests"""
    PENDING = "pending"
    PROCESSING = "processing"
    MATCHED = "matched"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ===== Input Models =====

class EmergencyMessage(BaseModel):
    """Raw emergency message input"""
    message: str = Field(..., description="The unstructured emergency message")
    source: MessageSource = Field(default=MessageSource.OTHER)
    phone_number: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ===== Extracted Information Models =====

class ExtractedNeed(BaseModel):
    """A single extracted need from the message"""
    need_type: NeedType
    quantity: Optional[int] = None
    description: str
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedLocation(BaseModel):
    """Location information extracted from message"""
    raw_text: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: float = Field(ge=0.0, le=1.0)
    is_geocoded: bool = False


class VulnerablePopulation(BaseModel):
    """Information about vulnerable populations mentioned"""
    type: str  # e.g., "elderly", "children", "disabled", "pregnant"
    count: Optional[int] = None
    mentioned_in_text: str


class UrgencyFactors(BaseModel):
    """Detailed breakdown of urgency scoring factors"""
    medical_risk_score: float = Field(ge=0.0, le=1.0, description="Medical emergency severity (0-1)")
    vulnerable_pop_score: float = Field(ge=0.0, le=1.0, description="Vulnerable population factor (0-1)")
    time_sensitivity_score: float = Field(ge=0.0, le=1.0, description="Time-critical language (0-1)")
    message_confidence_score: float = Field(ge=0.0, le=1.0, description="Message clarity/confidence (0-1)")
    severity_score: float = Field(ge=0.0, le=1.0, description="Overall severity indicators (0-1)")
    
    # Explanation components
    medical_risk_explanation: str
    vulnerable_pop_explanation: str
    time_sensitivity_explanation: str
    message_confidence_explanation: str
    severity_explanation: str


class ExtractedInformation(BaseModel):
    """Complete structured information extracted from emergency message"""
    needs: List[ExtractedNeed]
    location: Optional[ExtractedLocation] = None
    people_affected: Optional[int] = None
    vulnerable_populations: List[VulnerablePopulation] = Field(default_factory=list)
    urgency_factors: UrgencyFactors
    urgency_level: UrgencyLevel
    urgency_score: float = Field(ge=0.0, le=1.0)
    overall_explanation: str
    language_detected: Optional[str] = None
    extraction_confidence: float = Field(ge=0.0, le=1.0)


# ===== Resource Models =====

class ResourceLocation(BaseModel):
    """Location of a resource"""
    address: str
    latitude: float
    longitude: float
    region: Optional[str] = None


class Resource(Document):
    """Available resource in the system"""
    resource_id: str = Field(..., unique=True)
    resource_type: ResourceType
    name: str
    description: str
    location: ResourceLocation
    capacity: int = Field(gt=0, description="Total capacity")
    current_availability: int = Field(ge=0, description="Currently available capacity")
    capabilities: List[NeedType] = Field(default_factory=list)
    status: str = "active"  # active, inactive, deployed
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    estimated_response_time_minutes: int = Field(default=30)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "resources"
        indexes = ["resource_id", "resource_type", "status"]


# ===== Resource Matching Models =====

class MatchingFactors(BaseModel):
    """Detailed breakdown of resource matching scores"""
    suitability_score: float = Field(ge=0.0, le=1.0)
    availability_score: float = Field(ge=0.0, le=1.0)
    capacity_score: float = Field(ge=0.0, le=1.0)
    distance_score: float = Field(ge=0.0, le=1.0)
    
    suitability_explanation: str
    availability_explanation: str
    capacity_explanation: str
    distance_explanation: str


class ResourceMatch(BaseModel):
    """A matched resource for a request"""
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    match_score: float = Field(ge=0.0, le=1.0)
    matching_factors: MatchingFactors
    distance_km: Optional[float] = None
    estimated_arrival_minutes: Optional[int] = None
    overall_explanation: str
    trade_offs: List[str] = Field(default_factory=list)
    confidence_level: float = Field(ge=0.0, le=1.0)


# ===== Request Models =====

class EmergencyRequest(Document):
    """Complete emergency request with extracted info and matching"""
    request_id: str = Field(..., unique=True)
    
    # Original message
    original_message: str
    source: MessageSource
    phone_number: Optional[str] = None
    received_at: datetime
    
    # Extracted information
    extracted_info: Optional[ExtractedInformation] = None
    
    # Resource matching
    matched_resources: List[ResourceMatch] = Field(default_factory=list)
    
    # Status tracking
    status: RequestStatus = RequestStatus.PENDING
    assigned_resource_id: Optional[str] = None
    dispatcher_notes: Optional[str] = None
    dispatcher_id: Optional[str] = None
    
    # Human decisions
    human_overrides: List[Dict[str, Any]] = Field(default_factory=list)
    dispatcher_confirmed: bool = False
    confirmation_timestamp: Optional[datetime] = None
    
    # Timestamps
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    dispatched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    processing_time_seconds: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "emergency_requests"
        indexes = ["request_id", "status", "received_at", "urgency_level"]


# ===== API Response Models =====

class TriageResponse(BaseModel):
    """Response from triage processing"""
    request_id: str
    status: str
    extracted_info: ExtractedInformation
    matched_resources: List[ResourceMatch]
    processing_time_seconds: float
    requires_confirmation: bool
    warnings: List[str] = Field(default_factory=list)


class ConfirmationRequest(BaseModel):
    """Dispatcher confirmation of decision"""
    request_id: str
    confirmed: bool
    selected_resource_id: Optional[str] = None
    dispatcher_notes: Optional[str] = None
    dispatcher_id: str
    override_reason: Optional[str] = None


class DashboardStats(BaseModel):
    """Statistics for dashboard"""
    total_requests: int
    pending_requests: int
    processing_requests: int
    completed_requests: int
    average_triage_time_seconds: float
    critical_requests: int
    high_urgency_requests: int
    resources_available: int
    resources_deployed: int
