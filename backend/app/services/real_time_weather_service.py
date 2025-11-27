#!/usr/bin/env python3
"""
Real-time Weather Monitoring Service
Integrates with weather APIs to provide live radar data for nowcasting
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import numpy as np
from app.database import sync_predictions_collection, sync_warnings_collection
from app.services.notification_service import NotificationService
from app.schemas.prediction import WarningCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Weather data structure for real-time monitoring"""
    timestamp: datetime
    latitude: float
    longitude: float
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    wind_direction: float
    precipitation_rate: float
    radar_reflectivity: Optional[float] = None
    cloud_cover: Optional[float] = None
    visibility: Optional[float] = None

@dataclass
class StormCell:
    """Storm cell detection result"""
    cell_id: str
    center_lat: float
    center_lng: float
    radius_km: float
    intensity: str
    mcs_type: str
    mean_rainfall_rate: float
    max_rainfall_rate: float
    top10_mean_rr: float
    confidence: float

class RealTimeWeatherService:
    """Real-time weather monitoring service"""
    
    def __init__(self):
        # API Configuration
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.weatherapi_key = os.getenv("WEATHERAPI_KEY")
        self.accuweather_api_key = os.getenv("ACCUWEATHER_API_KEY")
        
        # Monitoring configuration
        self.monitoring_interval = int(os.getenv("MONITORING_INTERVAL_SECONDS", "300"))  # 5 minutes
        self.warning_threshold = float(os.getenv("WARNING_THRESHOLD_MMH", "70.0"))  # 70 mm/h
        self.monitoring_active = False
        
        # Geographic bounds for monitoring (Mumbai region)
        self.monitoring_bounds = {
            "min_lat": 18.5,
            "max_lat": 20.0,
            "min_lng": 72.5,
            "max_lng": 73.5
        }
        
        # Notification service
        self.notification_service = NotificationService()
        
        # Session for API calls
        self.session = None
        
    async def start_monitoring(self):
        """Start real-time weather monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
            
        self.monitoring_active = True
        logger.info("Starting real-time weather monitoring...")
        
        # Create session for API calls
        self.session = aiohttp.ClientSession()
        
        try:
            while self.monitoring_active:
                await self.monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
        finally:
            if self.session:
                await self.session.close()
    
    async def stop_monitoring(self):
        """Stop real-time weather monitoring"""
        self.monitoring_active = False
        logger.info("Stopping real-time weather monitoring...")
    
    async def monitoring_cycle(self):
        """Single monitoring cycle"""
        try:
            logger.info(f"Starting monitoring cycle at {datetime.utcnow()}")
            
            # 1. Fetch real-time weather data
            weather_data = await self.fetch_real_time_weather()
            
            if not weather_data:
                logger.warning("No weather data received")
                return
            
            # 2. Analyze for storm cells
            storm_cells = await self.detect_storm_cells(weather_data)
            
            # 3. Generate predictions
            predictions = await self.generate_predictions(storm_cells)
            
            # 4. Check for warnings
            warnings = await self.check_warnings(predictions)
            
            # 5. Send notifications if needed
            if warnings:
                await self.send_warnings(warnings)
            
            # 6. Store data
            await self.store_monitoring_data(weather_data, storm_cells, predictions, warnings)
            
            logger.info(f"Monitoring cycle completed. Found {len(storm_cells)} storm cells, {len(warnings)} warnings")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    async def fetch_real_time_weather(self) -> List[WeatherData]:
        """Fetch real-time weather data from APIs"""
        weather_data = []
        
        # Try multiple APIs for redundancy
        apis_to_try = [
            self.fetch_openweather_data,
            self.fetch_weatherapi_data,
            self.fetch_accuweather_data
        ]
        
        for api_func in apis_to_try:
            try:
                data = await api_func()
                if data:
                    weather_data.extend(data)
                    logger.info(f"Successfully fetched data from {api_func.__name__}")
                    break  # Use first successful API
            except Exception as e:
                logger.warning(f"Failed to fetch from {api_func.__name__}: {e}")
                continue
        
        return weather_data
    
    async def fetch_openweather_data(self) -> List[WeatherData]:
        """Fetch data from OpenWeatherMap API"""
        if not self.openweather_api_key:
            return []
        
        # Grid of points to monitor (Mumbai region)
        lat_points = np.linspace(self.monitoring_bounds["min_lat"], 
                                self.monitoring_bounds["max_lat"], 5)
        lng_points = np.linspace(self.monitoring_bounds["min_lng"], 
                                self.monitoring_bounds["max_lng"], 5)
        
        weather_data = []
        
        for lat in lat_points:
            for lng in lng_points:
                try:
                    url = f"http://api.openweathermap.org/data/2.5/weather"
                    params = {
                        "lat": lat,
                        "lon": lng,
                        "appid": self.openweather_api_key,
                        "units": "metric"
                    }
                    
                    async with self.session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Extract weather data
                            weather = WeatherData(
                                timestamp=datetime.utcnow(),
                                latitude=lat,
                                longitude=lng,
                                temperature=data["main"]["temp"],
                                humidity=data["main"]["humidity"],
                                pressure=data["main"]["pressure"],
                                wind_speed=data["wind"]["speed"],
                                wind_direction=data["wind"]["deg"],
                                precipitation_rate=self.extract_precipitation_rate(data),
                                cloud_cover=data["clouds"]["all"] if "clouds" in data else None,
                                visibility=data["visibility"] if "visibility" in data else None
                            )
                            weather_data.append(weather)
                            
                except Exception as e:
                    logger.warning(f"Error fetching OpenWeather data for {lat}, {lng}: {e}")
                    continue
        
        return weather_data
    
    async def fetch_weatherapi_data(self) -> List[WeatherData]:
        """Fetch data from WeatherAPI.com"""
        if not self.weatherapi_key:
            return []
        
        # Similar implementation for WeatherAPI.com
        # This would use their specific API endpoints
        return []
    
    async def fetch_accuweather_data(self) -> List[WeatherData]:
        """Fetch data from AccuWeather API"""
        if not self.accuweather_api_key:
            return []
        
        # Similar implementation for AccuWeather
        # This would use their specific API endpoints
        return []
    
    def extract_precipitation_rate(self, weather_data: Dict) -> float:
        """Extract precipitation rate from weather data"""
        try:
            # Check for rain data
            if "rain" in weather_data:
                if "1h" in weather_data["rain"]:
                    return weather_data["rain"]["1h"]  # mm/h
                elif "3h" in weather_data["rain"]:
                    return weather_data["rain"]["3h"] / 3  # Convert to mm/h
            
            # Check for snow data
            if "snow" in weather_data:
                if "1h" in weather_data["snow"]:
                    return weather_data["snow"]["1h"] * 0.1  # Convert snow to rain equivalent
                elif "3h" in weather_data["snow"]:
                    return weather_data["snow"]["3h"] * 0.1 / 3
            
            return 0.0
        except Exception:
            return 0.0
    
    async def detect_storm_cells(self, weather_data: List[WeatherData]) -> List[StormCell]:
        """Detect storm cells from weather data"""
        storm_cells = []
        
        if not weather_data:
            return storm_cells
        
        # Group data by proximity to detect storm cells
        cells = self.cluster_weather_data(weather_data)
        
        for i, cell_data in enumerate(cells):
            if len(cell_data) < 3:  # Need minimum data points
                continue
            
            # Calculate cell properties
            center_lat = np.mean([d.latitude for d in cell_data])
            center_lng = np.mean([d.longitude for d in cell_data])
            
            # Calculate rainfall statistics
            rainfall_rates = [d.precipitation_rate for d in cell_data if d.precipitation_rate > 0]
            
            if not rainfall_rates:
                continue
            
            mean_rainfall = np.mean(rainfall_rates)
            max_rainfall = np.max(rainfall_rates)
            
            # Calculate top 10% rainfall
            sorted_rates = sorted(rainfall_rates, reverse=True)
            top10_count = max(1, len(sorted_rates) // 10)
            top10_mean = np.mean(sorted_rates[:top10_count])
            
            # Determine cell type and intensity
            mcs_type = self.classify_storm_cell(mean_rainfall, len(cell_data))
            intensity = self.classify_intensity(mean_rainfall)
            
            # Calculate radius (simplified)
            radius_km = self.calculate_cell_radius(cell_data)
            
            # Calculate confidence based on data quality
            confidence = min(1.0, len(cell_data) / 10.0)
            
            storm_cell = StormCell(
                cell_id=f"REALTIME_CELL_{i:03d}",
                center_lat=center_lat,
                center_lng=center_lng,
                radius_km=radius_km,
                intensity=intensity,
                mcs_type=mcs_type,
                mean_rainfall_rate=mean_rainfall,
                max_rainfall_rate=max_rainfall,
                top10_mean_rr=top10_mean,
                confidence=confidence
            )
            
            storm_cells.append(storm_cell)
        
        return storm_cells
    
    def cluster_weather_data(self, weather_data: List[WeatherData]) -> List[List[WeatherData]]:
        """Cluster weather data points into storm cells"""
        if not weather_data:
            return []
        
        # Simple clustering based on proximity and rainfall
        clusters = []
        used_indices = set()
        
        for i, data in enumerate(weather_data):
            if i in used_indices:
                continue
            
            if data.precipitation_rate < 5.0:  # Skip low rainfall areas
                continue
            
            # Start new cluster
            cluster = [data]
            used_indices.add(i)
            
            # Find nearby points with rainfall
            for j, other_data in enumerate(weather_data):
                if j in used_indices:
                    continue
                
                if other_data.precipitation_rate < 5.0:
                    continue
                
                # Calculate distance
                distance = self.calculate_distance(
                    data.latitude, data.longitude,
                    other_data.latitude, other_data.longitude
                )
                
                if distance < 0.1:  # Within ~10km
                    cluster.append(other_data)
                    used_indices.add(j)
            
            if len(cluster) >= 2:  # Minimum cluster size
                clusters.append(cluster)
        
        return clusters
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in degrees"""
        return np.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2)
    
    def classify_storm_cell(self, mean_rainfall: float, data_points: int) -> str:
        """Classify storm cell type"""
        if mean_rainfall > 100 and data_points > 5:
            return "MCC"  # Mesoscale Convective Complex
        elif mean_rainfall > 50 and data_points > 3:
            return "SLD"  # Squall Line
        else:
            return "CC"   # Convective Cell
    
    def classify_intensity(self, mean_rainfall: float) -> str:
        """Classify rainfall intensity"""
        if mean_rainfall > 100:
            return "very_heavy"
        elif mean_rainfall > 70:
            return "heavy"
        elif mean_rainfall > 30:
            return "moderate"
        else:
            return "light"
    
    def calculate_cell_radius(self, cell_data: List[WeatherData]) -> float:
        """Calculate storm cell radius"""
        if len(cell_data) < 2:
            return 5.0  # Default radius
        
        # Calculate maximum distance between points
        max_distance = 0
        for i, data1 in enumerate(cell_data):
            for data2 in cell_data[i+1:]:
                distance = self.calculate_distance(
                    data1.latitude, data1.longitude,
                    data2.latitude, data2.longitude
                )
                max_distance = max(max_distance, distance)
        
        # Convert to km (rough approximation)
        radius_km = max_distance * 111.0  # 1 degree ≈ 111 km
        return max(5.0, min(50.0, radius_km))  # Clamp between 5-50 km
    
    async def generate_predictions(self, storm_cells: List[StormCell]) -> List[Dict]:
        """Generate nowcasting predictions"""
        predictions = []
        
        for cell in storm_cells:
            # Simple prediction model (in real system, use trained ML models)
            prediction = {
                "cell_id": cell.cell_id,
                "mcs_type": cell.mcs_type,
                "forecast_time": 30,  # 30-minute forecast
                "predicted_timestamp": datetime.utcnow() + timedelta(minutes=30),
                "predicted_mean_rr": cell.mean_rainfall_rate * 0.9,  # Slight decrease
                "predicted_top10_mean_rr": cell.top10_mean_rr * 0.9,
                "confidence": cell.confidence,
                "prediction_made_at": datetime.utcnow()
            }
            predictions.append(prediction)
        
        return predictions
    
    async def check_warnings(self, predictions: List[Dict]) -> List[Dict]:
        """Check if any predictions trigger warnings"""
        warnings = []
        
        for pred in predictions:
            if pred["predicted_top10_mean_rr"] > self.warning_threshold:
                warning = {
                    "cell_id": pred["cell_id"],
                    "mcs_type": pred["mcs_type"],
                    "forecast_time": pred["forecast_time"],
                    "predicted_timestamp": pred["predicted_timestamp"],
                    "predicted_top10_mean_rr": pred["predicted_top10_mean_rr"],
                    "message": self.generate_warning_message(pred),
                    "location_geojson": self.create_warning_geojson(pred),
                    "is_active": True
                }
                warnings.append(warning)
        
        return warnings
    
    def generate_warning_message(self, prediction: Dict) -> str:
        """Generate warning message"""
        intensity = "very heavy" if prediction["predicted_top10_mean_rr"] > 100 else "heavy"
        return f"{intensity.title()} rainfall warning: Expected rainfall intensity of {prediction['predicted_top10_mean_rr']:.1f} mm/h in the next {prediction['forecast_time']} minutes. Risk of flooding and disruption."
    
    def create_warning_geojson(self, prediction: Dict) -> Dict:
        """Create GeoJSON for warning area"""
        # This would use actual storm cell location
        # For now, create a simple polygon
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [72.8, 19.1],
                    [72.8, 18.9],
                    [72.6, 18.9],
                    [72.6, 19.1],
                    [72.8, 19.1]
                ]]
            },
            "properties": {
                "cell_id": prediction["cell_id"],
                "intensity": "high" if prediction["predicted_top10_mean_rr"] > 100 else "moderate"
            }
        }
    
    async def send_warnings(self, warnings: List[Dict]):
        """Send warnings via notification service"""
        for warning_data in warnings:
            try:
                warning = WarningCreate(**warning_data)
                await self.notification_service.send_heavy_rainfall_warning(warning)
                logger.info(f"Warning sent for cell {warning_data['cell_id']}")
            except Exception as e:
                logger.error(f"Failed to send warning: {e}")
    
    async def store_monitoring_data(self, weather_data: List[WeatherData], 
                                  storm_cells: List[StormCell], 
                                  predictions: List[Dict], 
                                  warnings: List[Dict]):
        """Store monitoring data in database"""
        try:
            # Store predictions
            for pred in predictions:
                pred_doc = {
                    **pred,
                    "timestamp": datetime.utcnow(),
                    "source": "real_time_monitoring"
                }
                sync_predictions_collection.insert_one(pred_doc)
            
            # Store warnings
            for warning in warnings:
                warning_doc = {
                    **warning,
                    "issued_at": datetime.utcnow(),
                    "source": "real_time_monitoring"
                }
                sync_warnings_collection.insert_one(warning_doc)
            
            logger.info(f"Stored {len(predictions)} predictions and {len(warnings)} warnings")
            
        except Exception as e:
            logger.error(f"Failed to store monitoring data: {e}")

# Global instance
real_time_service = RealTimeWeatherService()



