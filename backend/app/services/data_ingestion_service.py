# backend/app/services/data_ingestion_service.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.config import settings
from app.services.ml_service import MLModelService
from app.services.notification_service import NotificationService
from app.services.data_preprocessing import (
    get_radar_data, identify_storm_cells, derive_all_variables,
    categorize_storm_cell, generate_image_patch
)
# --- MODIFIED IMPORTS ---
# Remove SQLAlchemy components and import MongoDB collections
from app.database import (
    warnings_collection, 
    predictions_collection,
    # NOTE: You may need to create this collection in your database.py file
    # For now, we'll assume it exists and is named 'storm_cell_locations'
    database 
)
from app.schemas.prediction import WarningCreate, RainfallPredictionCreate, StormCellLocationCreate
from fastapi import HTTPException

# Define the collection for storm cell locations explicitly
storm_cell_locations_collection = database.storm_cell_locations

class DataIngestionService:
    def __init__(self, ml_service: MLModelService, notification_service: NotificationService):
        self.ml_service = ml_service
        self.notification_service = notification_service

    async def process_new_radar_data(self):
        """
        This asynchronous method orchestrates the entire nowcasting process.
        It fetches new radar data, identifies storm cells, makes predictions,
        and issues warnings using MongoDB.
        """
        print(f"\n--- [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting new radar data processing cycle ---")

        # Check if models are trained
        if not self.ml_service.are_models_trained():
            print("Models not trained yet. Skipping prediction cycle.")
            return

        # --- 1. Ingest Latest Radar Data ---
        latest_radar_composite = get_radar_data(settings.LATEST_RADAR_DATA_PATH)
        if latest_radar_composite is None:
            print("No new radar data loaded for processing. Skipping cycle.")
            return

        current_now_timestamp = datetime.utcnow()

        # --- 2. Identify & Process Storm Cells ---
        identified_storm_cells_raw = identify_storm_cells(latest_radar_composite)

        if not identified_storm_cells_raw:
            print("No storm cells identified in the latest radar data. Skipping prediction.")
            return

        for cell_raw_data in identified_storm_cells_raw:
            cell_id = cell_raw_data["id"]
            print(f"Processing storm cell: {cell_id}")

            all_input_features_dict = derive_all_variables(
                storm_cell_data=cell_raw_data,
                radar_composite=latest_radar_composite,
                current_topographic_features=cell_raw_data["current_topographic_features_raw"]
            )
            input_features_df = pd.DataFrame([all_input_features_dict])
            mcs_type = categorize_storm_cell(all_input_features_dict)
            image_patch = generate_image_patch(
                latest_radar_composite,
                cell_raw_data["center_pixel_coords"]
            )

            # --- 3. Loop for 30-min and 60-min forecasts ---
            for forecast_offset_minutes in [30, 60]:
                forecast_time_str = f"{forecast_offset_minutes}min"
                predicted_future_timestamp = current_now_timestamp + timedelta(minutes=forecast_offset_minutes)

                print(f"  -> Forecasting for {cell_id} at {forecast_time_str}")

                # --- 3a. Predict Storm Cell Location ---
                try:
                    is_storm_cell_predicted = self.ml_service.predict_storm_location(
                        image_patch=image_patch,
                        additional_features=input_features_df[settings.RADAR_VARIABLES + settings.TOPOGRAPHIC_VARIABLES],
                        mcs_type=mcs_type,
                        forecast_time=forecast_time_str
                    )
                    print(f"    Storm cell location predicted: {'YES' if is_storm_cell_predicted else 'NO'}")
                except Exception as e:
                    print(f"    Error in storm cell location prediction: {e}. Assuming NO storm cell.")
                    is_storm_cell_predicted = 0

                if not is_storm_cell_predicted:
                    print(f"    No storm cell predicted for {cell_id} in {forecast_time_str}. Skipping rain rate prediction.")
                    continue

                # --- 3b. Predict Rain Rates ---
                predicted_mean_rr, predicted_top10_rr = 0.0, 0.0
                best_regression_model_name = 'ann'
                try:
                    radar_only_features_df = input_features_df[settings.RADAR_VARIABLES]
                    predicted_mean_rr = self.ml_service.predict_rain_rate(
                        input_features=radar_only_features_df, mcs_type=mcs_type, forecast_time=forecast_time_str,
                        rain_rate_type='MeanRR', model_name=best_regression_model_name
                    )
                    predicted_top10_rr = self.ml_service.predict_rain_rate(
                        input_features=radar_only_features_df, mcs_type=mcs_type, forecast_time=forecast_time_str,
                        rain_rate_type='Top10%', model_name=best_regression_model_name
                    )
                    print(f"    Predicted MeanRR: {predicted_mean_rr:.2f} mm/h, Top10%RR: {predicted_top10_rr:.2f} mm/h")
                except Exception as e:
                    print(f"    Error during rain rate prediction: {e}. Skipping warning for this cell/time.")
                    continue

                # --- 4. Issue Early Warnings (MongoDB Logic) ---
                if predicted_top10_rr >= settings.HEAVY_RAINFALL_THRESHOLD_MM_H:
                    warning_message = (
                        f"Heavy rainfall predicted for storm cell '{cell_id}' ({mcs_type} type) "
                        f"in {forecast_offset_minutes} minutes! "
                        f"Predicted Top 10% Mean Rain Rate: {predicted_top10_rr:.2f} mm/h. "
                        f"Expected at: {predicted_future_timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC."
                    )
                    print(f"    *** WARNING ISSUED: {warning_message}")

                    # Check for existing active warning in MongoDB
                    existing_warning_query = {
                        "cell_id": cell_id,
                        "forecast_time": forecast_offset_minutes,
                        "is_active": True,
                        "predicted_timestamp": {
                            "$gte": predicted_future_timestamp - timedelta(minutes=5),
                            "$lte": predicted_future_timestamp + timedelta(minutes=5)
                        }
                    }
                    existing_warning = await warnings_collection.find_one(existing_warning_query)

                    if not existing_warning:
                        new_warning_data = WarningCreate(
                            cell_id=cell_id, mcs_type=mcs_type, forecast_time=forecast_offset_minutes,
                            predicted_timestamp=predicted_future_timestamp,
                            predicted_top10_mean_rr=predicted_top10_rr, message=warning_message,
                            location_geojson={"type": "Polygon", "coordinates": [[[127.0, 36.0], [127.5, 36.0], [127.5, 36.5], [127.0, 36.5], [127.0, 36.0]]]}
                        )
                        # Insert new warning into MongoDB
                        result = await warnings_collection.insert_one(new_warning_data.model_dump())
                        print(f"    Warning stored in DB with ID: {result.inserted_id}")
                        
                        # Trigger notification (removed 'db' argument)
                        await self.notification_service.send_heavy_rainfall_warning(new_warning_data)
                    else:
                        print(f"    Warning for {cell_id} ({forecast_time_str}) already active. Skipping duplicate notification.")
                else:
                    print(f"    Predicted Top10%RR ({predicted_top10_rr:.2f}) below threshold ({settings.HEAVY_RAINFALL_THRESHOLD_MM_H}). No warning.")

                # --- 5. Store Predictions in Database (MongoDB Logic) ---
                # Store StormCellLocation prediction
                storm_loc_data = StormCellLocationCreate(
                    cell_id=cell_id, mcs_type=mcs_type, forecast_time=forecast_offset_minutes,
                    predicted_timestamp=predicted_future_timestamp,
                    predicted_location_json={"type": "Polygon", "coordinates": [[[127.0, 36.0], [127.5, 36.0], [127.5, 36.5], [127.0, 36.5], [127.0, 36.0]]]}
                )
                await storm_cell_locations_collection.insert_one(storm_loc_data.model_dump())

                # Store RainfallPrediction
                rainfall_pred_data = RainfallPredictionCreate(
                    cell_id=cell_id, mcs_type=mcs_type, forecast_time=forecast_offset_minutes,
                    predicted_timestamp=predicted_future_timestamp, predicted_mean_rr=predicted_mean_rr,
                    predicted_top10_mean_rr=predicted_top10_rr
                )
                await predictions_collection.insert_one(rainfall_pred_data.model_dump())
                print(f"    Predictions stored for {cell_id} ({forecast_time_str}).")

        print(f"--- [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] End of radar data processing cycle ---")

