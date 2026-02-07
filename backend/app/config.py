"""
Configuration management for the Emergency Crisis Triage System
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "emergency_triage"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "openai"  # "openai" or "anthropic"
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000
    
    # System Configuration
    max_workers: int = 4
    request_timeout: int = 30
    
    # Urgency Scoring Weights (must sum to 1.0)
    weight_medical_risk: float = 0.35
    weight_vulnerable_pop: float = 0.25
    weight_time_sensitivity: float = 0.20
    weight_message_confidence: float = 0.10
    weight_severity: float = 0.10
    
    # Resource Matching Weights (must sum to 1.0)
    weight_suitability: float = 0.40
    weight_availability: float = 0.30
    weight_capacity: float = 0.15
    weight_distance: float = 0.15
    
    # AI-Enhanced Resource Matching
    enable_ai_matching: bool = False  # Enable LLM-enhanced resource matching
    ai_matching_min_confidence: float = 0.6  # Minimum confidence to use AI matching
    
    # Security
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def validate_weights():
    """Validate that scoring weights sum to 1.0"""
    urgency_sum = (
        settings.weight_medical_risk +
        settings.weight_vulnerable_pop +
        settings.weight_time_sensitivity +
        settings.weight_message_confidence +
        settings.weight_severity
    )
    
    resource_sum = (
        settings.weight_suitability +
        settings.weight_availability +
        settings.weight_capacity +
        settings.weight_distance
    )
    
    if abs(urgency_sum - 1.0) > 0.01:
        raise ValueError(f"Urgency weights must sum to 1.0, got {urgency_sum}")
    
    if abs(resource_sum - 1.0) > 0.01:
        raise ValueError(f"Resource weights must sum to 1.0, got {resource_sum}")


# Validate on import
validate_weights()
