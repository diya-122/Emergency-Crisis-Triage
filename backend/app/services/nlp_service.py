"""
NLP Service for extracting structured information from unstructured emergency messages
Uses LLM for intelligent extraction with explainability
"""
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.config import settings
from app.models.schemas import (
    ExtractedInformation, ExtractedNeed, ExtractedLocation,
    VulnerablePopulation, UrgencyFactors, UrgencyLevel, NeedType
)

logger = logging.getLogger(__name__)


class NLPService:
    """Service for natural language processing of emergency messages"""
    
    def __init__(self):
        self.llm_provider = settings.llm_provider
        self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize the appropriate LLM client"""
        if self.llm_provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.llm_provider == "anthropic":
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    async def extract_information(self, message: str, metadata: Dict[str, Any] = None) -> ExtractedInformation:
        """
        Extract structured information from unstructured emergency message
        
        Args:
            message: Raw emergency message text
            metadata: Additional context (source, timestamp, etc.)
        
        Returns:
            ExtractedInformation with all structured data and explanations
        """
        try:
            logger.info(f"Processing emergency message: {message[:100]}...")
            
            # Build the extraction prompt
            prompt = self._build_extraction_prompt(message, metadata)
            
            # Call LLM for structured extraction
            extraction_result = await self._call_llm(prompt)
            
            # Parse and validate the response
            extracted_info = self._parse_extraction_result(extraction_result, message)
            
            logger.info(f"Extraction completed. Urgency: {extracted_info.urgency_level}, Score: {extracted_info.urgency_score:.2f}")
            
            return extracted_info
            
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            # Return fallback extraction with low confidence
            return self._create_fallback_extraction(message)
    
    def _build_extraction_prompt(self, message: str, metadata: Optional[Dict] = None) -> str:
        """Build the LLM prompt for information extraction"""
        
        prompt = f"""You are an AI assistant helping emergency dispatchers analyze crisis messages. Your task is to extract structured information from an unstructured emergency message.

**CRITICAL INSTRUCTIONS:**
1. Extract information ONLY from the message provided
2. Provide TRANSPARENT, EXPLAINABLE reasoning for ALL scores
3. Be cautious with assumptions - indicate uncertainty
4. Consider multilingual and emotional language gracefully
5. DO NOT penalize poor grammar or emotional expression

**MESSAGE TO ANALYZE:**
{message}

**EXTRACTION TASKS:**

1. **NEEDS IDENTIFICATION**
   - What specific help is needed? (medical aid, food, water, shelter, evacuation, rescue, etc.)
   - Quantity estimates (number of people, supplies needed)
   - Confidence level for each need (0.0 to 1.0)

2. **LOCATION EXTRACTION**
   - Any location information mentioned (addresses, landmarks, neighborhoods)
   - Extract raw location text even if incomplete
   - Indicate confidence (0.0 to 1.0)

3. **PEOPLE AFFECTED**
   - How many people are affected?
   - Mention if number is explicit, estimated, or unknown

4. **VULNERABLE POPULATIONS**
   - Are there children, elderly, disabled, pregnant women mentioned?
   - Approximate count if mentioned

5. **URGENCY SCORING** (This is critical - be very detailed)
   
   Score each factor from 0.0 (none) to 1.0 (maximum) with clear explanation:
   
   a) **Medical Risk Score (0.0-1.0)**
      - Life-threatening conditions? Injuries? Illness severity?
      - Explanation: Why this score?
   
   b) **Vulnerable Population Score (0.0-1.0)**
      - Presence of children, elderly, disabled, pregnant?
      - Explanation: What vulnerable groups and why this score?
   
   c) **Time Sensitivity Score (0.0-1.0)**
      - Urgent language? Immediate danger? Deteriorating situation?
      - Explanation: What time indicators are present?
   
   d) **Message Confidence Score (0.0-1.0)**
      - How clear and specific is the message?
      - Explanation: What makes this message clear or unclear?
   
   e) **Severity Score (0.0-1.0)**
      - Overall situation severity indicators?
      - Explanation: What severity cues are present?

