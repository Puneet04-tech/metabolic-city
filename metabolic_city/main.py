"""
Main Orchestration Pipeline - Coordinates all stages of the MetabolicCity AI platform
"""

import asyncio
from datetime import datetime
from loguru import logger

from metabolic_city.config.settings import settings
from metabolic_city.ingestion.unified_spatial_join import UnifiedSpatialJoin
from metabolic_city.analysis.analysis_orchestrator import AnalysisOrchestrator
from metabolic_city.triage.triage_engine import TriageEngine
from metabolic_city.prescription.prescription_node import PrescriptionNode
from metabolic_city.prescription.narration_layer import NarrationLayer
from metabolic_city.forecasting.memory_matrix import MemoryMatrix
from metabolic_city.forecasting.trend_forecaster import TrendForecaster
from metabolic_city.feedback.feedback_processor import FeedbackProcessor
from metabolic_city.dispatch.dispatch_broker import DispatchBroker


class MetabolicCityPipeline:
    """
    Main orchestration pipeline that coordinates all four stages
    and enhanced features of the MetabolicCity AI platform.
    """
    
    def __init__(self):
        self.enabled = settings.pipeline_enabled
        self.cycle_minutes = settings.pipeline_cycle_minutes
        
        # Initialize components
        self.spatial_join = UnifiedSpatialJoin()
        self.analysis_orchestrator = AnalysisOrchestrator()
        self.triage_engine = TriageEngine()
        self.prescription_node = PrescriptionNode()
        self.narration_layer = NarrationLayer()
        self.memory_matrix = MemoryMatrix()
        self.trend_forecaster = TrendForecaster()
        self.feedback_processor = FeedbackProcessor()
        self.dispatch_broker = DispatchBroker()
        
        logger.info("MetabolicCity Pipeline initialized")
    
    async def run_single_cycle(self) -> dict:
        """
        Run a single complete pipeline cycle
        
        Returns:
            Dictionary with cycle results
        """
        logger.info("=" * 60)
        logger.info(f"Starting pipeline cycle at {datetime.utcnow().isoformat()}")
        logger.info("=" * 60)
        
        cycle_start = datetime.utcnow()
        results = {
            "cycle_start": cycle_start.isoformat(),
            "stage_1_success": False,
            "stage_2_success": False,
            "stage_3_success": False,
            "stage_4_success": False,
            "unified_data_count": 0,
            "risk_scores_count": 0,
            "alerts_generated": 0,
            "response_plans_count": 0,
            "dispatches_sent": 0
        }
        
        try:
            # Stage 1: Automated Ingestion & Unified Spatial Grid Normalization
            logger.info("STAGE 1: Ingestion & Spatial Normalization")
            unified_data = await self.spatial_join.fetch_all_data()
            results["unified_data_count"] = len(unified_data)
            results["stage_1_success"] = True
            logger.info(f"Stage 1 complete: {len(unified_data)} unified data points")
            
            # Stage 2: Parallel Context Isolation & Domain Mapping
            logger.info("STAGE 2: Parallel Analysis")
            risk_scores = await self.analysis_orchestrator.analyze_unified_data(unified_data)
            results["risk_scores_count"] = len(risk_scores)
            results["stage_2_success"] = True
            logger.info(f"Stage 2 complete: {len(risk_scores)} risk scores generated")
            
            # Stage 3: Deterministic Matrix Triage Engine
            logger.info("STAGE 3: Deterministic Triage")
            risk_scores = self.triage_engine.calculate_batch(risk_scores)
            high_risk_scores = self.triage_engine.filter_by_threshold(risk_scores)
            results["alerts_generated"] = len(high_risk_scores)
            results["stage_3_success"] = True
            logger.info(f"Stage 3 complete: {len(high_risk_scores)} alerts above threshold")
            
            # Record to memory matrix for forecasting
            self.memory_matrix.record_evaluation(risk_scores)
            
            # Stage 4: Constrained Prescriptive Blueprint Node
            logger.info("STAGE 4: Prescription & Dispatch")
            response_plans = {}
            if high_risk_scores:
                response_plans = self.prescription_node.generate_batch(high_risk_scores)
                results["response_plans_count"] = len(response_plans)
                
                # Dispatch to agencies
                dispatch_results = await self.dispatch_broker.dispatch_batch(response_plans)
                successful_dispatches = sum(
                    1 for dr in dispatch_results.values()
                    if any(success for success in dr.values())
                )
                results["dispatches_sent"] = successful_dispatches
                
                logger.info(f"Stage 4 complete: {len(response_plans)} plans generated, {successful_dispatches} dispatched")
            else:
                logger.info("Stage 4 complete: No alerts, no response plans needed")
            
            results["stage_4_success"] = True
            
            # Enhanced Features
            await self._run_enhanced_features(unified_data, risk_scores, response_plans)
            
            cycle_end = datetime.utcnow()
            results["cycle_end"] = cycle_end.isoformat()
            results["duration_seconds"] = (cycle_end - cycle_start).total_seconds()
            
            logger.info("=" * 60)
            logger.info(f"Pipeline cycle complete in {results['duration_seconds']:.2f} seconds")
            logger.info(f"Alerts: {results['alerts_generated']}, Plans: {results['response_plans_count']}, Dispatches: {results['dispatches_sent']}")
            logger.info("=" * 60)
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline cycle failed: {e}")
            results["error"] = str(e)
            return results
    
    async def _run_enhanced_features(
        self,
        unified_data: dict,
        risk_scores: dict,
        response_plans: dict
    ):
        """Run enhanced features (forecasting, feedback integration)"""
        
        # Temporal Trend Forecasting
        if settings.forecasting_enabled:
            logger.info("Running trend forecasting...")
            geohashes = list(unified_data.keys())
            forecasts = {}
            for geohash in geohashes:
                current_score = risk_scores.get(geohash)
                if current_score:
                    forecast = self.trend_forecaster.forecast_risk(
                        geohash, 
                        current_score.composite_risk_index
                    )
                    if forecast:
                        forecasts[geohash] = forecast
            alert_forecasts = self.trend_forecaster.get_alert_forecasts(geohashes)
            logger.info(f"Forecasting complete: {len(forecasts)} forecasts, {len(alert_forecasts)} geohashes likely to cross threshold")
        
        # Feedback Integration
        if settings.feedback_enabled:
            logger.info("Integrating citizen feedback...")
            # Adjust risk scores based on feedback
            for geohash, risk_score in risk_scores.items():
                adjusted = self.feedback_processor.integrate_with_risk_score(
                    geohash,
                    risk_score.composite_risk_index
                )
                risk_score.composite_risk_index = adjusted
            logger.info("Feedback integration complete")
    
    async def run_continuous(self):
        """
        Run the pipeline continuously on a scheduled cycle
        """
        if not self.enabled:
            logger.warning("Pipeline is disabled in settings")
            return
        
        logger.info(f"Starting continuous pipeline (cycle: {self.cycle_minutes} minutes)")
        
        while True:
            try:
                await self.run_single_cycle()
                
                # Wait for next cycle
                logger.info(f"Waiting {self.cycle_minutes} minutes until next cycle...")
                await asyncio.sleep(self.cycle_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Pipeline stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous pipeline: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def generate_status_report(self) -> str:
        """
        Generate a status report of the pipeline system
        
        Returns:
            Status report string
        """
        report = f"""
METABOLICCITY AI STATUS REPORT
==============================

Pipeline Configuration
----------------------
Enabled: {self.enabled}
Cycle Interval: {self.cycle_minutes} minutes
Risk Threshold: {settings.risk_threshold}

Domain Weights
--------------
Mobility: {settings.weight_mobility:.2f}
Climate: {settings.weight_climate:.2f}
Vulnerability: {settings.weight_vulnerability:.2f}

Enhanced Features
-----------------
Forecasting: {settings.forecasting_enabled}
Simulation: {settings.simulation_enabled}
Feedback Integration: {settings.feedback_enabled}
Dispatch Broker: {settings.dispatch_enabled}

Memory Matrix Statistics
-------------------------
{self._format_memory_stats()}

Feedback Statistics
--------------------
{self._format_feedback_stats()}

System Status
-------------
All components initialized and ready.
Last cycle: {datetime.utcnow().isoformat()}
"""
        return report.strip()
    
    def _format_memory_stats(self) -> str:
        """Format memory matrix statistics"""
        stats = self.memory_matrix.get_statistics()
        return f"Total Geohashes: {stats['total_geohashes']}\nTotal Records: {stats['total_records']}"
    
    def _format_feedback_stats(self) -> str:
        """Format feedback statistics"""
        stats = self.feedback_processor.get_statistics()
        return f"Total Reports: {stats['total_reports']}\nPending: {stats['pending']}\nResolved: {stats['resolved']}"


async def main():
    """Main entry point"""
    pipeline = MetabolicCityPipeline()
    
    # Print status report
    print(pipeline.generate_status_report())
    
    # Run single cycle for demonstration
    print("\nRunning single pipeline cycle...")
    results = await pipeline.run_single_cycle()
    print(f"\nCycle Results: {results}")
    
    # Uncomment below to run continuous pipeline
    # await pipeline.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
