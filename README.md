# MetabolicCity AI

Enterprise decision intelligence platform for urban management through real-time, software-only coordination.

## Overview

MetabolicCity AI transforms urban management by treating public software streams, transportation feeds, and digital citizen inputs as a unified urban data network. The platform operates on a continuous, fully automated software pipeline that executes on an asynchronous clock cycle.

## Core Architecture

The platform operates on a **Four-Stage Pipeline**:

### Stage 1: Automated Ingestion & Unified Spatial Grid Normalization
- **Mobility Feed**: GTFS-RT streaming for vehicle positions and trip updates
- **Climate Feed**: Meteorological API integration for environmental metrics
- **Socio-Demographic Baseline**: Census block and demographic data
- **Unified Spatial Join**: All data mapped to uniform geohash grid

### Stage 2: Parallel Context Isolation & Domain Mapping
- **Isolated Mobility Node**: Evaluates transit delays and network strains
- **Isolated Climate Node**: Evaluates microclimate stress indicators
- **Isolated Vulnerability Node**: Calculates community baseline exposure
- **Graceful Degradation**: System continues operating if individual feeds fail

### Stage 3: Deterministic Matrix Triage Engine
- Mathematical risk calculation using weighted formula
- Composite Risk Index = (W_mobility × S_mobility) + (W_climate × S_climate) + (W_vulnerability × S_vulnerability)
- Transparent, auditable threshold-based alerting

### Stage 4: Constrained Prescriptive Blueprint Node
- Pre-approved municipal response templates
- Structured deployment parameters
- Natural-language narration for human dispatchers

## Enhanced Features

- **Temporal Trend Forecasting**: Predictive analysis using historical data
- **Cross-Domain Cascading Flow Simulation**: "What-If" sandbox for infrastructure testing
- **Automated Digital Feedback Loop**: Citizen report integration via NLP
- **Multi-Agency Digital Dispatch Broker**: Automated routing to departmental systems

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

Create a `.env` file with the following variables:

```env
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
WEATHER_API_KEY=your_weather_api_key

# GTFS-RT Endpoints
GTFS_RT_VEHICLE_POSITIONS_URL=https://example.com/gtfs-rt/vehicle-positions
GTFS_RT_TRIP_UPDATES_URL=https://example.com/gtfs-rt/trip-updates

# Database
DATABASE_URL=sqlite:///metabolic_city/data/metabolic_city.db

# Pipeline Settings
PIPELINE_CYCLE_MINUTES=10
RISK_THRESHOLD=7.0

# Weights (must sum to 1.0)
WEIGHT_MOBILITY=0.4
WEIGHT_CLIMATE=0.3
WEIGHT_VULNERABILITY=0.3
```

## Usage

### Run the Main Pipeline

```bash
python -m metabolic_city.main
```

### Run Individual Stages

```bash
# Stage 1: Ingestion
python -m metabolic_city.ingestion.main

# Stage 2: Analysis
python -m metabolic_city.analysis.main

# Stage 3: Triage
python -m metabolic_city.triage.main

# Stage 4: Prescription
python -m metabolic_city.prescription.main
```

### Run Enhanced Features

```bash
# Temporal Forecasting
python -m metabolic_city.forecasting.main

# Simulation Sandbox
python -m metabolic_city.simulation.main

# Feedback Processing
python -m metabolic_city.feedback.main

# Dispatch Broker
python -m metabolic_city.dispatch.main
```

### API Server

```bash
uvicorn metabolic_city.api:app --reload
```

## Project Structure

```
metabolic_city/
├── ingestion/          # Stage 1: Data ingestion and normalization
├── analysis/           # Stage 2: Isolated domain nodes
├── triage/             # Stage 3: Deterministic risk engine
├── prescription/       # Stage 4: Response template system
├── forecasting/        # Temporal trend forecasting
├── simulation/         # What-If sandbox
├── feedback/           # Citizen feedback integration
├── dispatch/           # Multi-agency dispatch broker
├── utils/              # Shared utilities
├── config/             # Configuration management
└── data/               # Data storage
```

## Implementation Strategy

1. **Data Availability Audit**: Verify public access to live data sources
2. **Core Ingestion Pipeline**: Build data normalization and geohash mapping
3. **Isolated Domain Node Integration**: Connect AI models for each domain
4. **Mathematical Triage Configuration**: Implement risk scoring formula
5. **Prescriptive Template Deployment**: Integrate response templates
6. **Narration Layer and UI Polish**: Add natural-language summaries

## License

MIT License - See LICENSE file for details

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.
