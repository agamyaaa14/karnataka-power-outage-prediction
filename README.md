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
