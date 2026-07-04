"""
Prescription Node - Generates structured response plans
"""

from typing import Dict, Optional
from loguru import logger

from metabolic_city.utils.data_models import RiskScore, ResponsePlan, EmergencyType
from metabolic_city.prescription.response_templates import ResponseTemplateManager


class PrescriptionNode:
    """
    Constrained operational node that generates response plans.
    Strictly banned from writing freeform prose - must use pre-approved templates.
    """
    
    def __init__(self):
        self.template_manager = ResponseTemplateManager()
        self.node_name = "prescription_node"
    
    def determine_emergency_type(self, risk_score: RiskScore) -> EmergencyType:
        """
        Determine emergency type based on risk scores
        
        Args:
            risk_score: RiskScore object with domain scores
            
        Returns:
            EmergencyType enum value
        """
        mobility = risk_score.mobility_score
        climate = risk_score.climate_score
        vulnerability = risk_score.vulnerability_score
        
        # Decision tree for emergency classification
        if climate >= 7.0 and mobility >= 5.0:
            # High climate stress + mobility issues
            if climate >= 8.0:
                return EmergencyType.COMPOUND_THERMAL_STRANDING
            else:
                return EmergencyType.COMPOUND_TRANSIT_ISolation
        
        elif climate >= 7.0 and vulnerability >= 6.0:
            # High climate stress + vulnerable population
            if climate >= 8.0 or vulnerability >= 8.0:
                return EmergencyType.COMPOUND_THERMAL_STRANDING
            else:
                return EmergencyType.COMPOUND_PUBLIC_HEALTH
        
        elif mobility >= 7.0 and vulnerability >= 6.0:
            # High mobility issues + vulnerable population
            return EmergencyType.COMPOUND_TRANSIT_ISOLATION
        
        elif climate >= 8.0:
            # Extreme climate conditions
            if climate >= 9.0:
                return EmergencyType.COMPOUND_FLOOD_EVACUATION
            else:
                return EmergencyType.COMPOUND_THERMAL_STRANDING
        
        elif mobility >= 8.0:
            # Extreme mobility disruption
            return EmergencyType.COMPOUND_INFRASTRUCTURE_FAILURE
        
        elif vulnerability >= 8.0:
            # Extreme vulnerability
            return EmergencyType.COMPOUND_PUBLIC_HEALTH
        
        else:
            # Default to transit isolation for moderate risks
            return EmergencyType.COMPOUND_TRANSIT_ISOLATION
    
    def generate_response_plan(
        self,
        risk_score: RiskScore,
        additional_params: Optional[Dict] = None
    ) -> ResponsePlan:
        """
        Generate structured response plan using pre-approved template
        
        Args:
            risk_score: RiskScore object
            additional_params: Optional additional parameters
            
        Returns:
            ResponsePlan object
        """
        try:
            # Determine emergency type
            emergency_type = self.determine_emergency_type(risk_score)
            
            logger.info(f"{self.node_name}: Determined emergency type: {emergency_type}")
            
            # Populate template
            response_plan = self.template_manager.populate_template(
                emergency_type.value,
                risk_score.geohash,
                risk_score,
                additional_params
            )
            
            logger.info(f"{self.node_name}: Generated response plan for {risk_score.geohash}")
            return response_plan
            
        except Exception as e:
            logger.error(f"{self.node_name}: Error generating response plan: {e}")
            raise
    
    def generate_batch(
        self,
        risk_scores: Dict[str, RiskScore]
    ) -> Dict[str, ResponsePlan]:
        """
        Generate response plans for multiple geohashes
        
        Args:
            risk_scores: Dictionary mapping geohash to RiskScore
            
        Returns:
            Dictionary mapping geohash to ResponsePlan
        """
        response_plans = {}
        
        for geohash, risk_score in risk_scores.items():
            try:
                response_plans[geohash] = self.generate_response_plan(risk_score)
            except Exception as e:
                logger.error(f"Failed to generate plan for {geohash}: {e}")
                continue
        
        logger.info(f"{self.node_name}: Generated {len(response_plans)} response plans")
        return response_plans
    
    def validate_plan_structure(self, plan: ResponsePlan) -> bool:
        """
        Validate that response plan follows required structure
        
        Args:
            plan: ResponsePlan to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "emergency_type",
            "geohash",
            "timestamp",
            "risk_score",
            "dispatch_zone",
            "staging_area",
            "equipment_checklist",
            "personnel_requirements",
            "estimated_duration_hours",
            "priority_level"
        ]
        
        for field in required_fields:
            if not hasattr(plan, field) or getattr(plan, field) is None:
                logger.error(f"Validation failed: missing field {field}")
                return False
        
        # Validate equipment checklist is not empty
        if not plan.equipment_checklist:
            logger.error("Validation failed: equipment checklist is empty")
            return False
        
        # Validate personnel requirements
        if not plan.personnel_requirements:
            logger.error("Validation failed: personnel requirements is empty")
            return False
        
        logger.debug(f"Plan validation passed for {plan.geohash}")
        return True
