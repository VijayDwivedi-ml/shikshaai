from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TeachingRequest(BaseModel):
    """Async request model for teaching resource search"""
    topic: str = Field(..., min_length=2, max_length=100, description="Teaching topic")
    grade: str = Field(..., pattern=r'^(K|1|2|3|4|5|6|7|8|9|10|11|12)$', description="Grade level K-12")
    constraints: List[str] = Field(default=[], description="Optional constraints like 'hands-on', 'digital', 'low-cost'")
    max_resources: int = Field(default=3, ge=1, le=10, description="Maximum resources to return")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "photosynthesis",
                "grade": "7",
                "constraints": ["hands-on", "low-cost"],
                "max_resources": 3
            }
        }

class ResourceRecommendation(BaseModel):
    """Individual resource recommendation"""
    resource: str = Field(..., description="Resource description")
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Score from 0-1")
    reasoning: str = Field(..., description="Why this resource is suitable")
    time_estimate: str = Field(..., description="Estimated time to implement")
    cost_level: str = Field(..., description="low/medium/high cost")
    materials_needed: List[str] = Field(default=[], description="Required materials")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resource": "Leaf chromatography experiment",
                "suitability_score": 0.92,
                "reasoning": "Hands-on, visual, aligns with 7th grade standards",
                "time_estimate": "45 minutes",
                "cost_level": "low",
                "materials_needed": ["leaves", "rubbing alcohol", "coffee filters", "jars"]
            }
        }

class AgentResponse(BaseModel):
    """Async agent response"""
    request_id: str = Field(..., description="Unique request identifier")
    recommendations: List[ResourceRecommendation] = Field(..., description="Resource recommendations")
    agent_notes: str = Field(..., description="Agent's internal notes and reasoning")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    agent_version: str = Field(default="1.0.0", description="Agent version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_12345",
                "recommendations": [],
                "agent_notes": "Generated 5 ideas, filtered to 3 suitable ones",
                "processing_time_ms": 2450.5,
                "agent_version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }