# API Endpoints Configuration Guide

This guide explains all the API endpoints and keys you need to configure in the `.env` file to run MetabolicCity AI with real data.

## Required API Keys

### 1. Gemini API (Google)
- **Purpose**: AI model for analysis and natural language processing
- **Get Key**: https://makersuite.google.com/app/apikey
- **Models Used**:
  - Primary: `gemini-2.5-flash` (stable, fast)
  - Fallback: `gemini-1.5-flash` (stable, fast)
- **Configuration**:
  ```
  GEMINI_API_KEY=your_gemini_api_key_here
  GEMINI_MODEL_PRIMARY=gemini-2.5-flash
  GEMINI_MODEL_FALLBACK=gemini-1.5-flash
  ```

### 2. Mistral API
- **Purpose**: Alternative AI model for analysis and natural language processing
- **Get Key**: https://console.mistral.ai/
- **Model Used**: `mistral-large-latest`
- **Configuration**:
  ```
  MISTRAL_API_KEY=your_mistral_api_key_here
  MISTRAL_MODEL=mistral-large-latest
  ```

### 3. Weather API
- **Purpose**: Real-time weather data for climate analysis
- **Options**:
  - **OpenWeatherMap** (default): https://openweathermap.org/api
  - **WeatherAPI**: https://www.weatherapi.com/
  - **Other**: Any weather API that provides current conditions
- **Configuration**:
  ```
  WEATHER_API_KEY=your_weather_api_key_here
  WEATHER_API_PROVIDER=openweathermap
  WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5
  ```

## Optional API Endpoints

### GTFS-RT Endpoints (Transit Data)
- **Purpose**: Real-time public transit data (vehicle positions, trip updates)
- **Get URLs**: Contact your local transit authority or check:
  - https://transitfeeds.com/
  - https://mobilitydatabase.org/
- **Required Endpoints**:
  ```
  GTFS_RT_VEHICLE_POSITIONS_URL=https://example.com/gtfs-rt/vehicle-positions
  GTFS_RT_TRIP_UPDATES_URL=https://example.com/gtfs-rt/trip-updates
  GTFS_STATIC_URL=https://example.com/gtfs-static.zip
  ```
- **Note**: If not configured, the system will use mock data for demonstration

### Feedback API Endpoint
- **Purpose**: Optional endpoint for citizen feedback integration
- **Configuration**:
  ```
  FEEDBACK_API_ENDPOINT=https://your-feedback-system.com/api/feedback
  ```
- **Note**: If not configured, feedback integration will use local storage

### Dispatch System Endpoints
- **Purpose**: Endpoints for multi-agency dispatch coordination
- **Configuration**:
  ```
  DISPATCH_TRANSIT_SYSTEM=https://your-transit-system.com/api
  DISPATCH_PUBLIC_WORKS=https://your-public-works.com/api
  DISPATCH_EMERGENCY_SERVICES=https://your-emergency-services.com/api
  ```
- **Note**: If not configured, dispatch will log to console instead of sending to external systems

## How to Get API Keys

### Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Paste into `.env` file as `GEMINI_API_KEY`

### Mistral API Key
1. Go to https://console.mistral.ai/
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the API key
6. Paste into `.env` file as `MISTRAL_API_KEY`

### OpenWeatherMap API Key
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Navigate to API Keys section
4. Your free API key will be displayed
5. Copy the API key
6. Paste into `.env` file as `WEATHER_API_KEY`

### GTFS-RT Endpoints
1. Find your city's transit authority website
2. Look for "Developer Resources" or "Open Data"
3. Find GTFS-Realtime feeds
4. Copy the URLs for:
   - Vehicle Positions
   - Trip Updates
   - Static GTFS (optional but recommended)
5. Paste into `.env` file

## Minimum Configuration for Demo Mode

For testing/demonstration without real data, you only need:

```env
# AI Models (required for any AI operations)
GEMINI_API_KEY=your_gemini_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here

# Weather (optional - will use mock data if not set)
WEATHER_API_KEY=your_weather_api_key_here

# GTFS-RT (optional - will use mock data if not set)
# Leave GTFS_RT_* URLs empty or commented out
```

## Full Production Configuration

For production use with real data:

```env
# AI Models
GEMINI_API_KEY=your_gemini_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
GEMINI_MODEL_PRIMARY=gemini-2.5-flash
GEMINI_MODEL_FALLBACK=gemini-1.5-flash
MISTRAL_MODEL=mistral-large-latest

# Weather
WEATHER_API_KEY=your_weather_api_key_here
WEATHER_API_PROVIDER=openweathermap
WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5

# GTFS-RT (Real Transit Data)
GTFS_RT_VEHICLE_POSITIONS_URL=https://your-city.com/gtfs-rt/vehicle-positions
GTFS_RT_TRIP_UPDATES_URL=https://your-city.com/gtfs-rt/trip-updates
GTFS_STATIC_URL=https://your-city.com/gtfs-static.zip

# Feedback Integration (Optional)
FEEDBACK_API_ENDPOINT=https://your-feedback-system.com/api/feedback

# Dispatch Systems (Optional)
DISPATCH_TRANSIT_SYSTEM=https://your-transit-system.com/api
DISPATCH_PUBLIC_WORKS=https://your-public-works.com/api
DISPATCH_EMERGENCY_SERVICES=https://your-emergency-services.com/api
```

## Testing Your Configuration

After configuring your `.env` file, test the system:

```bash
# Activate virtual environment
./venv/Scripts/activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac

# Run the pipeline
python -m metabolic_city
```

The system will:
1. Load your API keys from `.env`
2. Attempt to connect to configured endpoints
3. Fall back to mock data if endpoints are unavailable
4. Report any connection errors in the logs

## Troubleshooting

### API Key Not Working
- Verify the key is copied correctly (no extra spaces)
- Check if the key has the required permissions
- Ensure your account has available quota

### GTFS-RT 404 Errors
- Verify the URLs are correct and accessible
- Some transit authorities require authentication
- Check if the feeds are publicly available
- Try accessing the URL in a browser to test

### Weather API Errors
- Verify your API key is valid
- Check if you've exceeded rate limits
- Ensure the API provider URL is correct

### General Tips
- The system includes graceful degradation - it will work with partial configuration
- Check `logs/metabolic_city.log` for detailed error messages
- Start with minimum configuration and add endpoints incrementally
- Use mock data for development and testing before connecting to real APIs
