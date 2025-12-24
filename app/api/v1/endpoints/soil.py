"""
Soil analysis endpoints
"""
import os
import uuid
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.core.dependencies import get_repo, get_current_user
from app.repository.postgres import DatabaseRepo
from app.db.models import User, SoilAnalysis
from app.schemas.soil import SoilAnalysisResponse, SoilAnalysisListResponse, UserStatsResponse
from app.services.ml_service import get_ml_service

router = APIRouter()

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def validate_image(file: UploadFile):
    """Validate uploaded image"""
    # Check extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    return file_ext


@router.post("/analyze", response_model=SoilAnalysisResponse)
async def analyze_soil(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    repo: DatabaseRepo = Depends(get_repo)
):
    """
    Analyze soil from uploaded image

    - Uploads image
    - Runs ML model prediction
    - Saves results to database
    - Returns analysis with recommendations
    """
    # Validate image
    file_ext = await validate_image(file)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save uploaded file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Run ML prediction
    try:
        ml_service = get_ml_service()
        prediction = ml_service.predict(str(file_path))
    except Exception as e:
        # Clean up file on prediction failure
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    # Save to database
    try:
        analysis = SoilAnalysis(
            user_id=current_user.id,
            image_filename=file.filename,
            image_path=str(file_path),
            soil_type=prediction.soil_type,
            confidence=prediction.confidence,
            description=prediction.description,
            characteristics=prediction.characteristics,
            recommended_crops=prediction.recommended_crops,
            recommendations=prediction.recommendations,
            created_at=datetime.utcnow()
        )

        await repo.save_soil_analysis(analysis)

        return SoilAnalysisResponse.model_validate(analysis)

    except Exception as e:
        # Clean up file on database failure
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save analysis: {str(e)}")


@router.get("/history", response_model=SoilAnalysisListResponse)
async def get_analysis_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    repo: DatabaseRepo = Depends(get_repo)
):
    """
    Get analysis history for current user

    - limit: Maximum number of results (default: 50)
    - offset: Number of results to skip (default: 0)
    """
    analyses = await repo.get_user_soil_analyses(current_user.id, limit, offset)
    total = await repo.count_user_analyses(current_user.id)

    return SoilAnalysisListResponse(
        analyses=[SoilAnalysisResponse.model_validate(a) for a in analyses],
        total=total
    )


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    repo: DatabaseRepo = Depends(get_repo)
):
    """
    Get user statistics for their soil analyses

    Returns:
    - Total number of analyses
    - Breakdown by soil type
    - Most common soil type
    - Latest analysis date
    """
    from app.schemas.soil import SoilTypeStats
    from collections import Counter

    # Get all user analyses
    analyses = await repo.get_user_soil_analyses(current_user.id, limit=1000, offset=0)
    total = len(analyses)

    if total == 0:
        return UserStatsResponse(
            total_analyses=0,
            soil_types_breakdown=[],
            most_common_type=None,
            latest_analysis_date=None
        )

    # Count soil types
    soil_type_counts = Counter(a.soil_type for a in analyses)

    # Calculate breakdown with percentages
    breakdown = [
        SoilTypeStats(
            soil_type=soil_type,
            count=count,
            percentage=round((count / total) * 100, 1)
        )
        for soil_type, count in soil_type_counts.most_common()
    ]

    # Get most common type
    most_common = soil_type_counts.most_common(1)[0][0] if soil_type_counts else None

    # Get latest analysis date
    latest_date = max(a.created_at for a in analyses) if analyses else None

    return UserStatsResponse(
        total_analyses=total,
        soil_types_breakdown=breakdown,
        most_common_type=most_common,
        latest_analysis_date=latest_date
    )


@router.get("/analysis/{analysis_id}", response_model=SoilAnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    repo: DatabaseRepo = Depends(get_repo)
):
    """Get specific analysis by ID"""
    analysis = await repo.get_soil_analysis_by_id(analysis_id, current_user.id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return SoilAnalysisResponse.model_validate(analysis)


@router.delete("/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    repo: DatabaseRepo = Depends(get_repo)
):
    """Delete analysis and associated image"""
    analysis = await repo.get_soil_analysis_by_id(analysis_id, current_user.id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Delete image file
    image_path = Path(analysis.image_path)
    if image_path.exists():
        try:
            image_path.unlink()
        except Exception:
            pass  # Ignore file deletion errors

    # Delete from database
    success = await repo.delete_soil_analysis(analysis_id, current_user.id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete analysis")

    return {"message": "Analysis deleted successfully"}


@router.get("/image/{analysis_id}")
async def get_analysis_image(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    repo: DatabaseRepo = Depends(get_repo)
):
    """Get the image for a specific analysis"""
    analysis = await repo.get_soil_analysis_by_id(analysis_id, current_user.id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    image_path = Path(analysis.image_path)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")

    return FileResponse(
        image_path,
        media_type="image/jpeg",
        filename=analysis.image_filename
    )
