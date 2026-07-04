"""
Agency Adapters - Translates response plans to agency-specific formats
"""

import aiohttp
from typing import Dict, Optional
from loguru import logger

from metabolic_city.utils.data_models import ResponsePlan
from metabolic_city.config.settings import settings


class BaseAdapter:
    """Base class for agency adapters"""
    
    def __init__(self, endpoint_url: Optional[str] = None):
        self.endpoint_url = endpoint_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_dispatch(self, formatted_data: Dict) -> bool:
        """Send formatted dispatch data to agency endpoint"""
        if not self.endpoint_url:
            logger.warning(f"Endpoint URL not configured, skipping dispatch")
            return False
        
        try:
            async with self.session.post(
                self.endpoint_url,
                json=formatted_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    logger.info(f"Dispatch sent successfully to {self.__class__.__name__}")
                    return True
                else:
                    logger.error(f"Dispatch failed: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error sending dispatch: {e}")
            return False


class TransitAdapter(BaseAdapter):
    """Adapter for transit/transportation dispatch systems"""
    
    def __init__(self):
        super().__init__(settings.dispatch_transit_system)
    
    def format_dispatch(self, response_plan: ResponsePlan) -> Dict:
        """
        Format response plan for transit system
        
        Args:
            response_plan: ResponsePlan object
            
        Returns:
            Formatted dispatch data for transit system
        """
        return {
            "dispatch_type": "transit_reroute",
            "priority": response_plan.priority_level,
            "location": {
                "geohash": response_plan.geohash,
                "dispatch_zone": response_plan.dispatch_zone,
                "staging_area": response_plan.staging_area
            },
            "operations": {
                "route_modifications": self._extract_route_changes(response_plan),
                "equipment_needed": [e for e in response_plan.equipment_checklist if "transport" in e.lower()],
                "estimated_duration_hours": response_plan.estimated_duration_hours
            },
            "metadata": {
                "emergency_type": response_plan.emergency_type.value,
                "risk_index": response_plan.risk_score.composite_risk_index,
                "timestamp": response_plan.timestamp.isoformat()
            }
        }
    
    def _extract_route_changes(self, response_plan: ResponsePlan) -> Dict:
        """Extract route modification instructions"""
        return {
            "affected_routes": [],  # Would be populated from route data
            "reroute_instructions": f"Implement emergency protocols for {response_plan.emergency_type.value}",
            "service_level": "reduced" if response_plan.priority_level in ["high", "critical"] else "normal"
        }


class PublicWorksAdapter(BaseAdapter):
    """Adapter for public works dispatch systems"""
    
    def __init__(self):
        super().__init__(settings.dispatch_public_works)
    
    def format_dispatch(self, response_plan: ResponsePlan) -> Dict:
        """
        Format response plan for public works system
        
        Args:
            response_plan: ResponsePlan object
            
        Returns:
            Formatted dispatch data for public works
        """
        return {
            "dispatch_type": "infrastructure_response",
            "priority": response_plan.priority_level,
            "location": {
                "geohash": response_plan.geohash,
                "dispatch_zone": response_plan.dispatch_zone,
                "staging_area": response_plan.staging_area
            },
            "operations": {
                "equipment_needed": self._filter_public_works_equipment(response_plan.equipment_checklist),
                "personnel_needed": response_plan.personnel_requirements,
                "estimated_duration_hours": response_plan.estimated_duration_hours
            },
            "metadata": {
                "emergency_type": response_plan.emergency_type.value,
                "risk_index": response_plan.risk_score.composite_risk_index,
                "timestamp": response_plan.timestamp.isoformat()
            }
        }
    
    def _filter_public_works_equipment(self, equipment_list: list) -> list:
        """Filter equipment relevant to public works"""
        public_works_keywords = ["pump", "generator", "repair", "construction", "barrier", "lighting"]
        return [e for e in equipment_list if any(kw in e.lower() for kw in public_works_keywords)]


class EmergencyAdapter(BaseAdapter):
    """Adapter for emergency services dispatch systems"""
    
    def __init__(self):
        super().__init__(settings.dispatch_emergency_services)
    
    def format_dispatch(self, response_plan: ResponsePlan) -> Dict:
        """
        Format response plan for emergency services
        
        Args:
            response_plan: ResponsePlan object
            
        Returns:
            Formatted dispatch data for emergency services
        """
        return {
            "dispatch_type": "emergency_response",
            "priority": response_plan.priority_level,
            "location": {
                "geohash": response_plan.geohash,
                "dispatch_zone": response_plan.dispatch_zone,
                "staging_area": response_plan.staging_area
            },
            "operations": {
                "equipment_needed": self._filter_emergency_equipment(response_plan.equipment_checklist),
                "personnel_needed": response_plan.personnel_requirements,
                "medical_requirements": self._assess_medical_needs(response_plan),
                "estimated_duration_hours": response_plan.estimated_duration_hours
            },
            "metadata": {
                "emergency_type": response_plan.emergency_type.value,
                "risk_index": response_plan.risk_score.composite_risk_index,
                "mobility_score": response_plan.risk_score.mobility_score,
                "climate_score": response_plan.risk_score.climate_score,
                "vulnerability_score": response_plan.risk_score.vulnerability_score,
                "timestamp": response_plan.timestamp.isoformat()
            }
        }
    
    def _filter_emergency_equipment(self, equipment_list: list) -> list:
        """Filter equipment relevant to emergency services"""
        emergency_keywords = ["medical", "rescue", "emergency", "triage", "communication"]
        return [e for e in equipment_list if any(kw in e.lower() for kw in emergency_keywords)]
    
    def _assess_medical_needs(self, response_plan: ResponsePlan) -> Dict:
        """Assess medical response needs based on emergency type"""
        from metabolic_city.utils.data_models import EmergencyType
        
        medical_needs = {
            "ambulances_required": 0,
            "medical_team_size": 0,
            "specialist_units": []
        }
        
        if response_plan.emergency_type in [
            EmergencyType.COMPOUND_THERMAL_STRANDING,
            EmergencyType.COMPOUND_PUBLIC_HEALTH
        ]:
            medical_needs["ambulances_required"] = 2
            medical_needs["medical_team_size"] = 4
            medical_needs["specialist_units"] = ["heat_stroke_specialist"]
        
        elif response_plan.emergency_type == EmergencyType.COMPOUND_FLOOD_EVACUATION:
            medical_needs["ambulances_required"] = 3
            medical_needs["medical_team_size"] = 6
            medical_needs["specialist_units"] = ["water_rescue", "triage"]
        
        return medical_needs
