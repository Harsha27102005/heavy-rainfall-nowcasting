from fastapi import APIRouter, HTTPException, status
from app.database import crowdsource_reports_collection
from app.models.crowdsource import CrowdsourceReport
from app.schemas.crowdsource import ReportCreate, ReportResponse
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/report", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate):
    new_report = CrowdsourceReport(
        location=report.location,
        intensity=report.intensity,
        description=report.description,
        timestamp=datetime.utcnow(),
        status="pending"
    )
    
    report_dict = new_report.dict()
    result = await crowdsource_reports_collection.insert_one(report_dict)
    
    return ReportResponse(
        id=str(result.inserted_id),
        **report_dict
    )

@router.get("/reports", response_model=list[ReportResponse])
async def get_reports():
    reports = []
    cursor = crowdsource_reports_collection.find().sort("timestamp", -1).limit(50)
    async for document in cursor:
        document["id"] = str(document["_id"])
        reports.append(ReportResponse(**document))
    return reports