6. **URGENCY LEVEL CLASSIFICATION**
   Based on the scores, classify as:
   - CRITICAL: Life-threatening, immediate response (score > 0.75)
   - HIGH: Urgent, response within 1 hour (score 0.5-0.75)
   - MEDIUM: Important, response within 4 hours (score 0.25-0.5)
   - LOW: Standard priority, response within 24 hours (score < 0.25)

7. **OVERALL EXPLANATION**
   Provide a 2-3 sentence summary explaining the urgency classification and key factors.

**OUTPUT FORMAT:**
Return your analysis as a valid JSON object with this structure:

{{
  "needs": [
    {{
      "need_type": "medical_aid|food|water|shelter|evacuation|rescue|other",
      "quantity": <number or null>,
      "description": "specific description",
      "confidence": 0.0-1.0
    }}
  ],
  "location": {{
    "raw_text": "extracted location text",
    "address": "formatted address if clear, else null",
    "confidence": 0.0-1.0
  }},
  "people_affected": <number or null>,
  "vulnerable_populations": [
    {{
      "type": "elderly|children|disabled|pregnant",
      "count": <number or null>,
      "mentioned_in_text": "relevant quote from message"
    }}
  ],
  "urgency_factors": {{
    "medical_risk_score": 0.0-1.0,
    "medical_risk_explanation": "detailed explanation",
    "vulnerable_pop_score": 0.0-1.0,
    "vulnerable_pop_explanation": "detailed explanation",
    "time_sensitivity_score": 0.0-1.0,
    "time_sensitivity_explanation": "detailed explanation",
    "message_confidence_score": 0.0-1.0,
    "message_confidence_explanation": "detailed explanation",
    "severity_score": 0.0-1.0,
    "severity_explanation": "detailed explanation"
  }},
  "urgency_level": "critical|high|medium|low",
  "overall_explanation": "2-3 sentence summary of urgency classification",
  "language_detected": "language code or null",
  "extraction_confidence": 0.0-1.0
}}

