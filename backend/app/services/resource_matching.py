"""
Resource Matching Service
Matches emergency requests to available resources using multi-factor scoring
"""
import math
import json
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import logging

from app.config import settings
from app.models.schemas import (
    ExtractedInformation, Resource, ResourceMatch, MatchingFactors,
    NeedType, ResourceType
)

logger = logging.getLogger(__name__)

# Backend System Prompt for AI-Enhanced Resource Matching
BACKEND_SYSTEM_PROMPT = """You are an AI decision-support backend for an emergency response system.
Your role is to assist human dispatchers by analyzing crisis requests and recommending only pre-verified emergency resources in a transparent, explainable manner.

You must never autonomously dispatch resources. All final decisions are made by humans.

## Core Objective
Support faster and safer emergency triage by ranking and explaining verified resource recommendations, while maintaining human-in-the-loop control and safety.

## Processing Rules

1. **Verification Constraint**
   - Use only resources where "verified": true
   - Ignore or discard unverified entries

2. **Resource Filtering**
   - Filter resources based on:
     * Matching service type with request need
     * Availability status
     * Minimum required capacity

3. **Resource Scoring (Explainable)**
   - Score each eligible resource using:
     * Suitability to the request (40% weight)
     * Real-time availability (30% weight)
     * Capacity sufficiency (15% weight)
     * Distance or response time (15% weight)
     * Operational constraints
   - You must compute a final weighted score and expose all component scores

4. **Ranking**
   - Rank resources from highest to lowest score
   - Include at least one fallback option if confidence is low

5. **Output Format**
   - Return a ranked list with human-readable explanations
   - Include reasoning steps for transparency
   - Highlight trade-offs and limitations

## Human-in-the-Loop Rules
- Always require dispatcher confirmation
- Never issue commands or dispatch actions
- Highlight uncertainty or low confidence explicitly
- Allow human override at all stages

## Safety & Ethics Constraints
- Prioritize safety over speed when uncertain
- Never hide reasoning
- Avoid penalizing unclear language or emotional expression
- Treat every request as potentially life-critical

## Failure & Uncertainty Handling
If:
- No suitable resource is available
- Capacity is insufficient
- Location is ambiguous

Then:
- Flag the issue clearly
- Suggest multiple fallback options
- Request human review

## Final Constraints
❌ No autonomous dispatch
❌ No unverified resources
❌ No opaque scoring
✅ Always explain
✅ Always defer to humans
✅ Always maintain transparency
"""


