"""
Feedback Processor - Integrates citizen reports into the main pipeline
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from metabolic_city.utils.data_models import CitizenReport
from metabolic_city.feedback.nlp_extractor import NLPExtractor
from metabolic_city.config.settings import settings


class FeedbackProcessor:
    """
    Processes direct digital communication from citizens and integrates
    it into the main scoring matrix as a supplementary verification layer.
    """
    
    def __init__(self):
        self.nlp_extractor = NLPExtractor()
        self.enabled = settings.feedback_enabled
        self.storage_path = Path("metabolic_city/data/citizen_reports.json")
        
        if not self.enabled:
            logger.warning("Feedback integration is disabled in settings")
        
        self._load_reports()
    
    def _load_reports(self):
        """Load stored reports from file"""
        if not self.storage_path.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.reports: Dict[str, CitizenReport] = {}
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                # Convert dicts back to CitizenReport objects
                self.reports = {
                    report_id: CitizenReport(**report_data)
                    for report_id, report_data in data.items()
                }
            logger.info(f"Loaded {len(self.reports)} citizen reports")
        except Exception as e:
            logger.error(f"Error loading reports: {e}")
            self.reports = {}
    
    def _save_reports(self):
        """Save reports to file"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                report_id: report.dict()
                for report_id, report in self.reports.items()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Saved citizen reports to storage")
        except Exception as e:
            logger.error(f"Error saving reports: {e}")
    
    def ingest_report(self, report_text: str, contact_info: Optional[str] = None) -> CitizenReport:
        """
        Ingest a new citizen report
        
        Args:
            report_text: Raw report text
            contact_info: Optional contact information
            
        Returns:
            Processed CitizenReport object
        """
        if not self.enabled:
            logger.warning("Feedback integration is disabled")
            raise RuntimeError("Feedback integration is disabled")
        
        # Generate report ID
        report_id = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(self.reports)}"
        
        # Process with NLP
        report = self.nlp_extractor.process_report(report_text, report_id)
        
        # Add contact info if provided
        if contact_info:
            report.contact_info = contact_info
        
        # Store report
        self.reports[report_id] = report
        
        # Check for duplicates
        self._check_for_duplicates()
        
        # Save to storage
        self._save_reports()
        
        logger.info(f"Ingested new citizen report: {report_id}")
        return report
    
    def _check_for_duplicates(self):
        """Check for duplicate reports and mark them"""
        report_list = list(self.reports.values())
        duplicates = self.nlp_extractor.detect_duplicates(report_list)
        
        for report_id, duplicate_of in duplicates.items():
            if report_id in self.reports:
                self.reports[report_id].duplicate_of = duplicate_of
                self.reports[report_id].status = "duplicate"
    
    def get_reports_by_geohash(self, geohash: str) -> List[CitizenReport]:
        """
        Get all reports for a specific geohash
        
        Args:
            geohash: Geohash string
            
        Returns:
            List of CitizenReport objects
        """
        return [
            report for report in self.reports.values()
            if report.geohash == geohash and report.status != "duplicate"
        ]
    
    def get_recent_reports(self, hours: int = 24) -> List[CitizenReport]:
        """
        Get reports from the last N hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent CitizenReport objects
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            report for report in self.reports.values()
            if report.timestamp >= cutoff and report.status != "duplicate"
        ]
    
    def get_urgency_summary(self, geohash: str) -> Dict[str, int]:
        """
        Get summary of report urgency for a geohash
        
        Args:
            geohash: Geohash string
            
        Returns:
            Dictionary with urgency counts
        """
        reports = self.get_reports_by_geohash(geohash)
        
        summary = {
            "high": 0,
            "medium": 0,
            "low": 0,
            "total": len(reports)
        }
        
        for report in reports:
            summary[report.urgency] += 1
        
        return summary
    
    def integrate_with_risk_score(self, geohash: str, base_risk_score: float) -> float:
        """
        Integrate citizen reports into risk score as verification layer
        
        Args:
            geohash: Geohash string
            base_risk_score: Base risk score from main pipeline
            
        Returns:
            Adjusted risk score
        """
        if not self.enabled:
            return base_risk_score
        
        urgency_summary = self.get_urgency_summary(geohash)
        
        # Calculate adjustment based on citizen reports
        high_count = urgency_summary["high"]
        medium_count = urgency_summary["medium"]
        
        # High urgency reports increase risk
        adjustment = (high_count * 0.5) + (medium_count * 0.2)
        
        # Cap adjustment
        adjustment = min(adjustment, 2.0)
        
        adjusted_score = base_risk_score + adjustment
        adjusted_score = min(adjusted_score, 10.0)
        
        if adjustment > 0:
            logger.debug(f"Adjusted risk for {geohash}: {base_risk_score:.2f} → {adjusted_score:.2f} (+{adjustment:.2f} from citizen reports)")
        
        return adjusted_score
    
    def mark_resolved(self, report_id: str):
        """
        Mark a report as resolved
        
        Args:
            report_id: Report identifier
        """
        if report_id in self.reports:
            self.reports[report_id].status = "resolved"
            self._save_reports()
            logger.info(f"Marked report {report_id} as resolved")
    
    def get_statistics(self) -> Dict:
        """
        Get feedback processing statistics
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.reports)
        pending = sum(1 for r in self.reports.values() if r.status == "pending")
        resolved = sum(1 for r in self.reports.values() if r.status == "resolved")
        duplicate = sum(1 for r in self.reports.values() if r.status == "duplicate")
        
        return {
            "total_reports": total,
            "pending": pending,
            "resolved": resolved,
            "duplicate": duplicate,
            "unique_reports": total - duplicate
        }
