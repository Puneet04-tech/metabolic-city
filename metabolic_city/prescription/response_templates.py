"""
Response Templates - Pre-approved municipal response blueprints
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from metabolic_city.utils.data_models import EmergencyType, ResponsePlan


class ResponseTemplateManager:
    """
    Manages pre-approved municipal response templates.
    Prevents AI hallucinations by restricting to structured templates.
    """
    
    def __init__(self, templates_path: Optional[str] = None):
        """
        Initialize template manager
        
        Args:
            templates_path: Path to templates JSON file
        """
        if templates_path:
            self.templates_path = Path(templates_path)
        else:
            self.templates_path = Path("metabolic_city/config/response_templates.json")
        
        self.templates: Dict[str, Dict] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load response templates from file"""
        if not self.templates_path.exists():
            logger.warning(f"Templates file not found at {self.templates_path}, creating default templates")
            self._create_default_templates()
            self._save_templates()
        
        try:
            with open(self.templates_path, 'r') as f:
                self.templates = json.load(f)
            logger.info(f"Loaded {len(self.templates)} response templates")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            self._create_default_templates()
    
    def _save_templates(self):
        """Save templates to file"""
        try:
            self.templates_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.templates_path, 'w') as f:
                json.dump(self.templates, f, indent=2)
            logger.info(f"Saved templates to {self.templates_path}")
        except Exception as e:
            logger.error(f"Error saving templates: {e}")
    
    def _create_default_templates(self):
        """Create default response templates"""
        self.templates = {
            "compound_thermal_stranding": {
                "emergency_type": "compound_thermal_stranding",
                "name": "Compound Thermal Stranding Emergency",
                "description": "High temperatures combined with transit delays and vulnerable population",
                "dispatch_zone_template": "{geohash} and surrounding 2km radius",
                "staging_area_template": "Nearest community center or public facility in {geohash}",
                "equipment_checklist": [
                    "mobile_cooling_units",
                    "hydration_supplies",
                    "medical_kits",
                    "portable_shade_structures",
                    "communication_equipment",
                    "transportation_vehicles"
                ],
                "personnel_requirements": {
                    "medical_staff": 2,
                    "logistics_coordinators": 1,
                    "volunteer_supervisors": 3,
                    "drivers": 2
                },
                "estimated_duration_hours": 4,
                "priority_level": "high"
            },
            "compound_transit_isolation": {
                "emergency_type": "compound_transit_isolation",
                "name": "Compound Transit Isolation Emergency",
                "description": "Severe transit disruptions affecting vulnerable communities",
                "dispatch_zone_template": "{geohash} transit corridor and adjacent neighborhoods",
                "staging_area_template": "Major transit hub serving {geohash}",
                "equipment_checklist": [
                    "alternative_transportation_vehicles",
                    "communication_systems",
                    "route_information_displays",
                    "crowd_control_equipment",
                    "medical_supplies"
                ],
                "personnel_requirements": {
                    "transit_coordinators": 2,
                    "customer_service_staff": 4,
                    "security_personnel": 2,
                    "logistics_staff": 1
                },
                "estimated_duration_hours": 6,
                "priority_level": "high"
            },
            "compound_flood_evacuation": {
                "emergency_type": "compound_flood_evacuation",
                "name": "Compound Flood Evacuation Emergency",
                "description": "Flash flooding combined with mobility issues and vulnerable population",
                "dispatch_zone_template": "{geohash} flood zone and evacuation routes",
                "staging_area_template": "High ground shelter nearest to {geohash}",
                "equipment_checklist": [
                    "water_rescue_equipment",
                    "emergency_vehicles",
                    "sandbags",
                    "pumps",
                    "emergency_shelter_supplies",
                    "medical_triage_equipment"
                ],
                "personnel_requirements": {
                    "rescue_teams": 3,
                    "medical_personnel": 4,
                    "evacuation_coordinators": 2,
                    "logistics_staff": 3,
                    "communication_specialists": 1
                },
                "estimated_duration_hours": 12,
                "priority_level": "critical"
            },
            "compound_infrastructure_failure": {
                "emergency_type": "compound_infrastructure_failure",
                "name": "Compound Infrastructure Failure Emergency",
                "description": "Critical infrastructure failure affecting multiple domains",
                "dispatch_zone_template": "{geohash} and affected service areas",
                "staging_area_template": "Emergency operations center for {geohash}",
                "equipment_checklist": [
                    "repair_equipment",
                    "backup_power_generators",
                    "communication_relay_systems",
                    "water_distribution_units",
                    "emergency_lighting"
                ],
                "personnel_requirements": {
                    "engineers": 3,
                    "technicians": 4,
                    "safety_officers": 2,
                    "logistics_coordinators": 2
                },
                "estimated_duration_hours": 8,
                "priority_level": "critical"
            },
            "compound_public_health": {
                "emergency_type": "compound_public_health",
                "name": "Compound Public Health Emergency",
                "description": "Public health crisis compounded by environmental and social factors",
                "dispatch_zone_template": "{geohash} and surrounding health district",
                "staging_area_template": "Nearest medical facility serving {geohash}",
                "equipment_checklist": [
                    "medical_supplies",
                    "testing_equipment",
                    "protective_equipment",
                    "communication_systems",
                    "quarantine_facilities"
                ],
                "personnel_requirements": {
                    "medical_personnel": 5,
                    "public_health_officers": 3,
                    "contact_tracers": 4,
                    "logistics_staff": 2
                },
                "estimated_duration_hours": 24,
                "priority_level": "critical"
            }
        }
        
        logger.info(f"Created {len(self.templates)} default response templates")
    
    def get_template(self, emergency_type: str) -> Optional[Dict]:
        """
        Get response template for emergency type
        
        Args:
            emergency_type: Type of emergency
            
        Returns:
            Template dictionary or None if not found
        """
        return self.templates.get(emergency_type)
    
    def list_templates(self) -> List[str]:
        """List all available template types"""
        return list(self.templates.keys())
    
    def populate_template(
        self,
        emergency_type: str,
        geohash: str,
        risk_score,
        additional_params: Optional[Dict] = None
    ) -> ResponsePlan:
        """
        Populate template with specific parameters
        
        Args:
            emergency_type: Type of emergency
            geohash: Geohash for the emergency
            risk_score: RiskScore object
            additional_params: Additional parameters for customization
            
        Returns:
            ResponsePlan object
        """
        template = self.get_template(emergency_type)
        if not template:
            logger.error(f"No template found for emergency type: {emergency_type}")
            raise ValueError(f"Unknown emergency type: {emergency_type}")
        
        # Populate template fields
        dispatch_zone = template["dispatch_zone_template"].format(geohash=geohash)
        staging_area = template["staging_area_template"].format(geohash=geohash)
        
        # Apply additional parameters if provided
        if additional_params:
            dispatch_zone = additional_params.get("dispatch_zone", dispatch_zone)
            staging_area = additional_params.get("staging_area", staging_area)
        
        # Determine priority based on risk level
        priority_level = template["priority_level"]
        if risk_score.risk_level == "critical":
            priority_level = "critical"
        elif risk_score.risk_level == "high":
            priority_level = "high"
        
        response_plan = ResponsePlan(
            emergency_type=EmergencyType(emergency_type),
            geohash=geohash,
            timestamp=risk_score.timestamp,
            risk_score=risk_score,
            dispatch_zone=dispatch_zone,
            staging_area=staging_area,
            equipment_checklist=template["equipment_checklist"].copy(),
            personnel_requirements=template["personnel_requirements"].copy(),
            estimated_duration_hours=template["estimated_duration_hours"],
            priority_level=priority_level,
            raw_plan_data=template
        )
        
        logger.info(f"Populated template for {emergency_type} in geohash {geohash}")
        return response_plan
    
    def add_template(self, template: Dict):
        """
        Add a new response template
        
        Args:
            template: Template dictionary
        """
        emergency_type = template.get("emergency_type")
        if not emergency_type:
            raise ValueError("Template must have emergency_type field")
        
        self.templates[emergency_type] = template
        self._save_templates()
        logger.info(f"Added new template: {emergency_type}")
