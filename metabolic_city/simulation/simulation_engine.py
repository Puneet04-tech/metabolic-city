"""
Simulation Engine - Runs what-if scenarios and analyzes cascading effects
"""

import asyncio
from typing import Dict, Optional
from loguru import logger

from metabolic_city.utils.data_models import SimulationScenario, RiskScore
from metabolic_city.analysis.mobility_node import MobilityNode
from metabolic_city.analysis.climate_node import ClimateNode
from metabolic_city.analysis.vulnerability_node import VulnerabilityNode
from metabolic_city.triage.triage_engine import TriageEngine
from metabolic_city.simulation.scenario_builder import ScenarioBuilder


class SimulationEngine:
    """
    Runs simulation scenarios through isolated agent loops to map
    ripple effects across different domains.
    """
    
    def __init__(self):
        self.scenario_builder = ScenarioBuilder()
        self.mobility_node = MobilityNode()
        self.climate_node = ClimateNode()
        self.vulnerability_node = VulnerabilityNode()
        self.triage_engine = TriageEngine()
        
        if not hasattr(self, 'enabled'):
            from metabolic_city.config.settings import settings
            self.enabled = settings.simulation_enabled
    
    async def run_scenario(
        self,
        scenario: SimulationScenario
    ) -> SimulationScenario:
        """
        Run a simulation scenario through the analysis pipeline
        
        Args:
            scenario: SimulationScenario to run
            
        Returns:
            Updated scenario with results
        """
        logger.info(f"Running scenario: {scenario.name}")
        
        # Evaluate baseline
        baseline_risk = await self._evaluate_data_point(scenario.baseline_data)
        
        # Evaluate modified data
        modified_risk = await self._evaluate_data_point(scenario.modified_data)
        
        # Calculate impact
        impact = {
            "baseline_composite_risk": baseline_risk.composite_risk_index,
            "modified_composite_risk": modified_risk.composite_risk_index,
            "risk_change": modified_risk.composite_risk_index - baseline_risk.composite_risk_index,
            "baseline_mobility_score": baseline_risk.mobility_score,
            "modified_mobility_score": modified_risk.mobility_score,
            "baseline_climate_score": baseline_risk.climate_score,
            "modified_climate_score": modified_risk.climate_score,
            "baseline_vulnerability_score": baseline_risk.vulnerability_score,
            "modified_vulnerability_score": modified_risk.vulnerability_score,
            "risk_level_change": self._compare_risk_levels(baseline_risk.risk_level, modified_risk.risk_level)
        }
        
        # Update scenario with results
        scenario.results = impact
        
        logger.info(f"Scenario complete: Risk change = {impact['risk_change']:+.2f}")
        return scenario
    
    async def _evaluate_data_point(self, data_point) -> RiskScore:
        """
        Evaluate a unified data point through the analysis pipeline
        
        Args:
            data_point: UnifiedDataPoint to evaluate
            
        Returns:
            RiskScore object
        """
        # Run isolated nodes
        mobility_score = self.mobility_node.evaluate(data_point.mobility)
        climate_score = self.climate_node.evaluate(data_point.climate)
        vulnerability_score = self.vulnerability_node.evaluate(data_point.demographic)
        
        # Create risk score
        risk_score = RiskScore(
            geohash=data_point.geohash,
            timestamp=data_point.timestamp,
            mobility_score=mobility_score,
            climate_score=climate_score,
            vulnerability_score=vulnerability_score,
            composite_risk_index=0.0,
            risk_level="pending"
        )
        
        # Calculate composite risk
        risk_score = self.triage_engine.calculate_composite_risk(risk_score)
        
        return risk_score
    
    def _compare_risk_levels(self, baseline: str, modified: str) -> str:
        """
        Compare risk levels and return change description
        
        Args:
            baseline: Baseline risk level
            modified: Modified risk level
            
        Returns:
            Description of change
        """
        levels = ["low", "medium", "high", "critical"]
        
        try:
            baseline_idx = levels.index(baseline)
            modified_idx = levels.index(modified)
            
            if modified_idx > baseline_idx:
                return "increased"
            elif modified_idx < baseline_idx:
                return "decreased"
            else:
                return "unchanged"
        except ValueError:
            return "unknown"
    
    async def run_batch_scenarios(
        self,
        scenarios: list
    ) -> Dict[str, SimulationScenario]:
        """
        Run multiple scenarios concurrently
        
        Args:
            scenarios: List of SimulationScenario objects
            
        Returns:
            Dictionary mapping scenario ID to updated scenario
        """
        logger.info(f"Running {len(scenarios)} scenarios concurrently")
        
        # Run scenarios concurrently
        results = await asyncio.gather(
            *[self.run_scenario(scenario) for scenario in scenarios],
            return_exceptions=True
        )
        
        # Handle exceptions
        updated_scenarios = {}
        for scenario, result in zip(scenarios, results):
            if isinstance(result, Exception):
                logger.error(f"Scenario {scenario.scenario_id} failed: {result}")
                scenario.results = {"error": str(result)}
            else:
                updated_scenarios[scenario.scenario_id] = result
        
        return updated_scenarios
    
    def generate_simulation_report(self, scenario: SimulationScenario) -> str:
        """
        Generate natural-language report of simulation results
        
        Args:
            scenario: SimulationScenario with results
            
        Returns:
            Report string
        """
        if not scenario.results:
            return "Simulation results not available."
        
        results = scenario.results
        
        report = f"""
SIMULATION REPORT
=================

Scenario: {scenario.name}
Description: {scenario.description}
Geohash: {scenario.baseline_data.geohash}

PARAMETERS MODIFIED
-------------------
{self._format_parameters(scenario.parameters)}

RISK ANALYSIS
-------------
Baseline Composite Risk: {results['baseline_composite_risk']:.2f}/10.0
Modified Composite Risk: {results['modified_composite_risk']:.2f}/10.0
Risk Change: {results['risk_change']:+.2f}

Domain-Specific Changes:
- Mobility: {results['baseline_mobility_score']:.2f} → {results['modified_mobility_score']:.2f} ({results['modified_mobility_score'] - results['baseline_mobility_score']:+.2f})
- Climate: {results['baseline_climate_score']:.2f} → {results['modified_climate_score']:.2f} ({results['modified_climate_score'] - results['baseline_climate_score']:+.2f})
- Vulnerability: {results['baseline_vulnerability_score']:.2f} → {results['modified_vulnerability_score']:.2f} ({results['modified_vulnerability_score'] - results['baseline_vulnerability_score']:+.2f})

Risk Level Change: {results['risk_level_change'].upper()}

RECOMMENDATION
--------------
{self._generate_recommendation(results)}
"""
        return report.strip()
    
    def _format_parameters(self, parameters: Dict) -> str:
        """Format parameters for display"""
        lines = []
        for category, mods in parameters.items():
            lines.append(f"{category.replace('_', ' ').title()}:")
            for key, value in mods.items():
                lines.append(f"  - {key}: {value}")
        return "\n".join(lines)
    
    def _generate_recommendation(self, results: Dict) -> str:
        """Generate recommendation based on results"""
        risk_change = results['risk_change']
        
        if risk_change > 3.0:
            return "HIGH IMPACT: This change significantly increases risk. Recommend against implementation or implement strong mitigation measures."
        elif risk_change > 1.5:
            return "MODERATE IMPACT: This change increases risk. Review mitigation strategies before implementation."
        elif risk_change > 0.5:
            return "LOW IMPACT: This change slightly increases risk. Monitor closely during implementation."
        elif risk_change > -0.5:
            return "NEUTRAL IMPACT: This change has minimal effect on risk. Proceed with standard monitoring."
        elif risk_change > -1.5:
            return "BENEFICIAL: This change slightly reduces risk. Consider implementation."
        else:
            return "HIGHLY BENEFICIAL: This change significantly reduces risk. Recommend implementation."
