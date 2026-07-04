"""
Memory Matrix - Historical data storage for trend analysis
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from metabolic_city.utils.data_models import RiskScore
from metabolic_city.config.settings import settings


class MemoryMatrix:
    """
    Stores historical risk evaluations for trend forecasting.
    Creates a detailed historical record of community strain.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize memory matrix
        
        Args:
            storage_path: Path to storage file
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path("metabolic_city/data/memory_matrix.json")
        
        self.history: Dict[str, List[Dict]] = {}
        self._load_history()
    
    def _load_history(self):
        """Load historical data from file"""
        if not self.storage_path.exists():
            logger.warning(f"Memory matrix file not found at {self.storage_path}, creating new storage")
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_history()
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                self.history = json.load(f)
            logger.info(f"Loaded historical data for {len(self.history)} geohashes")
        except Exception as e:
            logger.error(f"Error loading memory matrix: {e}")
            self.history = {}
    
    def _save_history(self):
        """Save historical data to file"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.debug(f"Saved memory matrix to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving memory matrix: {e}")
    
    def record_evaluation(self, risk_scores: Dict[str, RiskScore]):
        """
        Record risk evaluation results to memory matrix
        
        Args:
            risk_scores: Dictionary mapping geohash to RiskScore
        """
        timestamp = datetime.utcnow().isoformat()
        
        for geohash, risk_score in risk_scores.items():
            if geohash not in self.history:
                self.history[geohash] = []
            
            # Convert RiskScore to serializable dict
            record = {
                "timestamp": timestamp,
                "mobility_score": risk_score.mobility_score,
                "climate_score": risk_score.climate_score,
                "vulnerability_score": risk_score.vulnerability_score,
                "composite_risk_index": risk_score.composite_risk_index,
                "risk_level": risk_score.risk_level
            }
            
            self.history[geohash].append(record)
        
        # Prune old records (keep last 30 days)
        self._prune_old_records()
        
        # Save to disk
        self._save_history()
        
        logger.info(f"Recorded {len(risk_scores)} evaluations to memory matrix")
    
    def _prune_old_records(self, days_to_keep: int = 30):
        """
        Remove records older than specified days
        
        Args:
            days_to_keep: Number of days to retain
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        cutoff_iso = cutoff_date.isoformat()
        
        for geohash in self.history:
            self.history[geohash] = [
                record for record in self.history[geohash]
                if record["timestamp"] >= cutoff_iso
            ]
        
        logger.debug(f"Pruned records older than {days_to_keep} days")
    
    def get_history(self, geohash: str, hours: int = 24) -> List[Dict]:
        """
        Get historical data for a specific geohash
        
        Args:
            geohash: Geohash string
            hours: Number of hours of history to retrieve
            
        Returns:
            List of historical records
        """
        if geohash not in self.history:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)
        cutoff_iso = cutoff_date.isoformat()
        
        return [
            record for record in self.history[geohash]
            if record["timestamp"] >= cutoff_iso
        ]
    
    def get_all_history(self, hours: int = 24) -> Dict[str, List[Dict]]:
        """
        Get historical data for all geohashes
        
        Args:
            hours: Number of hours of history to retrieve
            
        Returns:
            Dictionary mapping geohash to list of records
        """
        result = {}
        for geohash in self.history:
            result[geohash] = self.get_history(geohash, hours)
        return result
    
    def get_trend(self, geohash: str, hours: int = 24) -> Dict[str, float]:
        """
        Calculate trend metrics for a geohash
        
        Args:
            geohash: Geohash string
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with trend metrics
        """
        records = self.get_history(geohash, hours)
        
        if len(records) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend
        recent_scores = [r["composite_risk_index"] for r in records]
        avg_score = sum(recent_scores) / len(recent_scores)
        
        # Compare first and last
        first_score = recent_scores[0]
        last_score = recent_scores[-1]
        change = last_score - first_score
        
        # Determine trend direction
        if change > 1.0:
            trend = "increasing"
        elif change < -1.0:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "average_score": avg_score,
            "change": change,
            "min_score": min(recent_scores),
            "max_score": max(recent_scores),
            "data_points": len(records)
        }
    
    def get_statistics(self) -> Dict:
        """
        Get overall memory matrix statistics
        
        Returns:
            Dictionary with statistics
        """
        total_records = sum(len(records) for records in self.history.values())
        geohash_count = len(self.history)
        
        return {
            "total_geohashes": geohash_count,
            "total_records": total_records,
            "average_records_per_geohash": total_records / geohash_count if geohash_count > 0 else 0
        }
