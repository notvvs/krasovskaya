from pydantic import BaseModel
from datetime import datetime


class SoilAnalysisResponse(BaseModel):
    """Response schema for soil analysis"""
    id: int
    user_id: int
    image_filename: str
    image_path: str
    soil_type: str
    confidence: float
    description: str
    characteristics: str
    recommended_crops: str
    recommendations: str
    created_at: datetime

    class Config:
        from_attributes = True


class SoilAnalysisListResponse(BaseModel):
    """Response schema for list of soil analyses"""
    analyses: list[SoilAnalysisResponse]
    total: int


class SoilPrediction(BaseModel):
    """Schema for ML model prediction"""
    soil_type: str
    confidence: float
    description: str
    characteristics: str
    recommended_crops: str
    recommendations: str


class SoilTypeStats(BaseModel):
    """Statistics for a specific soil type"""
    soil_type: str
    count: int
    percentage: float


class UserStatsResponse(BaseModel):
    """User statistics response"""
    total_analyses: int
    soil_types_breakdown: list[SoilTypeStats]
    most_common_type: str | None
    latest_analysis_date: datetime | None