class ResourceMatchingService:
    """Service for matching emergency requests to available resources"""
    
    # Mapping of needs to suitable resource types
    NEED_TO_RESOURCE_MAP = {
        NeedType.MEDICAL_AID: [ResourceType.AMBULANCE, ResourceType.MEDICAL_TEAM],
        NeedType.FOOD: [ResourceType.FOOD_SUPPLIES, ResourceType.SUPPLIES],
        NeedType.WATER: [ResourceType.WATER_SUPPLIES, ResourceType.SUPPLIES],
        NeedType.SHELTER: [ResourceType.SHELTER_TEAM, ResourceType.SUPPLIES],
        NeedType.EVACUATION: [ResourceType.TRANSPORT, ResourceType.RESCUE_TEAM],
        NeedType.RESCUE: [ResourceType.RESCUE_TEAM, ResourceType.AMBULANCE],
        NeedType.BLANKETS: [ResourceType.SUPPLIES],
        NeedType.CLOTHING: [ResourceType.SUPPLIES],
        NeedType.SANITATION: [ResourceType.SUPPLIES],
        NeedType.PSYCHOLOGICAL_SUPPORT: [ResourceType.MEDICAL_TEAM],
        NeedType.OTHER: [ResourceType.SUPPLIES]
    }
    
    def __init__(self):
        self.weight_suitability = settings.weight_suitability
        self.weight_availability = settings.weight_availability
        self.weight_capacity = settings.weight_capacity
        self.weight_distance = settings.weight_distance
        self.enable_ai_matching = settings.enable_ai_matching
        self.llm_client = None
        
        # Initialize LLM client if AI matching is enabled
        if self.enable_ai_matching:
            self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client for AI-enhanced matching"""
        try:
            if settings.llm_provider == "openai":
                from openai import AsyncOpenAI
                self.llm_client = AsyncOpenAI(api_key=settings.openai_api_key)
            elif settings.llm_provider == "anthropic":
                from anthropic import AsyncAnthropic
                self.llm_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            else:
                logger.warning(f"Unsupported LLM provider: {settings.llm_provider}. AI matching disabled.")
                self.enable_ai_matching = False
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}. AI matching disabled.")
            self.enable_ai_matching = False
    
    async def match_resources(
        self,
        extracted_info: ExtractedInformation,
        max_matches: int = 5,
        use_ai: Optional[bool] = None
    ) -> List[ResourceMatch]:
        """
        Find and rank the best resource matches for an emergency request
        
        Args:
            extracted_info: Extracted information from emergency message
            max_matches: Maximum number of matches to return
            use_ai: Override to force AI or rule-based matching
        
        Returns:
            List of ResourceMatch objects, ranked by match score
        """
        try:
            logger.info("Starting resource matching process")
            
            # Get all active and verified resources
            resources = await Resource.find({
                "status": "active",
                "verified": True  # Only use verified resources as per system prompt
            }).to_list()
            
            if not resources:
                logger.warning("No active verified resources available")
                return []
            
            # Determine if we should use AI matching
            should_use_ai = use_ai if use_ai is not None else self.enable_ai_matching
            
            # Use AI-enhanced matching if enabled and confidence is sufficient
            if (should_use_ai and self.llm_client and
                extracted_info.extraction_confidence >= settings.ai_matching_min_confidence):
                logger.info("Using AI-enhanced resource matching")
                try:
                    matches = await self._ai_match_resources(
                        extracted_info, resources, max_matches
                    )
                    if matches:
                        return matches
                except Exception as e:
                    logger.error(f"AI matching failed: {e}")
                logger.info("Falling back to rule-based matching")
            
            # Use rule-based matching (default or fallback)
            logger.info("Using rule-based resource matching")
            return await self._rule_based_match_resources(
                extracted_info, resources, max_matches
            )
            
        except Exception as e:
            logger.error(f"Error matching resources: {e}")
            return []
    
    async def _rule_based_match_resources(
        self,
        extracted_info: ExtractedInformation,
        resources: List[Resource],
        max_matches: int
    ) -> List[ResourceMatch]:
        """Rule-based resource matching (original implementation)"""
        # Determine primary need
        primary_need = self._get_primary_need(extracted_info)
        logger.info(f"Primary need identified: {primary_need}")
        
        # Score each resource
        scored_matches = []
        for resource in resources:
            match = await self._score_resource(
                resource,
                extracted_info,
                primary_need
            )
            if match:
                scored_matches.append(match)
        
        # Sort by match score (descending) and take top matches
        scored_matches.sort(key=lambda x: x.match_score, reverse=True)
        top_matches = scored_matches[:max_matches]
        
        logger.info(f"Found {len(scored_matches)} potential matches, returning top {len(top_matches)}")
        
        return top_matches
    
    async def _ai_match_resources(
        self,
        extracted_info: ExtractedInformation,
        resources: List[Resource],
        max_matches: int
    ) -> List[ResourceMatch]:
        """AI-enhanced resource matching using LLM with system prompt"""
        try:
            # Prepare request data
            request_data = {
                "request_id": str(extracted_info.id) if hasattr(extracted_info, 'id') else "PENDING",
                "needs": [{
                    "type": need.need_type.value,
                    "confidence": need.confidence
                } for need in extracted_info.needs] if extracted_info.needs else [],
                "people_affected": extracted_info.people_affected,
                "location": {
                    "address": extracted_info.location.address if extracted_info.location else None,
                    "latitude": extracted_info.location.latitude if extracted_info.location else None,
                    "longitude": extracted_info.location.longitude if extracted_info.location else None
                },
                "urgency_score": extracted_info.urgency_score,
                "confidence": extracted_info.extraction_confidence
            }
            
            # Prepare resource registry
            resource_registry = [{
                "resource_id": res.resource_id,
                "name": res.name,
                "type": res.resource_type.value,
                "services": [cap.value for cap in res.capabilities],
                "location": {
                    "address": res.location.address,
                    "latitude": res.location.latitude,
                    "longitude": res.location.longitude
                },
                "availability": "available" if res.current_availability > 0 else "unavailable",
                "capacity": res.current_availability,
                "response_time_minutes": res.estimated_response_time_minutes,
                "verified": res.verified
            } for res in resources]
            
            # Build the prompt
            user_prompt = f"""Analyze this emergency request and rank the available verified resources.

Emergency Request:
{json.dumps(request_data, indent=2)}

Available Verified Resources:
{json.dumps(resource_registry, indent=2)}

Provide a ranked list of the top {max_matches} resources with detailed scoring and explanations.
Return your response as a JSON object with this structure:
{{
  "recommendations": [
    {{
      "resource_id": "string",
      "final_score": 0.0-1.0,
      "component_scores": {{
        "suitability": 0.0-1.0,
        "availability": 0.0-1.0,
        "capacity": 0.0-1.0,
        "distance": 0.0-1.0
      }},
      "reasoning": ["explanation points"],
      "trade_offs": ["trade-off points"],
      "confidence": "high|medium|low"
    }}
  ],
  "human_action_required": true,
  "warnings": ["any concerns or limitations"]
}}
"""
            
            # Call LLM
            response_text = await self._call_llm_for_matching(user_prompt)
            
            # Parse LLM response
            ai_response = json.loads(response_text)
            
            # Convert AI recommendations to ResourceMatch objects
            matches = []
            for rec in ai_response.get("recommendations", [])[:max_matches]:
                # Find the corresponding resource
                resource = next((r for r in resources if r.resource_id == rec["resource_id"]), None)
                if not resource:
                    continue
                
                # Get component scores
                scores = rec.get("component_scores", {})
                
                # Create matching factors
                matching_factors = MatchingFactors(
                    suitability_score=scores.get("suitability", 0.5),
                    suitability_explanation="AI: " + "; ".join(rec.get("reasoning", [])),
                    availability_score=scores.get("availability", 0.5),
                    availability_explanation=f"AI: Resource availability assessed",
                    capacity_score=scores.get("capacity", 0.5),
                    capacity_explanation=f"AI: Capacity match assessed",
                    distance_score=scores.get("distance", 0.5),
                    distance_explanation=f"AI: Distance factor assessed"
                )
                
                # Calculate distance if possible
                distance_km = None
                if extracted_info.location and extracted_info.location.latitude:
                    distance_km = self._haversine_distance(
                        resource.location.latitude,
                        resource.location.longitude,
                        extracted_info.location.latitude,
                        extracted_info.location.longitude
                    )
                
                # Create match
                match = ResourceMatch(
                    resource_id=resource.resource_id,
                    resource_name=resource.name,
                    resource_type=resource.resource_type,
                    match_score=round(rec["final_score"], 3),
                    matching_factors=matching_factors,
                    distance_km=distance_km,
                    estimated_arrival_minutes=self._estimate_arrival_time(
                        distance_km, resource.estimated_response_time_minutes
                    ),
                    overall_explanation="AI-Enhanced: " + "; ".join(rec.get("reasoning", [])),
                    trade_offs=rec.get("trade_offs", []),
                    confidence_level=0.8 if rec.get("confidence") == "high" else 0.6 if rec.get("confidence") == "medium" else 0.4
                )
                matches.append(match)
            
            logger.info(f"AI matching returned {len(matches)} recommendations")
            return matches
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return []
        except Exception as e:
            logger.error(f"AI matching error: {e}")
            return []
    
    async def _call_llm_for_matching(self, user_prompt: str) -> str:
        """Call LLM for resource matching with system prompt"""
        if settings.llm_provider == "openai":
            response = await self.llm_client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": BACKEND_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
            return response.choices[0].message.content
        elif settings.llm_provider == "anthropic":
            response = await self.llm_client.messages.create(
                model=settings.llm_model,
                system=BACKEND_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
            return response.content[0].text
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    
    def _get_primary_need(self, extracted_info: ExtractedInformation) -> Optional[NeedType]:
        """Determine the primary need from extracted needs"""
        if not extracted_info.needs:
            return None
        
        # Sort by confidence and return highest confidence need
        sorted_needs = sorted(extracted_info.needs, key=lambda x: x.confidence, reverse=True)
        return sorted_needs[0].need_type
    
    async def _score_resource(
        self,
        resource: Resource,
        extracted_info: ExtractedInformation,
        primary_need: Optional[NeedType]
    ) -> Optional[ResourceMatch]:
        """
        Score a single resource against the request
        
        Returns None if resource is completely unsuitable
        """
        # Calculate individual factor scores
        suitability_score, suitability_explanation = self._calculate_suitability(
            resource, extracted_info, primary_need
        )
        
        # Skip if completely unsuitable
        if suitability_score == 0.0:
            return None
        
        availability_score, availability_explanation = self._calculate_availability(resource)
        capacity_score, capacity_explanation = self._calculate_capacity(
            resource, extracted_info
        )
        distance_score, distance_explanation, distance_km = self._calculate_distance(
            resource, extracted_info
        )
        
        # Calculate weighted total score
        match_score = (
            suitability_score * self.weight_suitability +
            availability_score * self.weight_availability +
            capacity_score * self.weight_capacity +
            distance_score * self.weight_distance
        )
        
        # Create matching factors explanation
        matching_factors = MatchingFactors(
            suitability_score=suitability_score,
            suitability_explanation=suitability_explanation,
            availability_score=availability_score,
            availability_explanation=availability_explanation,
            capacity_score=capacity_score,
            capacity_explanation=capacity_explanation,
            distance_score=distance_score,
            distance_explanation=distance_explanation
        )
        
        # Generate overall explanation
        overall_explanation = self._generate_match_explanation(
            resource, matching_factors, match_score
        )
        
        # Identify trade-offs
        trade_offs = self._identify_tradeoffs(matching_factors)
        
        # Estimate arrival time
        estimated_arrival = self._estimate_arrival_time(
            distance_km, resource.estimated_response_time_minutes
        )
        
        # Calculate confidence level
        confidence = self._calculate_match_confidence(matching_factors, extracted_info)
        
        return ResourceMatch(
            resource_id=resource.resource_id,
            resource_name=resource.name,
            resource_type=resource.resource_type,
            match_score=round(match_score, 3),
            matching_factors=matching_factors,
            distance_km=distance_km,
            estimated_arrival_minutes=estimated_arrival,
            overall_explanation=overall_explanation,
            trade_offs=trade_offs,
            confidence_level=confidence
        )
    
    def _calculate_suitability(
        self,
        resource: Resource,
        extracted_info: ExtractedInformation,
        primary_need: Optional[NeedType]
    ) -> Tuple[float, str]:
        """Calculate how suitable the resource is for the needs"""
        
        if not primary_need:
            return 0.5, "No specific need identified, using general suitability"
        
        # Check if resource type matches need
        suitable_types = self.NEED_TO_RESOURCE_MAP.get(primary_need, [])
        
        if resource.resource_type in suitable_types:
            # Check if resource has capability for this need
            if primary_need in resource.capabilities:
                score = 1.0
                explanation = f"Perfectly suited: {resource.resource_type.value} directly matches {primary_need.value} need with specific capability"
            else:
                score = 0.8
                explanation = f"Well suited: {resource.resource_type.value} matches {primary_need.value} need type"
        else:
            # Check for partial capability match
            matching_capabilities = set(resource.capabilities) & set([n.need_type for n in extracted_info.needs])
            if matching_capabilities:
                score = 0.4
                explanation = f"Partially suited: Can address {', '.join([c.value for c in matching_capabilities])} but not primary need"
            else:
                score = 0.0
                explanation = f"Not suitable: {resource.resource_type.value} doesn't match {primary_need.value} need"
        
        return score, explanation
    
    def _calculate_availability(self, resource: Resource) -> Tuple[float, str]:
        """Calculate resource availability score"""
        
        if resource.current_availability <= 0:
            return 0.0, "Not available: Currently fully deployed"
        
        availability_ratio = resource.current_availability / resource.capacity
        
        if availability_ratio >= 0.8:
            explanation = f"Highly available: {resource.current_availability}/{resource.capacity} capacity free"
        elif availability_ratio >= 0.5:
            explanation = f"Available: {resource.current_availability}/{resource.capacity} capacity free"
        elif availability_ratio >= 0.2:
            explanation = f"Limited availability: Only {resource.current_availability}/{resource.capacity} capacity free"
        else:
            explanation = f"Severely limited: Only {resource.current_availability}/{resource.capacity} capacity remaining"
        
        return availability_ratio, explanation
    
    def _calculate_capacity(
        self,
        resource: Resource,
        extracted_info: ExtractedInformation
    ) -> Tuple[float, str]:
        """Calculate if resource has sufficient capacity"""
        
        people_affected = extracted_info.people_affected or 1
        
        if resource.current_availability >= people_affected:
            score = 1.0
            explanation = f"Sufficient capacity: Can serve {resource.current_availability} people (need: {people_affected})"
        elif resource.current_availability > 0:
            ratio = resource.current_availability / people_affected
            score = ratio
            explanation = f"Partial capacity: Can serve {resource.current_availability} people (need: {people_affected})"
        else:
            score = 0.0
            explanation = "No capacity available"
        
        return min(score, 1.0), explanation
    
    def _calculate_distance(
        self,
        resource: Resource,
        extracted_info: ExtractedInformation
    ) -> Tuple[float, str, Optional[float]]:
        """Calculate distance score (closer is better)"""
        
        # If no location available, use neutral score
        if not extracted_info.location or not extracted_info.location.latitude:
            return 0.5, "Location unknown: Cannot calculate distance", None
        
        # Calculate Haversine distance
        distance_km = self._haversine_distance(
            resource.location.latitude,
            resource.location.longitude,
            extracted_info.location.latitude,
            extracted_info.location.longitude
        )
        
        # Score based on distance (exponential decay)
        # Perfect score at 0km, 0.5 at 50km, approaching 0 at large distances
        if distance_km <= 5:
            score = 1.0
            explanation = f"Very close: {distance_km:.1f} km away"
        elif distance_km <= 20:
            score = 0.8
            explanation = f"Nearby: {distance_km:.1f} km away"
        elif distance_km <= 50:
            score = 0.5
            explanation = f"Moderate distance: {distance_km:.1f} km away"
        elif distance_km <= 100:
            score = 0.3
            explanation = f"Far: {distance_km:.1f} km away"
        else:
            score = 0.1
            explanation = f"Very far: {distance_km:.1f} km away"
        
        return score, explanation, distance_km
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        return round(distance, 2)
    
    def _generate_match_explanation(
        self,
        resource: Resource,
        factors: MatchingFactors,
        match_score: float
    ) -> str:
        """Generate human-readable explanation of the match"""
        
        quality = "excellent" if match_score >= 0.8 else "good" if match_score >= 0.6 else "fair" if match_score >= 0.4 else "poor"
        
        explanation = f"This is a {quality} match (score: {match_score:.2f}). "
        
        # Highlight strongest factor
        factors_dict = {
            "suitability": factors.suitability_score,
            "availability": factors.availability_score,
            "capacity": factors.capacity_score,
            "distance": factors.distance_score
        }
        
        strongest = max(factors_dict, key=factors_dict.get)
        weakest = min(factors_dict, key=factors_dict.get)
        
        explanation += f"Strongest factor: {strongest} ({factors_dict[strongest]:.2f}). "
        if factors_dict[weakest] < 0.4:
            explanation += f"Limitation: {weakest} ({factors_dict[weakest]:.2f}). "
        
        return explanation
    
    def _identify_tradeoffs(self, factors: MatchingFactors) -> List[str]:
        """Identify trade-offs in the matching decision"""
        trade_offs = []
        
        if factors.suitability_score >= 0.8 and factors.distance_score < 0.5:
            trade_offs.append("High suitability but longer distance - faster response vs better match")
        
        if factors.distance_score >= 0.8 and factors.suitability_score < 0.6:
            trade_offs.append("Close distance but lower suitability - speed vs capability")
        
        if factors.availability_score < 0.5:
            trade_offs.append("Limited availability - may need to wait or use partial capacity")
        
        if factors.capacity_score < 0.7:
            trade_offs.append("Insufficient capacity - may need multiple resources or prioritization")
        
        return trade_offs
    
    def _estimate_arrival_time(
        self,
        distance_km: Optional[float],
        base_response_time: int
    ) -> Optional[int]:
        """Estimate arrival time in minutes"""
        if distance_km is None:
            return None
        
        # Assume average speed of 60 km/h in emergency
        travel_time = (distance_km / 60) * 60  # Convert to minutes
        total_time = base_response_time + travel_time
        
        return int(total_time)
    
    def _calculate_match_confidence(
        self,
        factors: MatchingFactors,
        extracted_info: ExtractedInformation
    ) -> float:
        """Calculate confidence in the match quality"""
        
        # Base confidence on extraction confidence and factor scores
        base_confidence = extracted_info.extraction_confidence
        
        # Reduce confidence if any factor is very low
        min_factor = min([
            factors.suitability_score,
            factors.availability_score,
            factors.capacity_score,
            factors.distance_score
        ])
        
        if min_factor < 0.3:
            base_confidence *= 0.7
        elif min_factor < 0.5:
            base_confidence *= 0.85
        
        return round(base_confidence, 2)
