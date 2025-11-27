# backend/app/services/ml_service.py
import os
import joblib
import tensorflow as tf
from tensorflow import keras
from app.config import settings
import numpy as np
import pandas as pd
from fastapi import HTTPException
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso

class MLModelService:
    def __init__(self):
        self.classification_models = {}
        self.regression_models = {}
        self.scalers = {}
        self.output_scalers = {}
        self.models_trained = False

    def load_models(self):
        print(f"Loading ML models from: {settings.ML_MODELS_DIR}")
        if not os.path.exists(settings.ML_MODELS_DIR):
            os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)
            print(f"Created ML models directory: {settings.ML_MODELS_DIR}")

        models_exist = self._check_models_exist()
        
        if not models_exist:
            print("No trained models found. Models need to be trained first.")
            self.models_trained = False
            return

        # Load classification models
        for mcs_type in settings.MCS_TYPES:
            for forecast_time in ['30min', '60min']:
                model_key = f'{mcs_type}_{forecast_time}'
                model_path = os.path.join(settings.ML_MODELS_DIR, 'classification_model', f'{model_key}_class_model.h5')
                if os.path.exists(model_path):
                    try:
                        self.classification_models[model_key] = keras.models.load_model(model_path)
                        print(f"Loaded classification model: {model_key}")
                    except Exception as e:
                        print(f"Error loading {model_key} CNN model: {e}")

        # Load regression models and scalers
        for mcs_type in settings.MCS_TYPES_REGRESSION:
            for forecast_time in ['30min', '60min']:
                for rain_rate_type in ['MeanRR', 'Top10%']:
                    scaler_key = f'{mcs_type}_{forecast_time}_{rain_rate_type}'
                    scaler_path = os.path.join(settings.ML_MODELS_DIR, 'preprocessing_scalers', f'{scaler_key}_scaler.pkl')
                    output_scaler_path = os.path.join(settings.ML_MODELS_DIR, 'preprocessing_scalers', f'{scaler_key}_output_scaler.pkl')

                    if os.path.exists(scaler_path):
                        self.scalers[scaler_key] = joblib.load(scaler_path)
                    if os.path.exists(output_scaler_path):
                        self.output_scalers[scaler_key] = joblib.load(output_scaler_path)

                    for model_name in ['lasso', 'ann']:
                        model_key_full = f'{scaler_key}_{model_name}'
                        model_file_ext = '.h5' if model_name == 'ann' else '.pkl'
                        model_path = os.path.join(settings.ML_MODELS_DIR, 'regression_models', f'{model_key_full}{model_file_ext}')
                        
                        if os.path.exists(model_path):
                            try:
                                if model_name == 'ann':
                                    self.regression_models[model_key_full] = keras.models.load_model(model_path)
                                else:
                                    self.regression_models[model_key_full] = joblib.load(model_path)
                                print(f"Loaded regression model: {model_key_full}")
                            except Exception as e:
                                print(f"Error loading {model_key_full} regression model: {e}")

        if self.classification_models or self.regression_models:
            self.models_trained = True
            print("ML Model loading complete.")
        else:
            self.models_trained = False
            print("No models could be loaded.")

    def _check_models_exist(self):
        classification_dir = os.path.join(settings.ML_MODELS_DIR, 'classification_model')
        regression_dir = os.path.join(settings.ML_MODELS_DIR, 'regression_models')
        
        if os.path.exists(classification_dir) and any(f.endswith('.h5') for f in os.listdir(classification_dir)):
            return True
        
        if os.path.exists(regression_dir) and any(f.endswith(('.h5', '.pkl')) for f in os.listdir(regression_dir)):
            return True
        
        return False

    def _load_and_preprocess_data(self, radar_data_paths, labels_data_paths):
        print("Loading and preprocessing data...")
        
        radar_df = pd.concat([pd.read_csv(p) for p in radar_data_paths])
        labels_df = pd.concat([pd.read_csv(p) for p in labels_data_paths])
        
        print(f"Radar data shape: {radar_df.shape}")
        print(f"Labels data shape: {labels_df.shape}")
        print(f"Radar columns: {radar_df.columns.tolist()}")
        print(f"Labels columns: {labels_df.columns.tolist()}")
        
        # Merge dataframes on cell_id
        merged_df = pd.merge(radar_df, labels_df, on='cell_id', suffixes=('', '_label'))
        
        print(f"Merged data shape: {merged_df.shape}")
        print(f"Merged columns: {merged_df.columns.tolist()}")
        
        # Feature selection and engineering
        features = settings.RADAR_VARIABLES
        target_classification = 'is_heavy_rainfall'
        target_regression_mean = 'mean_rainfall_rate_mmh'
        target_regression_top10 = 'top10_mean_rr_mmh'

        # Check if columns exist
        missing_features = [f for f in features if f not in merged_df.columns]
        if missing_features:
            print(f"WARNING: Missing features: {missing_features}")
            # Use only available features
            features = [f for f in features if f in merged_df.columns]
        
        # Extract data
        X = merged_df[features]
        y_class = merged_df[target_classification]
        y_reg_mean = merged_df[target_regression_mean]
        y_reg_top10 = merged_df[target_regression_top10]
        
        # Clean data: handle NaN and infinite values
        print(f"Checking for NaN values...")
        print(f"  X NaN count: {X.isna().sum().sum()}")
        print(f"  y_class NaN count: {y_class.isna().sum()}")
        print(f"  y_reg_mean NaN count: {y_reg_mean.isna().sum()}")
        print(f"  y_reg_top10 NaN count: {y_reg_top10.isna().sum()}")
        
        # Fill NaN values with column mean (for features) or 0 (for targets)
        X = X.fillna(X.mean())
        y_class = y_class.fillna(0)
        y_reg_mean = y_reg_mean.fillna(0)
        y_reg_top10 = y_reg_top10.fillna(0)
        
        # Replace infinite values with large finite values
        X = X.replace([np.inf, -np.inf], np.nan).fillna(X.mean())
        y_reg_mean = y_reg_mean.replace([np.inf, -np.inf], 0)
        y_reg_top10 = y_reg_top10.replace([np.inf, -np.inf], 0)
        
        print(f"After cleaning:")
        print(f"  X shape: {X.shape}")
        print(f"  X NaN count: {X.isna().sum().sum()}")
        
        # Use mcs_type from radar data (no suffix)
        mcs_type_col = 'mcs_type' if 'mcs_type' in merged_df.columns else 'mcs_type_label'
        
        return X, y_class, y_reg_mean, y_reg_top10, merged_df[mcs_type_col]


    def train_models(self, radar_data_paths, labels_data_paths):
        print("Starting real model training...")

        X, y_class, y_reg_mean, y_reg_top10, mcs_types = self._load_and_preprocess_data(radar_data_paths, labels_data_paths)

        # Create directories
        os.makedirs(os.path.join(settings.ML_MODELS_DIR, 'classification_model'), exist_ok=True)
        os.makedirs(os.path.join(settings.ML_MODELS_DIR, 'regression_models'), exist_ok=True)
        os.makedirs(os.path.join(settings.ML_MODELS_DIR, 'preprocessing_scalers'), exist_ok=True)

        # Train classification models
        for mcs_type in settings.MCS_TYPES:
            for forecast_time in ['30min', '60min']:
                model_key = f'{mcs_type}_{forecast_time}'
                
                # Check if we have data for this MCS type
                mcs_mask = mcs_types == mcs_type
                if mcs_mask.sum() == 0:
                    print(f"⚠️  Skipping {model_key} - no data for MCS type '{mcs_type}'")
                    continue
                
                print(f"Training classification model for {model_key}...")
                print(f"  Samples for {mcs_type}: {mcs_mask.sum()}")

                # Check if we have enough samples for train/test split
                if mcs_mask.sum() < 5:
                    print(f"⚠️  Skipping {model_key} - insufficient data (need at least 5 samples, have {mcs_mask.sum()})")
                    continue

                X_train, X_test, y_train, y_test = train_test_split(
                    X[mcs_mask], y_class[mcs_mask], test_size=0.2, random_state=42
                )

                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                
                # Save scaler
                scaler_path = os.path.join(settings.ML_MODELS_DIR, 'preprocessing_scalers', f'{model_key}_class_scaler.pkl')
                joblib.dump(scaler, scaler_path)

                # Reshape for 1D CNN: (samples, features, 1)
                X_train_reshaped = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))

                # 1D CNN Model for Classification
                model = keras.Sequential([
                    keras.layers.Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=(X_train_scaled.shape[1], 1)),
                    keras.layers.MaxPooling1D(pool_size=2),
                    keras.layers.Conv1D(filters=64, kernel_size=3, activation='relu'),
                    keras.layers.GlobalMaxPooling1D(),
                    keras.layers.Dense(64, activation='relu'),
                    keras.layers.Dropout(0.3),
                    keras.layers.Dense(1, activation='sigmoid')
                ])
                
                model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
                # Use X_train_reshaped
                model.fit(X_train_reshaped, y_train, epochs=20, batch_size=32, validation_split=0.2, verbose=1)
                
                model_path = os.path.join(settings.ML_MODELS_DIR, 'classification_model', f'{model_key}_class_model.h5')
                model.save(model_path)
                self.classification_models[model_key] = model

        # Train regression models
        for mcs_type in settings.MCS_TYPES_REGRESSION:
            for forecast_time in ['30min', '60min']:
                for rain_rate_type, y_reg in [('MeanRR', y_reg_mean), ('Top10%', y_reg_top10)]:
                    scaler_key = f'{mcs_type}_{forecast_time}_{rain_rate_type}'
                    
                    # Check if we have data for this MCS type
                    mcs_mask = mcs_types == mcs_type
                    if mcs_mask.sum() == 0:
                        print(f"⚠️  Skipping {scaler_key} - no data for MCS type '{mcs_type}'")
                        continue
                    
                    print(f"Training regression models for {scaler_key}...")
                    print(f"  Samples for {mcs_type}: {mcs_mask.sum()}")
                    
                    # Check if we have enough samples
                    if mcs_mask.sum() < 5:
                        print(f"⚠️  Skipping {scaler_key} - insufficient data (need at least 5 samples, have {mcs_mask.sum()})")
                        continue

                    X_train, X_test, y_train, y_test = train_test_split(
                        X[mcs_mask], y_reg[mcs_mask], test_size=0.2, random_state=42
                    )

                    # Input scaler
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    scaler_path = os.path.join(settings.ML_MODELS_DIR, 'preprocessing_scalers', f'{scaler_key}_scaler.pkl')
                    joblib.dump(scaler, scaler_path)
                    self.scalers[scaler_key] = scaler

                    # Output scaler
                    output_scaler = StandardScaler()
                    y_train_scaled = output_scaler.fit_transform(y_train.values.reshape(-1, 1))
                    output_scaler_path = os.path.join(settings.ML_MODELS_DIR, 'preprocessing_scalers', f'{scaler_key}_output_scaler.pkl')
                    joblib.dump(output_scaler, output_scaler_path)
                    self.output_scalers[scaler_key] = output_scaler

                    # Lasso model
                    lasso = Lasso(alpha=0.1)
                    lasso.fit(X_train_scaled, y_train_scaled.ravel())
                    model_path_lasso = os.path.join(settings.ML_MODELS_DIR, 'regression_models', f'{scaler_key}_lasso.pkl')
                    joblib.dump(lasso, model_path_lasso)
                    self.regression_models[f'{scaler_key}_lasso'] = lasso

                    # Deep ANN model for Regression
                    ann_model = keras.Sequential([
                        keras.layers.Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
                        keras.layers.Dropout(0.3),
                        keras.layers.Dense(64, activation='relu'),
                        keras.layers.Dropout(0.2),
                        keras.layers.Dense(32, activation='relu'),
                        keras.layers.Dense(1)
                    ])
                    ann_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
                    ann_model.fit(X_train_scaled, y_train_scaled, epochs=30, batch_size=32, validation_split=0.2, verbose=1)
                    model_path_ann = os.path.join(settings.ML_MODELS_DIR, 'regression_models', f'{scaler_key}_ann.h5')
                    ann_model.save(model_path_ann)
                    self.regression_models[f'{scaler_key}_ann'] = ann_model

        print("Real model training completed.")
        self.models_trained = True
        return True

    def predict_storm_location(self, additional_features: pd.DataFrame, mcs_type: str, forecast_time: str) -> int:
        if not self.models_trained:
            raise HTTPException(status_code=400, detail="Models not trained yet.")
        
        model_key = f'{mcs_type}_{forecast_time}'
        model = self.classification_models.get(model_key)
        if model is None:
            raise HTTPException(status_code=400, detail=f"Classification model for {model_key} not loaded.")

        scaler_path = os.path.join(settings.ML_MODELS_DIR, 'preprocessing_scalers', f'{model_key}_class_scaler.pkl')
        if not os.path.exists(scaler_path):
            raise HTTPException(status_code=500, detail=f"Scaler for {model_key} not found.")
        
        scaler = joblib.load(scaler_path)
        features_scaled = scaler.transform(additional_features)
        
        # Reshape for 1D CNN: (samples, features, 1)
        features_reshaped = features_scaled.reshape((features_scaled.shape[0], features_scaled.shape[1], 1))
        
        prediction = model.predict(features_reshaped)
        return int(prediction[0][0] >= 0.5)

    def predict_rain_rate(self, input_features: pd.DataFrame, mcs_type: str, forecast_time: str, rain_rate_type: str, model_name: str) -> float:
        if not self.models_trained:
            raise HTTPException(status_code=400, detail="Models not trained yet.")
            
        model_key_full = f'{mcs_type}_{forecast_time}_{rain_rate_type}_{model_name}'
        model = self.regression_models.get(model_key_full)
        scaler_key = f'{mcs_type}_{forecast_time}_{rain_rate_type}'

        if model is None:
            raise HTTPException(status_code=400, detail=f"Regression model for {model_key_full} not loaded.")

        scaler = self.scalers.get(scaler_key)
        output_scaler = self.output_scalers.get(scaler_key)

        if scaler is None or output_scaler is None:
            raise HTTPException(status_code=500, detail=f"Scalers for {scaler_key} not found.")

        processed_features = scaler.transform(input_features)
        
        prediction_scaled = model.predict(processed_features)
        final_prediction = output_scaler.inverse_transform(prediction_scaled.reshape(-1, 1))[0][0]
        return float(final_prediction)

    def are_models_trained(self) -> bool:
        return self.models_trained
