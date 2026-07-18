# Karnataka Power Outage Prediction

> 🏆 Winner — PATLN IET Bangalore Network Hackathon  
> Developed for Balfour Beatty Infrastructure India

Predicting localized power outages 24 hours in advance using weather forecasts, infrastructure data, and machine learning to support proactive maintenance and improve grid reliability.

---

## Project Overview

Power outages are often influenced by changing weather conditions and infrastructure failures. Utility providers typically respond only after outages occur, resulting in increased downtime and customer impact.

This project proposes a predictive maintenance solution that forecasts potential outages one day in advance, allowing engineers to identify high-risk regions and prioritize preventive actions.

The solution was developed during the **PATLN IET Bangalore Network Hackathon**, where it won first place and earned an internship opportunity with **Balfour Beatty Infrastructure India**.

---

## Problem Statement

Electrical utilities face challenges such as:

- Severe weather affecting power infrastructure
- Delayed identification of high-risk areas
- Reactive maintenance workflows
- Limited visibility into outage risks

The objective was to build a machine learning system capable of identifying areas that are likely to experience outages within the next 24 hours.

---

## Solution

The proposed solution combines weather forecasts with infrastructure information to estimate outage probability.

The workflow consists of:

Weather Data
↓

Infrastructure Data
↓

Feature Engineering
↓

Machine Learning Model
↓

Risk Prediction
↓

Interactive Dashboard

Engineers can use the dashboard to monitor outage risks and prioritize maintenance activities before failures occur.

---

## Features

- Predicts localized power outages 24 hours in advance
- Weather-driven risk assessment
- Infrastructure-aware predictions
- Interactive dashboard for visualization
- Region-wise outage probability
- Easy-to-understand risk indicators

---

# Machine Learning Pipeline

1. Data Collection
    - Weather observations
    - Infrastructure information
    - Historical outage patterns (synthetic for hackathon)

2. Data Cleaning
    - Missing value handling
    - Feature normalization
    - Data validation

3. Feature Engineering
    - Temperature
    - Rainfall
    - Wind Speed
    - Humidity
    - Infrastructure condition
    - Region mapping

4. Model Training
    - Train/Test split
    - Model selection
    - Performance evaluation

5. Prediction
    - Generate outage probability
    - Classify risk level
    - Display predictions on dashboard

---

## Technology Stack

### Programming

- Python

### Machine Learning

- Scikit-learn
- Pandas
- NumPy

### Visualization

- Streamlit
- Plotly

### Development

- Git
- GitHub

---

# Repository Structure

```
.
├── data/
├── models/
├── notebooks/
├── src/
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── train.py
│   ├── predict.py
│   └── utils.py
├── app.py
├── requirements.txt
└── README.md
```

*(Modify this tree to match your actual repository.)*

---

# Screenshots

## Dashboard

![Dashboard](images/dashboard.png)

---

## Prediction Results

![Predictions](images/predictions.png)

---

## Risk Map

![Risk Map](images/risk-map.png)

---

## Model Workflow

![Architecture](images/architecture.png)

---

## Feature Importance

![Feature Importance](images/feature-importance.png)

---

# Future Improvements

- Real-time weather API integration
- Live utility infrastructure data
- Deep learning models
- GIS-based visualization
- Automated maintenance recommendations
- Alert notification system

---

# Installation

Clone the repository

```bash
git clone https://github.com/agamyaaa14/karnataka-power-outage-prediction.git
```

Navigate into the project

```bash
cd karnataka-power-outage-prediction
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

## Key Learnings

- Building end-to-end machine learning pipelines
- Feature engineering for predictive analytics
- Designing interactive dashboards for decision support
- Collaborating under hackathon time constraints
- Presenting technical solutions to industry professionals

---

# Results

The prototype successfully demonstrated the feasibility of predicting localized outage risks using weather and infrastructure features, enabling proactive maintenance planning.

---
