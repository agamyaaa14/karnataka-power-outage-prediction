# Karnataka Power Grid Hyperlocal Risk Forecasting System

A data-driven prototype for **proactive power outage risk assessment and hyperlocal outage awareness** across Karnataka, with a focused view of Bengaluru.

The project addresses a simple real-world problem:

> Power outages can be extremely local. Two people living in different areas can experience completely different power conditions even when they are experiencing the same weather.

Instead of only asking **"Will Karnataka have power outages?"**, this system attempts to answer:

- Which districts are currently at higher risk?
- What factors are contributing to that risk?
- Which areas of Bengaluru may be more vulnerable?
- How many consumers could potentially be affected?
- What operational action could utility teams consider?
- How can citizens be alerted about potential outage conditions?

The prototype provides two separate interfaces:

1. **Utility Interface** – designed for maintenance and operations teams.
2. **Citizen Interface** – designed to communicate outage awareness and safety information to the public.

---

## Project Motivation

Traditional weather-based alerts are useful at a broad level, but power outages are often **hyperlocal**.

For example, two people living in nearby areas may experience the same wind, temperature, and humidity conditions, while one area loses power and the other does not.

This happens because outage risk is influenced by more than weather. Infrastructure characteristics such as:

- transformer condition
- feeder reliability
- asset age
- overhead vs underground lines
- geographical location
- consumer density
- local infrastructure

can significantly influence how vulnerable an area may be.

The long-term goal of this project is therefore to move from:

**"An outage happened → respond"**

towards:

**"An outage may be likely → prepare and alert."**

---

## Key Features

### Karnataka District-Level Risk Assessment
The system processes weather information across Karnataka and assigns each district a risk score.

Districts are classified into:
- Low
- Medium
- High
- Severe

Risk is influenced by factors such as:
- Wind
- Temperature / heat stress
- Humidity
- District characteristics
- Infrastructure-related risk factors

### Bengaluru Hyperlocal Outage View
Instead of showing Bengaluru as a single unit, the system provides a more localized view of selected Bengaluru areas.

This is important because:
> Saying "Bengaluru has a power outage" is not particularly useful.

A citizen or maintenance team needs to know **which area is affected**. The prototype therefore uses geographical boundaries and localized infrastructure information to represent potential outage conditions at an area/ward level.

### Utility Interface
The utility-facing interface focuses on operational awareness. It provides information such as:
- District risk levels
- Risk factors
- Bengaluru outage areas
- Number of affected consumers
- Estimated outage duration
- Reliability information
- Potential causes
- Operational recommendations
- Time-based risk/outage views

The goal is to help maintenance teams identify **where attention may be required first**.

### Citizen Interface
The citizen-facing interface presents information in a simpler format. Instead of exposing technical infrastructure information, it focuses on:
- Potential outage areas
- Current risk awareness
- Affected locations
- Safety/preparedness information
- Citizen-friendly alerts

The idea is to provide the public with useful information without requiring them to understand electrical-grid terminology.

---

## System Overview

The overall workflow can be represented as:

```text

                Weather Data
                     |
                     v
              Data Cleaning
                     |
                     v
          Missing Value Handling
                     |
                     v
          District Standardization
                     |
                     v
          Risk Score Calculation
                     |
                     v
       +-------------+-------------+
       |                           |
       v                           v
Karnataka District Risk      Bengaluru Hyperlocal
       Analysis              Outage Simulation
       |                           |
       |                     Infrastructure Data
       |                           |
       +-------------+-------------+
                     |
                     v
              Processed Data
                     |
                     v
              Streamlit App
              /           \
             /             \
            v               v
     Utility Interface   Citizen Interface

```

## Data Sources

### 1. Weather Data
Weather information was obtained from IMD (India Meteorological Department) weather station data. Because the required historical information was not available in a convenient downloadable format for all districts, weather values were collected from the available visual weather graphs.

Screenshots covering approximately two weeks of historical observations were collected and processed to extract structured weather values. The extracted information was then converted into structured tabular data for further processing.

Weather attributes used include:
- Temperature
- Wind speed
- Humidity
- Date
- Time
- Location / district

The weather data was then cleaned, standardized, and processed before being used for risk calculations.

### 2. Karnataka GeoJSON
Publicly available GeoJSON boundary data was used to visualize Karnataka geographically. This allows the system to display district-level risk information on an interactive map instead of presenting the results only as tables.

### 3. Bengaluru GeoJSON
Publicly available Bengaluru geographical boundary data was used for the hyperlocal visualization. The prototype focuses on a selected set of major/popular Bengaluru areas rather than attempting to model every residential area in the city. This was done to keep the prototype manageable while demonstrating the concept of hyperlocal outage awareness.

