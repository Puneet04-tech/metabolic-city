"""
Dispatch Broker - Routes response plans to appropriate agency systems
"""

import asyncio
from typing import Dict, List, Optional
from loguru import logger

from metabolic_city.utils.data_models import ResponsePlan
from metabolic_city.dispatch.agency_adapters import (
    TransitAdapter,
    PublicWorksAdapter,
    EmergencyAdapter
)
from metabolic_city.config.settings import settings


class DispatchBroker:
    """
    Automated router that translates action blueprints into specific
    data formats required by separate departmental tools.
    Coordinates fast, synchronized response across multiple agencies.
    """
    
    def __init__(self):
        self.enabled = settings.dispatch_enabled
        self.transit_adapter = TransitAdapter()
        self.public_works_adapter = PublicWorksAdapter()
        self.emergency_adapter = EmergencyAdapter()
        
        if not self.enabled:
            logger.warning("Dispatch broker is disabled in settings")
    
    async def dispatch_plan(self, response_plan: ResponsePlan) -> Dict[str, bool]:
        """
        Dispatch a response plan to appropriate agencies
        
        Args:
            response_plan: ResponsePlan object
            
        Returns:
            Dictionary mapping agency name to dispatch success status
        """
        if not self.enabled:
            logger.warning("Dispatch broker is disabled")
            return {}
        
        logger.info(f"Dispatching plan for {response_plan.geohash} (type: {response_plan.emergency_type.value})")
        
        # Determine which agencies to dispatch to based on emergency type
        agencies_to_dispatch = self._determine_agencies(response_plan)
        
        # Dispatch to all relevant agencies concurrently
        dispatch_results = {}
        
        async with self.transit_adapter, self.public_works_adapter, self.emergency_adapter:
            tasks = []
            
            if "transit" in agencies_to_dispatch:
                tasks.append(("transit", self._dispatch_to_transit(response_plan)))
            
            if "public_works" in agencies_to_dispatch:
                tasks.append(("public_works", self._dispatch_to_public_works(response_plan)))
            
            if "emergency" in agencies_to_dispatch:
                tasks.append(("emergency", self._dispatch_to_emergency(response_plan)))
            
            # Execute dispatches concurrently
            results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            # Collect results
            for (agency, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"Dispatch to {agency} failed: {result}")
                    dispatch_results[agency] = False
                else:
                    dispatch_results[agency] = result
        
        success_count = sum(1 for success in dispatch_results.values() if success)
        logger.info(f"Dispatch complete: {success_count}/{len(dispatch_results)} agencies notified")
        
        return dispatch_results
    
    def _determine_agencies(self, response_plan: ResponsePlan) -> List[str]:
        """
        Determine which agencies should be notified based on emergency type
        
        Args:
            response_plan: ResponsePlan object
            
        Returns:
            List of agency identifiers
        """
        from metabolic_city.utils.data_models import EmergencyType
        
        agencies = []
        
        # Always include emergency services for critical/high priority
        if response_plan.priority_level in ["critical", "high"]:
            agencies.append("emergency")
        
        # Add agencies based on emergency type
        if response_plan.emergency_type == EmergencyType.COMPOUND_TRANSIT_ISOLATION:
            agencies.append("transit")
        
        elif response_plan.emergency_type == EmergencyType.COMPOUND_FLOOD_EVACUATION:
            agencies.extend(["public_works", "emergency"])
        
        elif response_plan.emergency_type == EmergencyType.COMPOUND_INFRASTRUCTURE_FAILURE:
            agencies.append("public_works")
        
        elif response_plan.emergency_type == EmergencyType.COMPOUND_THERMAL_STRANDING:
            agencies.extend(["transit", "emergency"])
        
        elif response_plan.emergency_type == EmergencyType.COMPOUND_PUBLIC_HEALTH:
            agencies.append("emergency")
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(agencies))
    
    async def _dispatch_to_transit(self, response_plan: ResponsePlan) -> bool:
        """Dispatch to transit system"""
        formatted_data = self.transit_adapter.format_dispatch(response_plan)
        return await self.transit_adapter.send_dispatch(formatted_data)
    
    async def _dispatch_to_public_works(self, response_plan: ResponsePlan) -> bool:
        """Dispatch to public works system"""
        formatted_data = self.public_works_adapter.format_dispatch(response_plan)
        return await self.public_works_adapter.send_dispatch(formatted_data)
    
    async def _dispatch_to_emergency(self, response_plan: ResponsePlan) -> bool:
        """Dispatch to emergency services"""
        formatted_data = self.emergency_adapter.format_dispatch(response_plan)
        return await self.emergency_adapter.send_dispatch(formatted_data)
    
    async def dispatch_batch(self, response_plans: Dict[str, ResponsePlan]) -> Dict[str, Dict[str, bool]]:
        """
        Dispatch multiple response plans concurrently
        
        Args:
            response_plans: Dictionary mapping geohash to ResponsePlan
            
        Returns:
            Dictionary mapping geohash to dispatch results
        """
        if not self.enabled:
            return {}
        
        logger.info(f"Dispatching {len(response_plans)} response plans")
        
        # Dispatch all plans concurrently
        tasks = [
            self.dispatch_plan(plan)
            for plan in response_plans.values()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        dispatch_results = {}
        for (geohash, plan), result in zip(response_plans.items(), results):
            if isinstance(result, Exception):
                logger.error(f"Dispatch for {geohash} failed: {result}")
                dispatch_results[geohash] = {}
            else:
                dispatch_results[geohash] = result
        
        return dispatch_results
    
    def generate_dispatch_summary(self, dispatch_results: Dict[str, Dict[str, bool]]) -> str:
        """
        Generate summary of dispatch operations
        
        Args:
            dispatch_results: Dictionary of dispatch results
            
        Returns:
            Summary string
        """
        if not dispatch_results:
            return "No dispatch operations performed."
        
        total_plans = len(dispatch_results)
        successful_dispatches = sum(
            1 for results in dispatch_results.values()
            if any(success for success in results.values())
        )
        
        summary = f"""
DISPATCH SUMMARY
================

Total Response Plans Dispatched: {total_plans}
Successful Dispatches: {successful_dispatches}
Failed Dispatches: {total_plans - successful_dispatches}

AGENCY NOTIFICATION BREAKDOWN
-----------------------------
"""
        
        # Count agency notifications
        agency_counts = {"transit": 0, "public_works": 0, "emergency": 0}
        agency_success = {"transit": 0, "public_works": 0, "emergency": 0}
        
        for results in dispatch_results.values():
            for agency, success in results.items():
                agency_counts[agency] += 1
                if success:
                    agency_success[agency] += 1
        
        for agency in ["transit", "public_works", "emergency"]:
            if agency_counts[agency] > 0:
                summary += f"\n{agency.replace('_', ' ').title()}: {agency_success[agency]}/{agency_counts[agency]} successful"
        
        return summary.strip()
