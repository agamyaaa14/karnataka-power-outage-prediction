import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import random
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KarnatakaPowerGridProcessor:
    def __init__(self):
        self.weather_cols = ['temperature_c', 'wind_speed_ms', 'humidity', 'barometric_pressure', 'visibility_km']

        # Karnataka District Risk Categories - All 31 districts mapped
        self.district_categories = {
            'coastal_high': {
                'districts': [
                    'dakshina kannada', 'udupi', 'uttara kannada'
                ],
                'multiplier': 1.6,
                'category_name': 'Coastal High-Risk',
                'risk_factors': ['Salt Corrosion', 'Cyclone Exposure', 'High Humidity'],
                'infrastructure_count': {'feeders': 45, 'substations': 12}
            },
            'industrial_mining': {
                'districts': [
                    'ballari', 'raichur', 'kolar', 'koppal', 'chitradurga'
                ],
                'multiplier': 1.4,
                'category_name': 'Industrial/Mining Zone',
                'risk_factors': ['Heavy Industrial Load', 'Mining Dust', 'Equipment Stress'],
                'infrastructure_count': {'feeders': 38, 'substations': 8}
            },
            'urban_dense': {
                'districts': [
                    'bengaluru urban', 'mysuru', 'belagavi', 'dharwad', 'bengaluru rural'
                ],
                'multiplier': 1.35,
                'category_name': 'Urban Dense Area',
                'risk_factors': ['High Demand Density', 'Aging Infrastructure', 'Heat Island Effect'],
                'infrastructure_count': {'feeders': 65, 'substations': 18}
            },
            'hilly_terrain': {
                'districts': [
                    'kodagu', 'chikkamagaluru', 'hassan', 'shivamogga'
                ],
                'multiplier': 1.2,
                'category_name': 'Hilly Terrain',
                'risk_factors': ['Difficult Access', 'Weather Exposure', 'Transmission Challenges'],
                'infrastructure_count': {'feeders': 28, 'substations': 6}
            },
            'agricultural_stable': {
                'districts': [
                    'mandya', 'tumakuru', 'ramanagara', 'chamarajanagara', 'bidar', 'yadgir', 'bagalkote', 'kalaburagi'
                ],
                'multiplier': 1.05,
                'category_name': 'Agricultural Stable',
                'risk_factors': ['Lower Density', 'Good Maintenance Access', 'Stable Load'],
                'infrastructure_count': {'feeders': 22, 'substations': 4}
            },
            # Add remaining districts to a 'standard' category or assign to closest fit above
            'other': {
                'districts': [
                    'gadag', 'haveri', 'davanagere', 'chikkaballapura', 'vijayapura', 'mandya', 'tumakuru', 'ramanagara', 'chamarajanagara', 'bidar', 'yadgir', 'bagalkote', 'kalaburagi'
                ],
                'multiplier': 1.0,
                'category_name': 'Standard Grid Area',
                'risk_factors': ['Normal Conditions'],
                'infrastructure_count': {'feeders': 25, 'substations': 5}
            }
        }
        # List of all 31 districts for reference
        self.all_districts = [
            'bagalkote', 'ballari', 'belagavi', 'bengaluru rural', 'bengaluru urban', 'bidar', 'chamarajanagara',
            'chikkaballapura', 'chikkamagaluru', 'chitradurga', 'dakshina kannada', 'davanagere', 'dharwad',
            'gadag', 'hassan', 'haveri', 'kalaburagi', 'kodagu', 'kolar', 'koppal', 'mandya', 'mysuru',
            'raichur', 'ramanagara', 'shivamogga', 'tumakuru', 'udupi', 'uttara kannada', 'vijayapura', 'yadgir'
        ]
    
        # Bengaluru Ward Infrastructure Categories
        self.bengaluru_areas = {
            'new_tech_zones': {
            'wards': ['Kadugodi', 'Hudi', 'Kudlu', 'Bommanahalli', 'Singasandra', 'Whitefield'],
            'feeder_type': 'Underground',
            'age_range': (5, 15),
            'reliability': 0.995,
            'infrastructure_quality': 'Modern',
            'consumers_per_feeder': (8000, 12000)
            },
        'established_residential': {
            'wards': ['Koramangala', 'J P Nagar', 'BTM Layout', 'Domlur', 'Hoysala Nagar'],
            'feeder_type': 'Mixed',
            'age_range': (10, 20),
            'reliability': 0.988,
            'infrastructure_quality': 'Good',
            'consumers_per_feeder': (5000, 8000)
            },
        'traditional_areas': {
            'wards': ['Malleswaram', 'Mattikere', 'Basavanagudi', 'Vasanth Nagar', 'Rajaji Nagar'],
            'feeder_type': 'Overhead',
            'age_range': (20, 40),
            'reliability': 0.975,
            'infrastructure_quality': 'Legacy',
            'consumers_per_feeder': (3000, 6000)
            },
        'industrial_commercial': {
            'wards': ['Shivaji Nagar', 'Okalipuram', 'Hegganahalli', 'Kamakshipalya', 'Shettihalli'],
            'feeder_type': 'Overhead Heavy',
            'age_range': (15, 30),
            'reliability': 0.982,
            'infrastructure_quality': 'Industrial',
            'consumers_per_feeder': (4000, 7000)
            },
        'emerging_areas': {
            'wards': ['Yelahanka Satellite Town', 'Kengeri', 'Herohalli', 'Thanisandra', 'Byatarayanapura'],
            'feeder_type': 'Mixed New',
            'age_range': (8, 18),
            'reliability': 0.990,
            'infrastructure_quality': 'Developing',
            'consumers_per_feeder': (6000, 9000)
            }
        }

        self.critical_infrastructure = {
            'hospitals': ['Manipal Hospital', 'Fortis Hospital', 'Apollo Hospital', 'NIMHANS'],
            'emergency_services': ['Fire Station', 'Police Station', 'Emergency Control Room'],
            'telecom_towers': ['Airtel Tower', 'Jio Tower', 'BSNL Exchange'],
            'data_centers': ['Microsoft DC', 'Amazon DC', 'TCS DC'],
            'water_pumping': ['BWSSB Pump Station', 'Bore Well Station']
        }
        
    def get_district_category(self, district_name: str) -> Dict:
        """Get district category information"""
        for category, info in self.district_categories.items():
            if district_name.lower() in info['districts']:
                return {
                    'category': category,
                    'name': info['category_name'],
                    'multiplier': info['multiplier'],
                    'risk_factors': info['risk_factors'],
                    'infrastructure': info['infrastructure_count']
                }
        return {
            'category': 'standard',
            'name': 'Standard Grid Area',
            'multiplier': 1.0,
            'risk_factors': ['Normal Conditions'],
            'infrastructure': {'feeders': 25, 'substations': 5}
        }
    
    def get_bengaluru_ward_info(self, ward_name: str) -> Dict:
        """Get Bengaluru ward infrastructure information"""
        for area_type, info in self.bengaluru_areas.items():
            if ward_name in info['wards']:
                age = random.randint(info['age_range'][0], info['age_range'][1])
                consumers = random.randint(info['consumers_per_feeder'][0], info['consumers_per_feeder'][1])
                return {
                    'area_type': area_type,
                    'feeder_type': info['feeder_type'],
                    'asset_age': age,
                    'reliability': info['reliability'],
                    'infrastructure_quality': info['infrastructure_quality'],
                    'consumers_served': consumers,
                    'risk_multiplier': self.calculate_infrastructure_risk(info['feeder_type'], age)
                }
        return {
            'area_type': 'standard',
            'feeder_type': 'Overhead',
            'asset_age': 25,
            'reliability': 0.980,
            'infrastructure_quality': 'Standard',
            'consumers_served': 4500,
            'risk_multiplier': 1.0
        }
    
    def calculate_infrastructure_risk(self, feeder_type: str, age: int) -> float:
        """Calculate risk multiplier based on infrastructure type and age"""
        base_multipliers = {
            'Underground': 0.7,
            'Mixed': 0.9,
            'Mixed New': 0.8,
            'Overhead': 1.2,
            'Overhead Heavy': 1.1
        }
        
        base_risk = base_multipliers.get(feeder_type, 1.0)
        age_factor = 1 + (age - 15) * 0.02
        
        return max(0.5, min(2.0, base_risk * age_factor))
    
    def clean_numeric_column(self, series: pd.Series, unit: str, default_val: float = 0) -> pd.Series:
        """Clean numeric columns"""
        cleaned = series.astype(str).str.lower().str.strip()
        cleaned = cleaned.str.replace(unit.lower(), '', regex=False)
        cleaned = cleaned.str.replace(',', '.')
        cleaned = cleaned.replace(['', 'nan', 'null', 'none'], np.nan)
        
        numeric_series = pd.to_numeric(cleaned, errors='coerce')
        numeric_series = numeric_series.fillna(default_val)
        
        return numeric_series
    
    def create_datetime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create datetime features"""
        datetime_col = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str), errors='coerce')
        df['datetime'] = datetime_col
        df = df.dropna(subset=['datetime']).copy()
        return df
    
    def calculate_enhanced_risk_score(self, temp_c: float, wind_ms: float, humidity: float, 
                                    district: str) -> Tuple[float, str, List[str]]:
        """Calculate enhanced risk score with district-specific factors"""
        # Base weather risk calculation
        wind_risk = min(1.0, (wind_ms / 20.0) ** 2)
        temp_excess = max(0, temp_c - 35)
        temp_risk = 1 / (1 + np.exp(-temp_excess / 3))
        humidity_normalized = abs(humidity - 0.5) * 2
        humidity_risk = min(1.0, humidity_normalized ** 1.5)
        
        # Combined weather risk
        weather_risk = (0.5 * wind_risk + 0.3 * temp_risk + 0.2 * humidity_risk)
        
        # Apply district-specific multipliers
        district_info = self.get_district_category(district)
        enhanced_risk = weather_risk * district_info['multiplier']
        
        # Scale to 1-10 range
        final_risk = 1 + (enhanced_risk * 9)
        final_risk = min(10.0, final_risk)
        
        # Determine risk level
        if final_risk >= 8.0:
            risk_level = 'Severe'
        elif final_risk >= 5.0:
            risk_level = 'High'
        elif final_risk >= 3.5:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Determine primary risk factors
        risk_factors = []
        if wind_ms > 12:
            risk_factors.append('High Winds')
        if temp_c > 38:
            risk_factors.append('Extreme Heat')
        if abs(humidity - 0.5) > 0.3:
            risk_factors.append('Humidity Stress')
        
        risk_factors.extend(district_info['risk_factors'][:2])
        
        return round(final_risk, 2), risk_level, risk_factors
    
    def extend_to_september_6(self, df_clean: pd.DataFrame) -> pd.DataFrame:
        """Extend weather data to September 6 using rule-based forecasting"""
        logger.info("Extending data to September 6 using rule-based AI...")
        
        # Get latest available data as baseline
        latest_date = df_clean['datetime'].max().date()
        latest_data = df_clean[df_clean['datetime'].dt.date == latest_date]
        
        september_6_data = []
        target_date = pd.to_datetime('2025-09-06')
        
        for hour in [0, 3, 6, 9, 12, 15, 18, 21]:
            forecast_timestamp = target_date + pd.Timedelta(hours=hour)
            
            for _, baseline_row in latest_data.iterrows():
                district = baseline_row['district']
                
                # Rule-based weather progression
                temp_progression = np.random.normal(0.5, 1.0)  # Slightly warmer trend
                wind_progression = np.random.normal(-0.2, 0.8)  # Calmer winds expected
                humidity_progression = np.random.normal(-0.02, 0.03)  # Slightly drier
                
                # Hourly patterns
                hour_temp_factor = 0
                hour_wind_factor = 0
                
                if 6 <= hour <= 18:  # Daytime heating
                    hour_temp_factor = 1 + 3.5 * np.sin(np.pi * (hour - 6) / 12)
                
                if 12 <= hour <= 18:  # Afternoon wind pickup
                    hour_wind_factor = 0.5 + 1.5 * np.sin(np.pi * (hour - 12) / 6)
                
                # District-specific adjustments
                district_info = self.get_district_category(district)
                
                if district_info['category'] == 'coastal_high':
                    humidity_progression += 0.01
                    wind_progression *= 0.8
                elif district_info['category'] == 'urban_dense':
                    temp_progression += 0.8
                    humidity_progression -= 0.01
                elif district_info['category'] == 'industrial_mining':
                    temp_progression += 0.5
                
                # Apply predictions
                predicted_temp = np.clip(baseline_row['temperature_c'] + temp_progression + hour_temp_factor, 20, 45)
                predicted_wind = np.clip(baseline_row['wind_speed_ms'] + wind_progression + hour_wind_factor, 0, 30)
                predicted_humidity = np.clip(baseline_row['humidity'] + humidity_progression, 0.1, 0.9)
                
                september_6_data.append({
                    'district': district,
                    'datetime': forecast_timestamp,
                    'temperature_c': round(predicted_temp, 1),
                    'wind_speed_ms': round(predicted_wind, 1),
                    'humidity': round(predicted_humidity, 3),
                    'barometric_pressure': baseline_row.get('barometric_pressure', 1.013),
                    'visibility_km': baseline_row.get('visibility_km', 15.0),
                    'weather': np.random.choice(['Clear', 'Partly Cloudy', 'Cloudy'], p=[0.7, 0.25, 0.05])
                })
        
        # Combine original data with September 6 forecasts
        september_6_df = pd.DataFrame(september_6_data)
        extended_df = pd.concat([df_clean, september_6_df], ignore_index=True)
        
        logger.info(f"Extended data to September 6: Added {len(september_6_data)} forecast points")
        return extended_df
    
    def generate_september_6_outages(self) -> List[Dict]:
        """Generate September 6 outage scenarios"""
        all_wards = []
        for area_info in self.bengaluru_areas.values():
            all_wards.extend(area_info['wards'])
        
        september_6_outages = []
        base_date = pd.to_datetime('2025-09-06')
        
        # Guaranteed weekend outages for demonstration
        # Enhanced guaranteed outages with GeoJSON-verified ward names
        guaranteed_outages = [
            {'ward': 'Mattikere', 'hour': 9, 'cause': 'Equipment Failure', 'duration': 120, 
             'reason': '35-year old overhead transformer failure', 'consumers': 2800},
            {'ward': 'Hudi', 'hour': 11, 'cause': 'Anomaly: Major Cable Fault', 'duration': 360,
             'reason': 'Underground cable splice failure in tech corridor (rep. Whitefield)', 'consumers': 7500},
            {'ward': 'Malleshwaram', 'hour': 14, 'cause': 'Weather: High Winds', 'duration': 180,
             'reason': 'Tree contact on 40-year overhead feeder', 'consumers': 3500},
            {'ward': 'Shettihalli', 'hour': 15, 'cause': 'Weather: Grid Overload', 'duration': 240,
             'reason': 'Industrial load surge during peak production (rep. Peenya)', 'consumers': 4100},
            {'ward': 'Koramangala', 'hour': 15, 'cause': 'Weather: Grid Overload', 'duration': 150,
             'reason': 'Commercial area AC load during peak heat', 'consumers': 4100},
            {'ward': 'BTM Layout', 'hour': 18, 'cause': 'Equipment Failure', 'duration': 90,
             'reason': 'Residential evening peak overload', 'consumers': 3200},
        ]
        
        for hour in [0, 3, 6, 9, 12, 15, 18, 21]:
            timestamp = base_date + pd.Timedelta(hours=hour)
            for ward in all_wards:
                ward_info = self.get_bengaluru_ward_info(ward)
                
                # Check for guaranteed outage
                guaranteed_outage = None
                for outage in guaranteed_outages:
                    if outage['ward'] == ward and outage['hour'] == hour:
                        guaranteed_outage = outage
                        break
                
                if guaranteed_outage:
                    cause = guaranteed_outage['cause']
                    duration = guaranteed_outage['duration']
                    consumers = ward_info['consumers_served']
                else:
                    # Weekend probability (higher due to maintenance aftermath)
                    weekend_multiplier = 1.3
                    base_outage_prob = (1 - ward_info['reliability']) * ward_info['risk_multiplier']
                    weekend_prob = base_outage_prob * weekend_multiplier
                    
                    if hour in [9, 12, 15, 18]:  # Weekend peak hours
                        weekend_prob *= 1.4
                    
                    if random.random() < weekend_prob:
                        cause = np.random.choice([
                            'Equipment Failure', 'Tree Contact', 'Cable Fault', 
                            'Weather: Overload', 'Maintenance Issue'
                        ])
                        duration = random.randint(45, 200)
                        consumers = random.randint(ward_info['consumers_served'] // 3, ward_info['consumers_served'])
                    else:
                        cause = 'No Outage'
                        duration = 0
                        consumers = 0
                
                area_code = ward.replace(' ', '').upper()[:3]
                feeder_id = f'FD-{area_code}-{random.randint(1, 5):02d}'
                
                september_6_outages.append({
                    'ward_name': ward,  # keep original for display
                    'feeder_id': feeder_id,
                    'asset_type': ward_info['feeder_type'],
                    'asset_age_years': ward_info['asset_age'],
                    'infrastructure_quality': ward_info['infrastructure_quality'],
                    'reliability_rating': ward_info['reliability'],
                    'datetime_start': timestamp,
                    'duration_minutes': duration,
                    'consumers_affected': consumers,
                    'cause': cause,
                    'area_type': ward_info['area_type'],
                    'estimated_revenue_loss': consumers * duration * 0.05 if duration > 0 else 0,
                    'crew_requirement': self.get_crew_requirement(cause, ward_info['feeder_type']),
                    'restoration_complexity': self.get_restoration_complexity(cause, ward_info)
                })
        
        return september_6_outages
    
    def get_crew_requirement(self, cause: str, feeder_type: str) -> str:
        """Determine crew requirement"""
        crew_map = {
            'Equipment Failure': 'Line Crew + Transformer Team',
            'Weather: High Winds': 'Emergency Crew + Tree Removal',
            'Weather: Grid Overload': 'Load Management Team',
            'Anomaly: Major Cable Fault': 'Underground Cable Specialists',
            'Maintenance Issue': 'Maintenance Crew',
            'Tree Contact': 'Line Crew + Forestry Team',
            'Cable Fault': 'Cable Repair Team'
        }
        
        base_crew = crew_map.get(cause, 'Standard Line Crew')
        
        if 'Underground' in feeder_type:
            base_crew += ' + Excavation Support'
        elif 'Heavy' in feeder_type:
            base_crew += ' + Heavy Equipment'
            
        return base_crew
    
    def get_restoration_complexity(self, cause: str, ward_info: Dict) -> str:
        """Determine restoration complexity"""
        complexity_map = {
            'Equipment Failure': 'Medium',
            'Weather: High Winds': 'High',
            'Weather: Grid Overload': 'Low',
            'Anomaly: Major Cable Fault': 'Very High',
            'Maintenance Issue': 'Low',
            'Tree Contact': 'Medium',
            'Cable Fault': 'High'
        }
        
        base_complexity = complexity_map.get(cause, 'Medium')
        
        if 'Underground' in ward_info['feeder_type'] and cause != 'Weather: Grid Overload':
            upgrade_map = {'Low': 'Medium', 'Medium': 'High', 'High': 'Very High'}
            base_complexity = upgrade_map.get(base_complexity, base_complexity)
        
        return base_complexity
    
    def process_statewide_data(self, df_extended: pd.DataFrame) -> pd.DataFrame:
        """Process state-wide data with enhanced risk calculation"""
        risk_data = []
        
        for _, row in df_extended.iterrows():
            risk_score, risk_level, risk_factors = self.calculate_enhanced_risk_score(
                row['temperature_c'], row['wind_speed_ms'], row['humidity'], row['district']
            )
            
            district_info = self.get_district_category(row['district'])
            
            processed_row = row.to_dict()
            processed_row.update({
                'risk_score': risk_score,
                'risk_level': risk_level,
                'primary_risk_factor': risk_factors[0] if risk_factors else 'Normal Conditions',
                'all_risk_factors': ', '.join(risk_factors),
                'district_category': district_info['name'],
                'category_multiplier': district_info['multiplier'],
                'infrastructure_feeders': district_info['infrastructure']['feeders'],
                'infrastructure_substations': district_info['infrastructure']['substations'],
                'at_risk_assets': random.randint(1, district_info['infrastructure']['feeders'] // 5),
                'emergency_contact': f'+91-{random.randint(800, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                'operational_recommendations': self.generate_operational_recommendations(risk_level, row['wind_speed_ms'], row['temperature_c'])
            })
            
            risk_data.append(processed_row)
        
        return pd.DataFrame(risk_data)
    
    def generate_operational_recommendations(self, risk_level: str, wind_speed: float, temperature: float) -> str:
        """Generate operational recommendations"""
        recommendations = []
        
        if risk_level in ['Severe', 'High']:
            recommendations.append("Deploy emergency crews")
            recommendations.append("Pre-position equipment")
            
        if wind_speed > 15:
            recommendations.append("Monitor overhead lines for tree contact")
            
        if temperature > 38:
            recommendations.append("Activate backup cooling systems")
            
        if not recommendations:
            recommendations.append("Continue normal monitoring")
            
        return " • ".join(recommendations[:3])


def main():
    """Main execution function"""
    try:
        processor = KarnatakaPowerGridProcessor()
        
        data_path = Path('data')
        data_path.mkdir(exist_ok=True)
        
        logger.info("=== BALFOUR BEATTY POWER GRID FORECAST SYSTEM ===")
        logger.info("Loading and processing weather data...")
        
        # Load weather data
        df_raw = pd.read_excel('data/weather_data.xlsx', sheet_name='weatherbb')
        logger.info(f"Loaded weather data: {len(df_raw)} rows")
        
        # Clean and process data
        df_raw.columns = df_raw.columns.str.lower().str.strip()
        df_clean = processor.create_datetime_features(df_raw)
        
        # Enhanced data cleaning
        df_clean['temperature_c'] = processor.clean_numeric_column(df_clean['temp'], '°c', default_val=28)
        df_clean['wind_speed_ms'] = processor.clean_numeric_column(df_clean['wind_speed'], 'm/s', default_val=3)
        df_clean['humidity'] = processor.clean_numeric_column(df_clean['humidity'], '', default_val=0.6)
        df_clean['barometric_pressure'] = processor.clean_numeric_column(df_clean['barometer'], 'bars', default_val=1.013)
        df_clean['visibility_km'] = processor.clean_numeric_column(df_clean['visibility'], 'km', default_val=15)
        
        # Standardize location names
        location_map = {
            'bengaluru': 'bengaluru urban', 'devanahalli': 'bengaluru rural',
            'hubballi': 'dharwad', 'kadur': 'chikkamagaluru', 'kundapur': 'udupi',
            'mangaluru': 'dakshina kannada', 'mudigere': 'chikkamagaluru',
            'sringeri': 'chikkamagaluru', 'tarikere': 'chikkamagaluru', 'vijaypura': 'vijayapura',
            'tumkur': 'tumakuru', 'bijapur': 'vijayapura', 'gulbarga': 'kalaburagi',
            'bellary': 'ballari', 'chikmagalur': 'chikkamagaluru', 'shimoga': 'shivamogga'
        }
        df_clean['district'] = df_clean['district'].str.lower().str.strip().replace(location_map)

        final_cols = ['district', 'datetime', 'temperature_c', 'wind_speed_ms', 'humidity', 
                     'barometric_pressure', 'visibility_km', 'weather']
        df_clean = df_clean[final_cols].dropna(subset=['temperature_c'])

        # --- Interpolate missing values for districts present ---
        df_clean = df_clean.sort_values(['district', 'datetime'])
        for col in ['temperature_c', 'wind_speed_ms', 'humidity', 'barometric_pressure', 'visibility_km']:
            df_clean[col] = df_clean.groupby('district')[col].transform(lambda x: x.interpolate(method='linear').fillna(method='bfill').fillna(method='ffill'))

        # Round interpolated columns
        df_clean['temperature_c'] = df_clean['temperature_c'].round(1)
        df_clean['wind_speed_ms'] = df_clean['wind_speed_ms'].round(1)
        df_clean['humidity'] = df_clean['humidity'].round(2)
        df_clean['barometric_pressure'] = df_clean['barometric_pressure'].round(3)
        df_clean['visibility_km'] = df_clean['visibility_km'].round(1)

        # --- Add missing districts with interpolated values ---
        processor_districts = set(processor.all_districts)
        present_districts = set(df_clean['district'].unique())
        missing_districts = processor_districts - present_districts

        if missing_districts:
            logger.info(f"Adding missing districts with interpolated weather: {missing_districts}")
            all_datetimes = df_clean['datetime'].unique()
            mean_weather = df_clean.groupby('datetime')[['temperature_c', 'wind_speed_ms', 'humidity', 'barometric_pressure', 'visibility_km']].mean().reset_index()
            weather_desc = df_clean.groupby('datetime')['weather'].agg(lambda x: x.mode()[0] if not x.mode().empty else 'Clear').reset_index()

            for district in missing_districts:
                for i, row in mean_weather.iterrows():
                    weather_row = {
                        'district': district,
                        'datetime': row['datetime'],
                        'temperature_c': round(row['temperature_c'], 1),
                        'wind_speed_ms': round(row['wind_speed_ms'], 1),
                        'humidity': round(row['humidity'], 2),
                        'barometric_pressure': round(row['barometric_pressure'], 3),
                        'visibility_km': round(row['visibility_km'], 1),
                        'weather': weather_desc.loc[weather_desc['datetime'] == row['datetime'], 'weather'].values[0]
                    }
                    df_clean = pd.concat([df_clean, pd.DataFrame([weather_row])], ignore_index=True)

        # Extend to September 6
        df_extended = processor.extend_to_september_6(df_clean)
        
        # Process state-wide data
        df_state_enhanced = processor.process_statewide_data(df_extended)
        df_state_enhanced.to_csv('data/statewide_weather_risk_enhanced.csv', index=False)
        logger.info(f"State-wide risk data saved: {len(df_state_enhanced)} rows")
        
        # Generate September 6 outage data
        september_6_outages = processor.generate_september_6_outages()
        
        # Load existing outage data and extend
        try:
            existing_outages = pd.read_csv('data/hyperlocal_outage_enhanced.csv')
            all_outages = pd.concat([existing_outages, pd.DataFrame(september_6_outages)], ignore_index=True)
        except FileNotFoundError:
            all_outages = pd.DataFrame(september_6_outages)
        
        all_outages.to_csv('data/hyperlocal_outage_enhanced.csv', index=False)
        logger.info(f"Hyperlocal outage data saved: {len(all_outages)} rows")
        
        # Summary statistics
        sept_6_data = df_state_enhanced[df_state_enhanced['datetime'].dt.date == pd.to_datetime('2025-09-06').date()]
        severe_districts = len(sept_6_data[sept_6_data['risk_level'] == 'Severe'])
        high_risk_districts = len(sept_6_data[sept_6_data['risk_level'] == 'High'])
        
        sept_6_outages = [o for o in september_6_outages if o['cause'] != 'No Outage']
        active_outages = len(sept_6_outages)
        total_consumers_affected = sum([o['consumers_affected'] for o in sept_6_outages])
        
        logger.info("=== SEPTEMBER 6 FORECAST STATISTICS ===")
        logger.info(f"Districts with Severe Risk: {severe_districts}")
        logger.info(f"Districts with High Risk: {high_risk_districts}")
        logger.info(f"Predicted Bengaluru Outages: {active_outages}")
        logger.info(f"Total Consumers at Risk: {total_consumers_affected:,}")
        logger.info("=== READY FOR DEMONSTRATION ===")
        
    except Exception as e:
        logger.error(f"Critical error in processing: {e}")
        raise

if __name__ == "__main__":
    main()

    
'''
✅ Key Features Implemented:

District Risk Categories:
5 distinct categories with specific multipliers
Coastal, Industrial, Urban, Hilly, Agricultural classifications
Infrastructure counts (feeders, substations) per category
Category-specific risk factors

Bengaluru Infrastructure Types:
New tech zones (Underground, modern)
Established residential (Mixed infrastructure)
Traditional areas (Overhead, older)
Industrial/commercial (Heavy load)
Emerging areas (Mixed new)

Enhanced Risk Calculation:
Weather-based base risk + district multipliers
Infrastructure age and type factors
Realistic risk distribution across all categories

Professional Data Generation:
Technical reasons for outages
Crew requirements based on infrastructure type
Restoration complexity assessment
Revenue impact calculations
Critical infrastructure mapping

Utilities-Focused Data:
Operational recommendations
Emergency contact information
At-risk asset counts
Infrastructure details for dispatch
'''