**IMPORTANT:** Return ONLY the JSON object, no additional text."""

        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM provider"""
        
        if self.llm_provider == "openai":
            response = await self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "You are an expert emergency triage assistant. Provide accurate, structured analysis with transparent reasoning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
            return response.choices[0].message.content
        
        elif self.llm_provider == "anthropic":
            response = await self.client.messages.create(
                model=settings.llm_model,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
    
    def _parse_extraction_result(self, result: str, original_message: str) -> ExtractedInformation:
        """Parse LLM response into ExtractedInformation model"""
        
        try:
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                result = json_match.group(0)
            
            data = json.loads(result)
            
            # Parse needs
            needs = [
                ExtractedNeed(
                    need_type=NeedType(need['need_type']),
                    quantity=need.get('quantity'),
                    description=need['description'],
                    confidence=need['confidence']
                )
                for need in data.get('needs', [])
            ]
            
            # Parse location
            location = None
            if data.get('location'):
                loc_data = data['location']
                location = ExtractedLocation(
                    raw_text=loc_data['raw_text'],
                    address=loc_data.get('address'),
                    confidence=loc_data['confidence']
                )
            
            # Parse vulnerable populations
            vulnerable_pops = [
                VulnerablePopulation(
                    type=vp['type'],
                    count=vp.get('count'),
                    mentioned_in_text=vp['mentioned_in_text']
                )
                for vp in data.get('vulnerable_populations', [])
            ]
            
            # Parse urgency factors
            uf = data['urgency_factors']
            urgency_factors = UrgencyFactors(
                medical_risk_score=uf['medical_risk_score'],
                medical_risk_explanation=uf['medical_risk_explanation'],
                vulnerable_pop_score=uf['vulnerable_pop_score'],
                vulnerable_pop_explanation=uf['vulnerable_pop_explanation'],
                time_sensitivity_score=uf['time_sensitivity_score'],
                time_sensitivity_explanation=uf['time_sensitivity_explanation'],
                message_confidence_score=uf['message_confidence_score'],
                message_confidence_explanation=uf['message_confidence_explanation'],
                severity_score=uf['severity_score'],
                severity_explanation=uf['severity_explanation']
            )
            
            # Calculate weighted urgency score
            urgency_score = self._calculate_urgency_score(urgency_factors)
            
            # Create extracted information
            extracted_info = ExtractedInformation(
                needs=needs,
                location=location,
                people_affected=data.get('people_affected'),
                vulnerable_populations=vulnerable_pops,
                urgency_factors=urgency_factors,
                urgency_level=UrgencyLevel(data['urgency_level']),
                urgency_score=urgency_score,
                overall_explanation=data['overall_explanation'],
                language_detected=data.get('language_detected'),
                extraction_confidence=data.get('extraction_confidence', 0.8)
            )
            
            return extracted_info
            
        except Exception as e:
            logger.error(f"Error parsing extraction result: {e}")
            logger.error(f"Raw result: {result}")
            raise
    
    def _calculate_urgency_score(self, factors: UrgencyFactors) -> float:
        """Calculate weighted urgency score from factors"""
        
        score = (
            factors.medical_risk_score * settings.weight_medical_risk +
            factors.vulnerable_pop_score * settings.weight_vulnerable_pop +
            factors.time_sensitivity_score * settings.weight_time_sensitivity +
            factors.message_confidence_score * settings.weight_message_confidence +
            factors.severity_score * settings.weight_severity
        )
        
        return round(score, 3)
    
    def _create_fallback_extraction(self, message: str) -> ExtractedInformation:
        """Create a fallback extraction when LLM fails"""
        
        logger.warning("Using fallback extraction")
        
        # Simple keyword-based fallback
        urgency_keywords = {
            'critical': ['dying', 'death', 'critical', 'emergency', 'life-threatening', 'severe'],
            'high': ['urgent', 'soon', 'quickly', 'asap', 'immediately'],
            'medical': ['injured', 'hurt', 'bleeding', 'pain', 'sick', 'medical']
        }
        
        message_lower = message.lower()
        
        # Determine basic urgency
        has_critical = any(kw in message_lower for kw in urgency_keywords['critical'])
        has_high = any(kw in message_lower for kw in urgency_keywords['high'])
        has_medical = any(kw in message_lower for kw in urgency_keywords['medical'])
        
        if has_critical:
            urgency_level = UrgencyLevel.CRITICAL
            urgency_score = 0.85
        elif has_high or has_medical:
            urgency_level = UrgencyLevel.HIGH
            urgency_score = 0.65
        else:
            urgency_level = UrgencyLevel.MEDIUM
            urgency_score = 0.50
        
        urgency_factors = UrgencyFactors(
            medical_risk_score=0.7 if has_medical else 0.3,
            medical_risk_explanation="Fallback extraction - keyword-based",
            vulnerable_pop_score=0.5,
            vulnerable_pop_explanation="Unable to determine - fallback mode",
            time_sensitivity_score=0.7 if has_high else 0.5,
            time_sensitivity_explanation="Based on urgency keywords",
            message_confidence_score=0.3,
            message_confidence_explanation="Low confidence - LLM extraction failed",
            severity_score=0.6,
            severity_explanation="Estimated from message content"
        )
        
        return ExtractedInformation(
            needs=[ExtractedNeed(
                need_type=NeedType.OTHER,
                description="Unable to extract specific needs - requires manual review",
                confidence=0.3
            )],
            location=None,
            people_affected=None,
            vulnerable_populations=[],
            urgency_factors=urgency_factors,
            urgency_level=urgency_level,
            urgency_score=urgency_score,
            overall_explanation="Fallback extraction used. Manual review required for accurate triage.",
            extraction_confidence=0.3
        )