### 4. Infrastructure and Outage Data
Detailed transformer- and feeder-level operational data was not available for this prototype. Therefore, infrastructure and outage information was synthetically generated for demonstration and analysis.

The synthetic data was designed to represent differences in infrastructure vulnerability, including factors such as:
- Feeder reliability
- Asset age
- Infrastructure type
- Consumer count
- Infrastructure risk
- Potential outage causes
- Estimated outage duration
- Consumers affected

The synthetic outage scenarios were also designed to remain reasonably consistent with the calculated environmental risk.

> **Important:** The outage records in this prototype should not be interpreted as real historical outage records from a utility.

---

## Why Transformer and Feeder Data Matters

Weather is an important external factor, but it is not sufficient to explain hyperlocal outages. For example:

```text
             Same weather
                  |
         +----------------+
         |                |
         v                v
      Area A            Area B
   newer assets      older assets
   underground       overhead lines
higher reliability  lower reliability
         |                |
         v                v
    Lower risk       Higher risk
```

This is why actual transformer and feeder-level information would significantly improve the system. If real infrastructure data were available for each area, the system could potentially incorporate:

- Transformer location
- Transformer age
- Transformer capacity
- Feeder condition
- Feeder loading
- Historical failures
- Maintenance history
- Overhead / underground line information
- Number of consumers connected
- Historical outage frequency

This would make the system substantially more hyperlocal and data-driven.

---

## Risk Scoring

The current prototype uses a rule-based risk scoring approach. The risk score considers environmental and infrastructure-related factors such as:

**Weather Risk:**
- Wind-related risk
- Heat-related stress
- Humidity-related stress

**Geographic Risk:**
Different districts have different characteristics. For example, coastal, urban, industrial, and other district categories can have different risk multipliers.

**Infrastructure Risk:**
Infrastructure characteristics can influence vulnerability. Factors include:
- Feeder type
- Asset age
- Reliability
- Local infrastructure characteristics

The combined risk is converted into a score between 1 and 10 and classified into:

- **1–2:** Low
- **3–5:** Medium
- **6–8:** High
- **9–10:** Severe

---

## Bengaluru Hyperlocal Outage Simulation

The Bengaluru component demonstrates how outage analysis could move beyond city-level predictions. The system generates potential outage scenarios for selected areas based on factors such as:

- Infrastructure reliability
- Risk multiplier
- Weather conditions
- Peak-hour effects
- Weekend effects
- Infrastructure characteristics

Each simulated outage can contain information such as:

- Area
- Feeder ID
- Cause
- Duration
- Consumers affected
- Crew requirement
- Restoration complexity
- Estimated revenue impact

Some outage scenarios were strategically included in the synthetic dataset to demonstrate how the interface behaves under different conditions.

---

## Data Processing Pipeline

The data processing pipeline performs several steps before the data reaches the dashboard.

1. **Load Data**  
   Weather data is loaded from Excel/text-based sources.

2. **Normalize Columns**  
   Column names and location values are standardized.

3. **Clean Numeric Values**  
   Values containing units such as `32°C`, `12 km/h`, and `75%` are converted into usable numerical values.

4. **Create Date-Time Information**  
   Separate date and time information is combined into a usable datetime field.

5. **Handle Missing Values**  
   Missing weather observations are handled using interpolation and representative values where appropriate.

6. **Standardize District Names**  
   Different naming formats are normalized so that they can be correctly associated with Karnataka districts.

7. **Add Missing Districts**  
   Where weather observations were unavailable for certain districts, representative values based on available district observations were used for the prototype.

8. **Calculate Risk**  
   Weather and infrastructure-related factors are used to calculate district-level risk.

9. **Generate Hyperlocal Outage Scenarios**  
   Synthetic Bengaluru outage scenarios are generated using infrastructure and risk information.

10. **Export Processed Data**  
    The processed datasets are saved for use by the application.

---

## Application Interfaces

### 1. Utility Interface
The utility interface is designed for maintenance and operations teams. It focuses on questions such as:

- Where should we pay attention?
- Which districts are at higher risk?
- Which Bengaluru areas may experience outages?
- How many consumers could be affected?
- What could be contributing to the risk?

![Utility Dashboard Placeholder](images/utility-dashboard.png)  
*(Replace the path above with your actual screenshot)*

### 2. Citizen Interface
The citizen interface presents the same underlying information in a simpler and more accessible way. It focuses on:

- Area-level outage awareness
- Risk information
- Potential affected locations
- Safety guidance
- Public alerts

![Citizen Dashboard Placeholder](images/citizen-dashboard.png)  
*(Replace the path above with your actual screenshot)*

---

## Technology Stack

**Programming & Data Processing**
- Python
- Pandas
- NumPy

