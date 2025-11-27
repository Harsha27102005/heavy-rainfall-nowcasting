# backend/app/api/nowcasting.py
from fastapi import APIRouter, Depends, HTTPException
from app.database import sync_predictions_collection
from app.schemas.prediction import StormCellLocation, NowcastResponse
from datetime import datetime, timedelta
from typing import List
import json

router = APIRouter()

@router.get("/{forecast_time}", response_model=NowcastResponse)
async def get_nowcast_predictions(forecast_time: str):
    """
    Retrieves the latest nowcast predictions for storm cells.
    'forecast_time' can be '30min' or '60min'.
    """
    if forecast_time not in ["30min", "60min"]:
        raise HTTPException(status_code=400, detail="Invalid forecast_time. Use '30min' or '60min'.")

    offset_minutes = 30 if forecast_time == "30min" else 60

    # Fetch the most recent prediction to find the latest timestamp
    latest_prediction = sync_predictions_collection.find_one(
        {"forecast_time": offset_minutes},
        sort=[("predicted_timestamp", -1)]
    )

    if not latest_prediction:
        # If no predictions are found, return an empty response
        return NowcastResponse(
            timestamp=datetime.utcnow(),
            selected_forecast_time=forecast_time,
            predicted_storm_cells=[]
        )

    latest_prediction_time = latest_prediction["predicted_timestamp"]

    # Fetch all storm cell locations made at this latest time for the given forecast_time
    try:
        storm_locations_db = list(sync_predictions_collection.find({
            "predicted_timestamp": latest_prediction_time,
            "forecast_time": offset_minutes
        }))
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching predictions from database.")

    # Convert to the expected format for frontend
    # Convert to the expected format for frontend
    formatted_storm_cells = []
    for location in storm_locations_db:
        # Handle potential field name variations (LLD vs Legacy)
        geojson = location.get("predicted_location") or location.get("predicted_location_geojson")
        mean_rr = location.get("predicted_mean_rain_rate") or location.get("predicted_mean_rr")
        top10_rr = location.get("predicted_top_10_rain_rate") or location.get("predicted_top10_mean_rr")

        # Calculate Impact Risk
        if mean_rr and mean_rr > 16:
            impact_risk = "High"
        elif mean_rr and mean_rr > 5:
            impact_risk = "Medium"
        else:
            impact_risk = "Low"

        formatted_cell = StormCellLocation(
            id=str(location["_id"]),
            cell_id=location["cell_id"],
            mcs_type=location["mcs_type"],
            forecast_time=location["forecast_time"],
            predicted_timestamp=location["predicted_timestamp"],
            predicted_location=geojson,
            predicted_mean_rain_rate=mean_rr,
            predicted_top_10_rain_rate=top10_rr,
            prediction_made_at=location.get("prediction_made_at", location["predicted_timestamp"]),
            impact_risk=impact_risk
        )
        formatted_storm_cells.append(formatted_cell)

    return NowcastResponse(
        timestamp=latest_prediction_time,
        selected_forecast_time=forecast_time,
        predicted_storm_cells=formatted_storm_cells
    )
