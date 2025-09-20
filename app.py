import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path
import numpy as np
import re

st.set_page_config(
    page_title="Balfour Beatty - Power Grid Monitor",
    page_icon="⚡",
    layout="wide"
)

# Session states
if 'user_type' not in st.session_state:
    st.session_state.user_type = 'Utilities'

# Clean styling
st.markdown("""
<style>
    .stApp {
        background: #f8fafc;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .kpi-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        flex: 1;
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1e40af;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f2937;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0.25rem 0 0 0;
        text-transform: uppercase;
        font-weight: 500;
    }
    .alert-utilities { 
        background: linear-gradient(135deg, #60a5fa, #3730a3 80%);
        color: white; 
        border: none;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 1rem;
        border-radius: 8px;
    }
    .alert-citizens { 
        background: linear-gradient(135deg, #f87171, #b91c1c 80%);
        color: white; 
        border: none;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 1rem;
        border-radius: 8px;
    }
    .alert-success { 
        background: linear-gradient(135deg, #34d399, #047857 80%);
        color: white; 
        border: none;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 1rem;
        border-radius: 8px;
    }
    .alert-citizens ul,
    .alert-utilities ul,
    .alert-success ul {
        margin: 0.5rem 0 0 1.5rem;
        padding: 0;
    }
    .alert-citizens li,
    .alert-utilities li,
    .alert-success li {
        margin-bottom: 0.5rem;
    }
    .risk-severe { border-left-color: #dc2626 !important; }
    .risk-high { border-left-color: #d97706 !important; }
    .risk-medium { border-left-color: #fbbf24 !important; }
    .risk-low { border-left-color: #0b43e0 !important; }

    .legend-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1rem 0;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .legend-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2px solid white;
    }
    .legend-low { background-color: #0b43e0; }
    .legend-medium { background-color: #fbbf24; }
    .legend-high { background-color: #d97706; }
    .legend-severe { background-color: #dc2626; }
    .legend-normal { background-color: #4450f9; }
    .legend-outage { background-color: #dc2626; }
</style>
""", unsafe_allow_html=True)

