"""
Narration Layer - Translates structured plans into natural language
"""

from typing import Dict, Optional
from loguru import logger

from metabolic_city.utils.data_models import ResponsePlan, RiskScore


class NarrationLayer:
    """
    Translates structured response plans into clear natural-language summaries
    for human dispatchers.
    """
    
    def __init__(self):
        self.node_name = "narration_layer"
    
    def generate_briefing(self, response_plan: ResponsePlan) -> str:
        """
        Generate natural-language briefing from response plan
        
        Args:
            response_plan: ResponsePlan object
            
        Returns:
            Natural-language briefing string
        """
        try:
            risk = response_plan.risk_score
            emergency_name = response_plan.emergency_type.value.replace("_", " ").title()
            
            briefing = f"""
EMERGENCY BRIEFING
==================

Emergency Type: {emergency_name}
Location: Geohash {response_plan.geohash}
Timestamp: {response_plan.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
Priority Level: {response_plan.priority_level.upper()}

RISK ASSESSMENT
---------------
Composite Risk Index: {risk.composite_risk_index:.2f}/10.0
Risk Level: {risk.risk_level.upper()}
- Mobility Threat Score: {risk.mobility_score:.2f}/10.0
- Climate Threat Score: {risk.climate_score:.2f}/10.0
- Vulnerability Score: {risk.vulnerability_score:.2f}/10.0

DEPLOYMENT INSTRUCTIONS
-----------------------
Dispatch Zone: {response_plan.dispatch_zone}
Staging Area: {response_plan.staging_area}
Estimated Duration: {response_plan.estimated_duration_hours} hours

EQUIPMENT CHECKLIST
------------------
{self._format_list(response_plan.equipment_checklist)}

PERSONNEL REQUIREMENTS
---------------------
{self._format_personnel(response_plan.personnel_requirements)}

This response plan has been automatically generated based on real-time risk assessment.
All deployment parameters follow pre-approved municipal response templates.
"""
            logger.debug(f"{self.node_name}: Generated briefing for {response_plan.geohash}")
            return briefing.strip()
            
        except Exception as e:
            logger.error(f"{self.node_name}: Error generating briefing: {e}")
            return f"Error generating briefing: {str(e)}"
    
    def _format_list(self, items: list) -> str:
        """Format list as bullet points"""
        return "\n".join(f"- {item}" for item in items)
    
    def _format_personnel(self, personnel: Dict[str, int]) -> str:
        """Format personnel requirements"""
        return "\n".join(f"- {role}: {count}" for role, count in personnel.items())
    
    def generate_summary(self, response_plans: Dict[str, ResponsePlan]) -> str:
        """
        Generate summary of multiple response plans
        
        Args:
            response_plans: Dictionary mapping geohash to ResponsePlan
            
        Returns:
            Natural-language summary string
        """
        if not response_plans:
            return "No active response plans at this time."
        
        total_plans = len(response_plans)
        critical_count = sum(1 for p in response_plans.values() if p.priority_level == "critical")
        high_count = sum(1 for p in response_plans.values() if p.priority_level == "high")
        
        summary = f"""
OPERATIONAL SUMMARY
===================

Total Active Response Plans: {total_plans}
- Critical Priority: {critical_count}
- High Priority: {high_count}
- Medium/Low Priority: {total_plans - critical_count - high_count}

AFFECTED LOCATIONS
------------------
"""
        
        for geohash, plan in response_plans.items():
            summary += f"\nGeohash {geohash}: {plan.emergency_type.value.replace('_', ' ').title()} ({plan.priority_level})"
        
        summary += f"\n\nGenerated at: {response_plans[list(response_plans.keys())[0]].timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        logger.info(f"{self.node_name}: Generated summary for {total_plans} response plans")
        return summary.strip()
    
    def generate_alert_notification(self, response_plan: ResponsePlan) -> str:
        """
        Generate concise alert notification for dispatch
        
        Args:
            response_plan: ResponsePlan object
            
        Returns:
            Concise alert string
        """
        emergency_name = response_plan.emergency_type.value.replace("_", " ").title()
        
        alert = f"""
ALERT: {emergency_name}
Location: {response_plan.geohash}
Priority: {response_plan.priority_level.upper()}
Risk Index: {response_plan.risk_score.composite_risk_index:.2f}/10.0
Dispatch Zone: {response_plan.dispatch_zone}
Staging Area: {response_plan.staging_area}
""".strip()
        
        return alert
