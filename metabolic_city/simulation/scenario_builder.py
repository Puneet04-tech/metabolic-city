"""
Scenario Builder - Creates simulation scenarios for what-if analysis
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from metabolic_city.utils.data_models import SimulationScenario, UnifiedDataPoint


class ScenarioBuilder:
    """
    Builds simulation scenarios for testing infrastructure changes
    and their ripple effects across domains.
    """
    
    def __init__(self):
        self.scenarios: Dict[str, SimulationScenario] = {}
    
    def create_scenario(
        self,
        name: str,
        description: str,
        baseline_data: UnifiedDataPoint,
        parameters: Dict[str, Any]
    ) -> SimulationScenario:
        """
        Create a new simulation scenario
        
        Args:
            name: Scenario name
            description: Scenario description
            baseline_data: Baseline unified data point
            parameters: Simulation parameters
            
        Returns:
            SimulationScenario object
        """
        scenario_id = str(uuid.uuid4())
        
        # Create modified data by applying parameters to baseline
        modified_data = self._apply_parameters(baseline_data, parameters)
        
        scenario = SimulationScenario(
            scenario_id=scenario_id,
            name=name,
            description=description,
            timestamp=datetime.utcnow(),
            parameters=parameters,
            baseline_data=baseline_data,
            modified_data=modified_data,
            results=None
        )
        
        self.scenarios[scenario_id] = scenario
        logger.info(f"Created scenario: {name} (ID: {scenario_id})")
        
        return scenario
    
    def _apply_parameters(
        self,
        baseline: UnifiedDataPoint,
        parameters: Dict[str, Any]
    ) -> UnifiedDataPoint:
        """
        Apply simulation parameters to baseline data
        
        Args:
            baseline: Baseline unified data point
            parameters: Parameters to apply
            
        Returns:
            Modified UnifiedDataPoint
        """
        # Deep copy baseline
        import copy
        modified = copy.deepcopy(baseline)
        
        # Apply mobility modifications
        if "mobility_modifications" in parameters:
            mod = parameters["mobility_modifications"]
            if modified.mobility:
                if "delay_multiplier" in mod:
                    modified.mobility.average_delay_minutes *= mod["delay_multiplier"]
                if "cancelled_routes_add" in mod:
                    modified.mobility.cancelled_routes += mod["cancelled_routes_add"]
                if "vehicle_count_multiplier" in mod:
                    modified.mobility.vehicle_count = int(
                        modified.mobility.vehicle_count * mod["vehicle_count_multiplier"]
                    )
        
        # Apply climate modifications
        if "climate_modifications" in parameters:
            mod = parameters["climate_modifications"]
            if modified.climate:
                if "temperature_offset" in mod:
                    modified.climate.temperature_celsius += mod["temperature_offset"]
                if "precipitation_add" in mod:
                    modified.climate.precipitation_mm += mod["precipitation_add"]
                if "wind_speed_multiplier" in mod:
                    modified.climate.wind_speed_kmh *= mod["wind_speed_multiplier"]
        
        # Apply demographic modifications (typically static, but can simulate changes)
        if "demographic_modifications" in parameters:
            mod = parameters["demographic_modifications"]
            if modified.demographic:
                if "population_density_multiplier" in mod:
                    modified.demographic.population_density *= mod["population_density_multiplier"]
        
        return modified
    
    def get_predefined_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """
        Get predefined scenario templates
        
        Returns:
            Dictionary of scenario templates
        """
        return {
            "bridge_closure": {
                "name": "Major Bridge Closure",
                "description": "Simulate closure of a major bridge and its impact on transit",
                "parameters": {
                    "mobility_modifications": {
                        "delay_multiplier": 3.0,
                        "cancelled_routes_add": 5,
                        "vehicle_count_multiplier": 0.7
                    }
                }
            },
            "heat_wave": {
                "name": "Extreme Heat Wave",
                "description": "Simulate extreme heat event with temperature spike",
                "parameters": {
                    "climate_modifications": {
                        "temperature_offset": 15.0,
                        "precipitation_add": 0.0
                    }
                }
            },
            "transit_strike": {
                "name": "Transit Worker Strike",
                "description": "Simulate transit system strike reducing service",
                "parameters": {
                    "mobility_modifications": {
                        "delay_multiplier": 5.0,
                        "cancelled_routes_add": 20,
                        "vehicle_count_multiplier": 0.3
                    }
                }
            },
            "flash_flood": {
                "name": "Flash Flood Event",
                "description": "Simulate sudden heavy rainfall and flooding",
                "parameters": {
                    "climate_modifications": {
                        "temperature_offset": -2.0,
                        "precipitation_add": 40.0,
                        "wind_speed_multiplier": 1.5
                    },
                    "mobility_modifications": {
                        "delay_multiplier": 4.0,
                        "cancelled_routes_add": 10,
                        "vehicle_count_multiplier": 0.5
                    }
                }
            },
            "route_reduction": {
                "name": "Transit Route Reduction",
                "description": "Simulate permanent reduction in transit routes",
                "parameters": {
                    "mobility_modifications": {
                        "delay_multiplier": 1.5,
                        "cancelled_routes_add": 8,
                        "vehicle_count_multiplier": 0.8
                    }
                }
            }
        }
    
    def create_from_template(
        self,
        template_name: str,
        baseline_data: UnifiedDataPoint,
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> SimulationScenario:
        """
        Create scenario from predefined template
        
        Args:
            template_name: Name of template
            baseline_data: Baseline unified data point
            custom_parameters: Optional custom parameters to override template
            
        Returns:
            SimulationScenario object
        """
        templates = self.get_predefined_scenarios()
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = templates[template_name]
        parameters = template["parameters"].copy()
        
        # Apply custom parameters if provided
        if custom_parameters:
            parameters.update(custom_parameters)
        
        return self.create_scenario(
            name=template["name"],
            description=template["description"],
            baseline_data=baseline_data,
            parameters=parameters
        )
    
    def get_scenario(self, scenario_id: str) -> Optional[SimulationScenario]:
        """Get scenario by ID"""
        return self.scenarios.get(scenario_id)
    
    def list_scenarios(self) -> list:
        """List all scenarios"""
        return list(self.scenarios.values())