# Data loading
@st.cache_data
def load_data():
    try:
        state_data = pd.read_csv('data/statewide_weather_risk_enhanced.csv')
        outage_data = pd.read_csv('data/hyperlocal_outage_enhanced.csv')
        
        state_data['datetime'] = pd.to_datetime(state_data['datetime'])
        outage_data['datetime_start'] = pd.to_datetime(outage_data['datetime_start'])
        
        target_date = pd.to_datetime('2025-09-06').date()
        state_data = state_data[state_data['datetime'].dt.date == target_date]
        outage_data = outage_data[outage_data['datetime_start'].dt.date == target_date]
        
        return state_data, outage_data
    except FileNotFoundError as e:
        st.error(f"Data files not found: {e}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data
def load_geospatial():
    try:
        with open('data/karnataka_districts.geojson', 'r') as f:
            karnataka_geojson = json.load(f)
        try:
            with open('data/bengaluru_wards.geojson', 'r') as f:
                bengaluru_geojson = json.load(f)
        except FileNotFoundError:
            st.warning("bengaluru_wards.geojson not found.")
            bengaluru_geojson = None
        return karnataka_geojson, bengaluru_geojson
    except FileNotFoundError:
        st.error("karnataka_districts.geojson not found in data/ folder.")
        return None, None

state_data, outage_data = load_data()
karnataka_geojson, bengaluru_geojson = load_geospatial()

if state_data.empty or outage_data.empty or not karnataka_geojson:
    st.stop()

# Header
st.markdown("""
<div class="main-header">
    <h1>BALFOUR BEATTY POWER GRID MONITOR</h1>
    <p style="margin: 0; opacity: 0.9;">September 6, 2025 - Real-time Infrastructure Monitoring</p>
</div>
""", unsafe_allow_html=True)

# SIDEBAR CONTROLS
st.sidebar.header("Dashboard Controls")

current_view = 'Operations Center' if st.session_state.user_type == 'Utilities' else 'Public Information'
st.sidebar.info(f"**Current Mode:** {current_view}")

user_label = "Switch to Citizens View" if st.session_state.user_type == 'Utilities' else "Switch to Utilities View"
if st.sidebar.button(user_label):
    st.session_state.user_type = 'Citizens' if st.session_state.user_type == 'Utilities' else 'Utilities'
    st.rerun()

analysis_type = st.sidebar.radio(
    "Select Analysis:",
    ['Karnataka State Analysis', 'Bengaluru City Analysis'],
    key="analysis_radio"
)

st.sidebar.subheader("Time Selection")
st.sidebar.info("**Date:** September 6, 2025")

selected_hour = st.sidebar.select_slider(
    "Select Hour:",
    options=[0, 3, 6, 9, 12, 15, 18, 21],
    value=12,
    format_func=lambda x: f"{x:02d}:00"
)

selected_datetime = pd.to_datetime(f"2025-09-06 {selected_hour:02d}:00:00")
st.sidebar.success(f"**Time:** {selected_datetime.strftime('%I:%M %p')}")

state_at_time = state_data[state_data['datetime'].dt.hour == selected_hour]
outages_at_time = outage_data[outage_data['datetime_start'].dt.hour == selected_hour]

def format_state_tooltip(row, user_type):
    district = row['district'].replace('_', ' ').title()
    if user_type == 'Utilities':
        return (f"<b>{district}</b><br>"
               f"Risk Level: {row['risk_level']} ({row['risk_score']:.1f}/10)<br>"
               f"Temperature: {row['temperature_c']:.1f}°C<br>"
               f"Wind Speed: {row['wind_speed_ms']:.1f} m/s<br>"
               f"Infrastructure: {row.get('infrastructure_feeders', 'N/A')} feeders<br>"
               f"Primary Factor: {row.get('primary_risk_factor', 'Normal')}")
    else:
        if row['risk_level'] in ['Severe', 'High']:
            return (f"<b>{district}</b><br>"
                   f"Alert Level: {row['risk_level']}<br>"
                   f"Action Required: Prepare for power outages<br>"
                   f"Estimated Duration: 2-6 hours<br>"
                   f"Emergency Helpline: 1912")
        else:
            return (f"<b>{district}</b><br>"
                   f"Status: Normal operations expected<br>"
                   f"No special preparation required<br>"
                   f"Report Issues: 1912")

def format_outage_tooltip(row, user_type):
    ward = row['ward_name']
    if row['cause'] != 'No Outage':
        if user_type == 'Utilities':
            return (f"<b>{ward} - ACTIVE OUTAGE</b><br>"
                   f"Cause: {row['cause']}<br>"
                   f"Duration: {row['duration_minutes']} minutes<br>"
                   f"Consumers Affected: {row['consumers_affected']:,}<br>"
                   f"Feeder ID: {row.get('feeder_id', 'N/A')}<br>"
                   f"Crew Required: {row.get('crew_requirement', 'Standard crew')}")
        else:
            return (f"<b>{ward}</b><br>"
                   f"Power supply is interrupted in this area.<br>"
                   f"Estimated restoration time: {row['duration_minutes']} minutes.<br>"
                   f"People affected: {row['consumers_affected']:,}<br>"
                   f"Avoid using elevators, keep your mobile charged, and stay updated via local news.<br>"
                   f"Emergency services: 1912 (Electricity), 108 (Ambulance), 100 (Police), 101 (Fire)")
    else:
        return (f"<b>{ward}</b><br>"
               f"Power supply is normal.<br>"
               f"No outages reported.<br>"
               f"All services are working.")

# STATE ANALYSIS
if 'Karnataka State Analysis' in analysis_type:
    st.header("Karnataka State Risk Assessment")
    st.subheader(f"Forecast: {selected_datetime.strftime('%B %d, %Y at %I:%M %p')}")
    
    if not state_at_time.empty:
        unique_districts = state_at_time.drop_duplicates(subset=['district'])
        
        severe = len(unique_districts[unique_districts['risk_level'] == 'Severe'])
        high = len(unique_districts[unique_districts['risk_level'] == 'High'])
        medium = len(unique_districts[unique_districts['risk_level'] == 'Medium'])
        low = len(unique_districts[unique_districts['risk_level'] == 'Low'])
        
        # Display KPIs
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card risk-severe">
                <p class="kpi-value">{severe}</p>
                <p class="kpi-label">Severe Risk</p>
            </div>
            <div class="kpi-card risk-high">
                <p class="kpi-value">{high}</p>
                <p class="kpi-label">High Risk</p>
            </div>
            <div class="kpi-card risk-medium">
                <p class="kpi-value">{medium}</p>
                <p class="kpi-label">Medium Risk</p>
            </div>
            <div class="kpi-card risk-low">
                <p class="kpi-value">{low}</p>
                <p class="kpi-label">Low Risk</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Karnataka Map
        st.markdown("### Karnataka Districts Risk Map")
        
        st.markdown("""
        <div class="legend-container">
            <div class="legend-item">
                <div class="legend-dot legend-low"></div>
                <span>Low Risk</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot legend-medium"></div>
                <span>Medium Risk</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot legend-high"></div>
                <span>High Risk</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot legend-severe"></div>
                <span>Severe Risk</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        district_risk_map = {}
        hover_map = {}
        
        for _, row in unique_districts.iterrows():
            district_key = row['district'].replace('_', ' ').title()
            risk_level_mapping = {
                'Low': 0,
                'Medium': 1,  
                'High': 2,
                'Severe': 3
            }
            district_risk_map[district_key] = risk_level_mapping.get(row['risk_level'], 0)
            hover_map[district_key] = format_state_tooltip(row, st.session_state.user_type)
        
        locations = []
        risk_categories = []
        hover_texts = []
        
        for feature in karnataka_geojson['features']:
            district_name = feature['properties']['district']
            locations.append(district_name)
            
            if district_name in district_risk_map:
                risk_categories.append(district_risk_map[district_name])
                hover_texts.append(hover_map[district_name])
            else:
                risk_categories.append(0)
                hover_texts.append(f"<b>{district_name}</b><br>No data available")
        
        fig = go.Figure(go.Choropleth(
            geojson=karnataka_geojson,
            locations=locations,
            z=risk_categories,
            featureidkey="properties.district",
            colorscale=[
                [0.0, '#0b43e0'],
                [0.33, '#fbbf24'],
                [0.67, '#d97706'],
                [1.0, '#dc2626']
            ],
            zmin=0,
            zmax=3,
            showscale=True,
            colorbar=dict(
                title="Risk Level",
                tickvals=[0, 1, 2, 3],
                ticktext=["Low", "Medium", "High", "Severe"],
                len=0.7
            ),
            hovertext=hover_texts,
            hovertemplate='%{hovertext}<extra></extra>',
            marker_line_color='white',
            marker_line_width=0.8
        ))
        
        fig.update_geos(
            projection_type="mercator",
            fitbounds="geojson", 
            visible=False
        )
        
        fig.update_layout(
            height=500,
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # FIXED: Alert messages as bullet points
        total_high_risk = severe + high
        if total_high_risk > 0:
            alert_class = f"alert-{st.session_state.user_type.lower()}"
            
            if st.session_state.user_type == 'Utilities':
                msg = (
                    f"<b>Operations Alert:</b> {total_high_risk} districts require immediate attention.<br>"
                    f"<ul>"
                    f"<li>Deploy emergency response teams to affected areas</li>"
                    f"<li>Monitor critical infrastructure closely</li>"
                    f"<li>Coordinate with local utility teams</li>"
                    f"<li>Prepare backup power systems</li>"
                    f"</ul>"
                )
            else:
                msg = (
                    f"<b>Public Alert:</b> {total_high_risk} districts may experience power disruptions.<br>"
                    f"<ul>"
                    f"<li>Charge electronic devices immediately</li>"
                    f"<li>Prepare emergency supplies (flashlights, water, food)</li>"
                    f"<li>Avoid using elevators during outages</li>"
                    f"<li>Keep emergency contact numbers ready</li>"
                    f"</ul>"
                )
            
            st.markdown(f'<div class="{alert_class}">{msg}</div>', unsafe_allow_html=True)
            
            # High Priority Districts Table
            st.markdown("### High Priority Districts")
            
            high_risk_districts = unique_districts[unique_districts['risk_level'].isin(['Severe', 'High'])].copy()
            
            if not high_risk_districts.empty:
                high_risk_districts['District'] = high_risk_districts['district'].str.replace('_', ' ').str.title()
                high_risk_districts['Risk Score'] = high_risk_districts['risk_score'].round(2)
                high_risk_districts['Risk Level'] = high_risk_districts['risk_level']
                high_risk_districts['Primary Reason'] = high_risk_districts['primary_risk_factor']
                high_risk_districts['Weather'] = (high_risk_districts['temperature_c'].round(1).astype(str) + '°C, ' + 
                                                 high_risk_districts['wind_speed_ms'].round(1).astype(str) + ' m/s')
                
                display_cols = ['District', 'Risk Level', 'Risk Score', 'Weather', 'Primary Reason']
                
                if st.session_state.user_type == 'Utilities':
                    high_risk_districts['Infrastructure'] = (high_risk_districts['infrastructure_feeders'].astype(str) + ' feeders, ' +
                                                           high_risk_districts['infrastructure_substations'].astype(str) + ' substations')
                    display_cols.append('Infrastructure')
                
                st.dataframe(
                    high_risk_districts[display_cols].sort_values('Risk Score', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            msg = (
                "<b>System Status:</b> All districts operating within normal parameters.<br>"
                "<ul>"
                "<li>Continue routine monitoring procedures</li>"
                "<li>All systems operational</li>"
                "<li>No immediate action required</li>"
                "</ul>"
            )
            st.markdown(f'<div class="alert-success">{msg}</div>', unsafe_allow_html=True)

# BENGALURU ANALYSIS
else:
    def normalize_ward_name(name):
        if not isinstance(name, str):
            return ""
        name = re.sub(r'( ward| layout| nagar| nagara| town| city| temple)', '', name)
        name = re.sub(r'\W+', '', name)
        return name.strip()

    st.header("Bengaluru Outage Analysis") 
    st.subheader(f"Status: {selected_datetime.strftime('%B %d, %Y at %I:%M %p')}")

    if not outages_at_time.empty and bengaluru_geojson:
        active_outages = outages_at_time[outages_at_time['cause'] != 'No Outage']
        total_consumers = active_outages['consumers_affected'].sum()
        reliability = ((len(outages_at_time) - len(active_outages)) / len(outages_at_time)) * 100
        avg_duration = active_outages['duration_minutes'].mean() if not active_outages.empty else 0

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <p class="kpi-value">{len(active_outages)}</p>
                <p class="kpi-label">Active Outages</p>
            </div>
            <div class="kpi-card">
                <p class="kpi-value">{total_consumers:,}</p>
                <p class="kpi-label">Consumers Affected</p>
            </div>
            <div class="kpi-card">
                <p class="kpi-value">{reliability:.1f}%</p>
                <p class="kpi-label">System Reliability</p>
            </div>
            <div class="kpi-card">
                <p class="kpi-value">{avg_duration:.0f}</p>
                <p class="kpi-label">Avg Duration (Min)</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="legend-container">
            <div class="legend-item">
                <div class="legend-dot legend-normal"></div>
                <span>Normal Operations</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot legend-outage"></div>
                <span>Power Outage</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ward_data_map = {}
        for _, row in outages_at_time.iterrows():
            norm_ward = normalize_ward_name(row['ward_name'])
            ward_data_map[norm_ward] = {
                'status': 1 if row['cause'].lower() != 'no outage' else 0,
                'hover': format_outage_tooltip(row, st.session_state.user_type)
            }

        locations = []
        outage_values = []
        hover_texts = []
        geojson_wards = set()

        for feature in bengaluru_geojson['features']:
            properties = feature.get('properties', {})
            ward_name = properties.get('KGISWardName')
            norm_geojson_ward = normalize_ward_name(ward_name)
            geojson_wards.add(norm_geojson_ward)
            locations.append(ward_name)
            if norm_geojson_ward in ward_data_map:
                outage_values.append(ward_data_map[norm_geojson_ward]['status'])
                hover_texts.append(ward_data_map[norm_geojson_ward]['hover'])
            else:
                outage_values.append(0)
                hover_texts.append(f"<b>{ward_name}</b><br>Normal operations<br>No outages reported")

        fig = go.Figure(go.Choropleth(
            geojson=bengaluru_geojson,
            locations=locations,
            z=outage_values,
            featureidkey="properties.KGISWardName",
            colorscale=[[0, "#4450f9"], [1, '#dc2626']],
            zmin=0, zmax=1,
            showscale=False,
            hovertext=hover_texts,
            hovertemplate='%{hovertext}<extra></extra>',
            marker_line_color='white',
            marker_line_width=0.5
        ))

        fig.update_geos(
            projection_type="mercator",
            fitbounds="geojson",
            visible=False
        )

        fig.update_layout(
            height=500,
            margin={"r":0,"t":0,"l":0,"b":0},
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        if not active_outages.empty:
            st.markdown("### Current Outages")
            if st.session_state.user_type == 'Utilities':
                display_data = active_outages[['ward_name', 'cause', 'duration_minutes', 'consumers_affected', 'feeder_id']].copy()
                display_data.columns = ['Ward', 'Cause', 'Duration (min)', 'Consumers', 'Feeder']
            else:
                display_data = active_outages[['ward_name', 'duration_minutes', 'consumers_affected']].copy()
                display_data.columns = ['Area', 'Duration (min)', 'Residents Affected']
            st.dataframe(display_data.sort_values(display_data.columns[-2], ascending=False), use_container_width=True, hide_index=True)

        # FIXED: Alert with bullet points
        if not active_outages.empty:
            alert_class = f"alert-{st.session_state.user_type.lower()}"
            if st.session_state.user_type == 'Utilities':
                priority_ward = active_outages.loc[active_outages['consumers_affected'].idxmax()]
                msg = (
                    f"<b>Dispatch Required:</b> {len(active_outages)} active outages affecting {total_consumers:,} consumers.<br>"
                    f"<ul>"
                    f"<li>Priority Area: <b>{priority_ward['ward_name']}</b> ({priority_ward['consumers_affected']:,} affected)</li>"
                    f"<li>Deploy repair crews immediately</li>"
                    f"<li>Coordinate with local teams for traffic and safety</li>"
                    f"</ul>"
                )
                st.markdown(f'<div class="alert-utilities">{msg}</div>', unsafe_allow_html=True)
            else:
                affected_wards = ', '.join(active_outages['ward_name'].head(3))
                msg = (
                    f"<b>Service Alert:</b> Power supply interrupted in {len(active_outages)} areas.<br>"
                    f"<ul>"
                    f"<li>Affected areas include: <b>{affected_wards}</b></li>"
                    f"<li>Avoid using elevators, keep mobile charged</li>"
                    f"<li>Emergency services: 1912 (Electricity), 108 (Ambulance), 100 (Police), 101 (Fire)</li>"
                    f"<li>Stay updated via local news</li>"
                    f"</ul>"
                )
                st.markdown(f'<div class="alert-citizens">{msg}</div>', unsafe_allow_html=True)
        else:
            msg = (
                "<b>System Status:</b> All monitored areas operational.<br>"
                "<ul>"
                "<li>No power outages detected at this time</li>"
                "<li>All services are functioning normally</li>"
                "<li>Continue routine monitoring</li>"
                "</ul>"
            )
            st.markdown(f'<div class="alert-success">{msg}</div>', unsafe_allow_html=True)

    else:
        st.info("No outage data or map available for the selected time.")

# Sidebar info (keeping minimal info)
st.sidebar.markdown("---")
st.sidebar.info("**Total Karnataka Districts:** 31")
st.sidebar.info("**Data Source:** Enhanced weather and grid data")
