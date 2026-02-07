"""
Main Triage Service
Orchestrates the complete triage workflow: extraction, scoring, matching
"""
from datetime import datetime
import logging
import uuid
from typing import Optional

from app.models.schemas import (
    EmergencyMessage, EmergencyRequest, ExtractedInformation,
    TriageResponse, ResourceMatch, RequestStatus, MessageSource
)
from app.services.nlp_service import NLPService
from app.services.resource_matching import ResourceMatchingService
from app.services.geocoding import GeocodingService

logger = logging.getLogger(__name__)


class TriageService:
    """Main service for emergency request triage"""
    
    def __init__(self):
        self.nlp_service = NLPService()
        self.matching_service = ResourceMatchingService()
        self.geocoding_service = GeocodingService()
    
    async def process_emergency_message(
        self,
        message: EmergencyMessage
    ) -> TriageResponse:
        """
        Complete triage workflow for an emergency message
        
        1. Extract structured information using NLP
        2. Geocode location if possible
        3. Match to available resources
        4. Store request in database
        5. Return decision support information
        
        Returns:
            TriageResponse with all analysis and recommendations
        """
        start_time = datetime.utcnow()
        request_id = str(uuid.uuid4())
        
        logger.info(f"Processing emergency request {request_id}")
        
        try:
            # Step 1: Extract information using NLP
            extracted_info = await self.nlp_service.extract_information(
                message.message,
                metadata={
                    'source': message.source,
                    'phone_number': message.phone_number
                }
            )
            
            # Step 2: Enhance with geocoding if location found
            if extracted_info.location and extracted_info.location.raw_text:
                geocoded_location = await self.geocoding_service.geocode(
                    extracted_info.location.raw_text
                )
                if geocoded_location:
                    extracted_info.location = geocoded_location
            
            # Step 3: Match resources
            matched_resources = await self.matching_service.match_resources(
                extracted_info,
                max_matches=5
            )
            
            # Step 4: Determine if human confirmation required
            requires_confirmation = self._requires_human_confirmation(
                extracted_info,
                matched_resources
            )
            
            # Step 5: Generate warnings
            warnings = self._generate_warnings(extracted_info, matched_resources)
            
            # Step 6: Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Step 7: Save to database
            await self._save_request(
                request_id=request_id,
                message=message,
                extracted_info=extracted_info,
                matched_resources=matched_resources,
                processing_time=processing_time
            )
            
            logger.info(
                f"Request {request_id} processed in {processing_time:.2f}s. "
                f"Urgency: {extracted_info.urgency_level}, "
                f"Matches: {len(matched_resources)}"
            )
            
            # Step 8: Create response
            return TriageResponse(
                request_id=request_id,
                status="processed",
                extracted_info=extracted_info,
                matched_resources=matched_resources,
                processing_time_seconds=round(processing_time, 3),
                requires_confirmation=requires_confirmation,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}", exc_info=True)
            raise
    
    def _requires_human_confirmation(
        self,
        extracted_info: ExtractedInformation,
        matches: list
    ) -> bool:
        """
        Determine if human confirmation is required before dispatch
        
        Confirmation required when:
        - Critical urgency (life-threatening)
        - Low extraction confidence
        - No good resource matches
        - Conflicting information
        """
        # Always require confirmation for critical cases
        if extracted_info.urgency_level.value == "critical":
            return True
        
        # Require confirmation if extraction confidence is low
        if extracted_info.extraction_confidence < 0.6:
            return True
        
        # Require confirmation if no good matches
        if not matches or (matches and matches[0].match_score < 0.5):
            return True
        
        # Require confirmation if top match has low confidence
        if matches and matches[0].confidence_level < 0.6:
            return True
        
        return False
    
    def _generate_warnings(
        self,
        extracted_info: ExtractedInformation,
        matches: list
    ) -> list:
        """Generate warnings for dispatcher attention"""
        warnings = []
        
        # Low extraction confidence
        if extracted_info.extraction_confidence < 0.7:
            warnings.append(
                f"Low extraction confidence ({extracted_info.extraction_confidence:.2f}). "
                "Please verify extracted information manually."
            )
        
        # Missing location
        if not extracted_info.location or not extracted_info.location.is_geocoded:
            warnings.append(
                "Location could not be precisely determined. "
                "Distance calculations may be inaccurate."
            )
        
        # No matches found
        if not matches:
            warnings.append(
                "No suitable resources found. Manual allocation required."
            )
        
        # Low confidence matches
        if matches and matches[0].match_score < 0.5:
            warnings.append(
                f"Best match has low score ({matches[0].match_score:.2f}). "
                "Consider alternative resources."
            )
        
        # Critical with no immediate options
        if extracted_info.urgency_level.value == "critical":
            if not matches or matches[0].estimated_arrival_minutes and matches[0].estimated_arrival_minutes > 30:
                warnings.append(
                    "CRITICAL: Life-threatening situation but no immediate resources available. "
                    "Consider emergency alternatives."
                )
        
        # Vulnerable populations with limited capacity
        if extracted_info.vulnerable_populations and matches:
            if matches[0].matching_factors.capacity_score < 0.7:
                warnings.append(
                    "Vulnerable populations present with limited resource capacity. "
                    "Prioritize accordingly."
                )
        
        return warnings
    
    async def _save_request(
        self,
        request_id: str,
        message: EmergencyMessage,
        extracted_info: ExtractedInformation,
        matched_resources: list,
        processing_time: float
    ):
        """Save emergency request to database"""
        
        request = EmergencyRequest(
            request_id=request_id,
            original_message=message.message,
            source=message.source,
            phone_number=message.phone_number,
            received_at=message.timestamp,
            extracted_info=extracted_info,
            matched_resources=matched_resources,
            status=RequestStatus.PENDING,
            processing_started_at=datetime.utcnow(),
            processing_completed_at=datetime.utcnow(),
            processing_time_seconds=processing_time,
            metadata=message.metadata
        )
        
        await request.insert()
        logger.info(f"Request {request_id} saved to database")
    
    async def confirm_dispatch(
        self,
        request_id: str,
        selected_resource_id: Optional[str],
        dispatcher_id: str,
        notes: Optional[str] = None,
        override_reason: Optional[str] = None
    ) -> EmergencyRequest:
        """
        Process human confirmation of resource dispatch
        
        Human-in-the-loop: Dispatcher makes final decision
        """
        logger.info(f"Processing dispatch confirmation for request {request_id}")
        
        # Retrieve request
        request = await EmergencyRequest.find_one({"request_id": request_id})
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        # Record human decision
        request.dispatcher_confirmed = True
        request.confirmation_timestamp = datetime.utcnow()
        request.dispatcher_id = dispatcher_id
        request.dispatcher_notes = notes
        request.assigned_resource_id = selected_resource_id
        
        # Track overrides (if dispatcher chose different resource than top recommendation)
        if selected_resource_id:
            top_recommendation = request.matched_resources[0].resource_id if request.matched_resources else None
            if top_recommendation and selected_resource_id != top_recommendation:
                request.human_overrides.append({
                    'timestamp': datetime.utcnow(),
                    'dispatcher_id': dispatcher_id,
                    'recommended_resource': top_recommendation,
                    'selected_resource': selected_resource_id,
                    'reason': override_reason or "Manual selection"
                })
                logger.info(f"Human override: Selected {selected_resource_id} instead of {top_recommendation}")
        
        # Update status
        if selected_resource_id:
            request.status = RequestStatus.DISPATCHED
            request.dispatched_at = datetime.utcnow()
            
            # Update resource availability
            resource = await self._allocate_resource(selected_resource_id, request)
        else:
            request.status = RequestStatus.CANCELLED
        
        await request.save()
        logger.info(f"Dispatch confirmed for request {request_id}")
        
        return request
    
    async def _allocate_resource(self, resource_id: str, request: EmergencyRequest):
        """Allocate resource and update availability"""
        from app.models.schemas import Resource
        
        resource = await Resource.find_one({"resource_id": resource_id})
        if resource:
            people_affected = request.extracted_info.people_affected or 1
            resource.current_availability = max(0, resource.current_availability - people_affected)
            resource.status = "deployed" if resource.current_availability == 0 else "active"
            resource.updated_at = datetime.utcnow()
            await resource.save()
            logger.info(f"Resource {resource_id} allocated. Remaining capacity: {resource.current_availability}")
        
        return resource
