"""
Geocoding Service
Converts location text to coordinates using geocoding APIs
"""
import logging
from typing import Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from app.models.schemas import ExtractedLocation

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding location strings"""
    
    def __init__(self):
        # Use Nominatim (OpenStreetMap) - free but rate-limited
        # For production, consider Google Maps Geocoding API or similar
        self.geolocator = Nominatim(user_agent="emergency-triage-system")
    
    async def geocode(self, location_text: str) -> Optional[ExtractedLocation]:
        """
        Convert location text to coordinates
        
        Args:
            location_text: Raw location string
        
        Returns:
            ExtractedLocation with coordinates if successful, None otherwise
        """
        try:
            logger.info(f"Geocoding location: {location_text}")
            
            # Try to geocode
            location = self.geolocator.geocode(location_text, timeout=5)
            
            if location:
                logger.info(f"Successfully geocoded: {location.address}")
                
                return ExtractedLocation(
                    raw_text=location_text,
                    address=location.address,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    confidence=0.8,  # High confidence for successful geocoding
                    is_geocoded=True
                )
            else:
                logger.warning(f"Could not geocode location: {location_text}")
                return ExtractedLocation(
                    raw_text=location_text,
                    confidence=0.3,  # Low confidence if geocoding failed
                    is_geocoded=False
                )
        
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding error: {e}")
            return ExtractedLocation(
                raw_text=location_text,
                confidence=0.3,
                is_geocoded=False
            )
        
        except Exception as e:
            logger.error(f"Unexpected geocoding error: {e}")
            return None