**Data Visualization / Application**
- Streamlit
- GeoJSON
- Interactive geographical visualization

**Data Sources**
- IMD weather station data
- Public Karnataka GeoJSON data
- Public Bengaluru GeoJSON data
- Synthetic infrastructure and outage data

---

## Example Use Cases

### For Utility Teams
The system can support:
- Early identification of high-risk districts
- Prioritization of maintenance resources
- Crew planning
- Potential equipment staging
- Identification of vulnerable areas
- Situational awareness during adverse weather

### For Citizens
The system can support:
- Awareness of potential outages
- Area-specific outage information
- Preparedness before severe weather
- Understanding whether their locality may be affected

---

## Why Hyperlocal Prediction?

A state-level statement such as:
> "Karnataka has a high outage risk."

does not provide enough information for either a utility operator or a citizen. A more useful output is:
> "This particular area has elevated risk because of its local infrastructure characteristics combined with current environmental conditions."

The ultimate goal is therefore to move toward:

```text
State Level
     ↓
District Level
     ↓
City Level
     ↓
Area / Ward Level
     ↓
Feeder Level
     ↓
Transformer Level
```

The further down this hierarchy the system can reliably operate, the more useful the prediction becomes.

---

## Limitations

This project is a prototype, and several limitations exist.

1. **Synthetic outage data**  
   The current outage scenarios are synthetically generated because real utility outage records were not available.

2. **Limited infrastructure data**  
   Actual transformer and feeder-level information was not available. This is the most important area for future improvement.

3. **Limited Bengaluru coverage**  
   Only selected major/popular Bengaluru areas were modeled because the project was developed as a prototype.

4. **Weather data availability**  
   Weather observations were not available in the required format for every district, so missing information had to be handled during preprocessing.

5. **Rule-based risk model**  
   The current prototype uses a rule-based risk scoring approach rather than a model trained on a large historical outage dataset. Therefore, the risk scores should be considered prototype decision-support outputs, not official outage predictions.

---

## Future Improvements

The system could be significantly improved with access to real utility infrastructure and historical outage data.

### Real Transformer and Feeder Data
Integrating actual:
- Transformer locations
- Transformer age
- Transformer capacity
- Feeder connections
- Feeder loading
- Historical failures
- Maintenance records

could allow the system to produce much more precise predictions.

### Historical Outage Data
With historical outage records, the project could move from rule-based risk scoring toward a supervised machine learning approach. Potential inputs could include:

```text
       Weather
          +
    Infrastructure
          +
  Historical outages
          +
      Geography
          +
    Time patterns
          ↓
Machine Learning Model
          ↓
Probability of outage
          ↓
Hyperlocal risk map
```
### More Detailed Geographic Coverage
Future versions could expand from selected Bengaluru areas to:
- All Bengaluru wards
- Individual feeders
- Transformer-level areas
- Other major cities in Karnataka

### Real-Time Data
Integration with live:
- Weather APIs
- Utility monitoring systems
- Smart meters
- Transformer sensors
- Feeder monitoring systems

could allow the system to move toward real-time risk monitoring.

### Improved Infrastructure Modeling
Infrastructure characteristics could be modeled more realistically by considering:
- Underground vs overhead lines
- Age of infrastructure
- Maintenance history
- Load conditions
- Transformer capacity
- Feeder reliability
- Local geography

For example, recently developed areas with underground infrastructure could have different vulnerability characteristics compared with older areas relying heavily on overhead lines.

---

## Key Insight

The biggest insight from this project was:

> **Weather alone cannot explain hyperlocal power outages.**

Two nearby locations can experience the same weather but have different outage outcomes because their infrastructure is different. Therefore, a useful power-grid risk system needs to combine:

**Weather + Geography + Infrastructure + Historical Outage Patterns**

rather than relying on weather alone.

---

## Project Outcome

The project was developed as a prototype to demonstrate how data can be transformed into actionable information for both utility teams and citizens. The final system provides:

- Karnataka district-level risk assessment
- Bengaluru hyperlocal outage visualization
- Geographic risk maps
- Synthetic outage scenarios
- Consumer impact estimates
- Operational recommendations
- Separate utility and citizen interfaces

The project won the PATLN IET Bangalore Network Hackathon and also contributed to my understanding of how domain research, data engineering, geographic visualization, and decision-support systems can be combined to solve a real-world problem.

---

## Disclaimer

This project is an academic/prototype system and is not an official power-grid forecasting or outage notification system. Weather observations were collected from available IMD weather station visualizations, while infrastructure and outage records used in the prototype were synthetically generated for demonstration purposes. 

The system should therefore not be used for real-world operational decisions without validation using actual utility infrastructure, historical outage records, and domain-expert review.

---
