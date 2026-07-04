"""
NLP Extractor - Processes citizen reports using natural language processing
"""

import re
from typing import Dict, Optional, List
from loguru import logger

from metabolic_city.utils.data_models import CitizenReport
from metabolic_city.utils.geohash_utils import encode_geohash


class NLPExtractor:
    """
    Extracts location, issue type, and urgency from citizen reports
    using natural language processing techniques.
    """
    
    def __init__(self):
        self.issue_keywords = {
            "transit": ["bus", "train", "subway", "metro", "delay", "late", "cancelled", "route", "station"],
            "weather": ["rain", "flood", "heat", "cold", "snow", "wind", "storm", "temperature"],
            "infrastructure": ["road", "bridge", "sidewalk", "light", "power", "water", "sewer"],
            "safety": ["crime", "violence", "assault", "theft", "dangerous", "unsafe"],
            "health": ["medical", "hospital", "injury", "sick", "emergency", "ambulance"],
            "noise": ["loud", "noise", "construction", "party", "music"]
        }
        
        self.urgency_keywords = {
            "high": ["emergency", "urgent", "critical", "danger", "immediate", "life-threatening"],
            "medium": ["important", "soon", "issue", "problem", "concern"],
            "low": ["minor", "inconvenience", "annoyance", "suggestion"]
        }
    
    def extract_location(self, text: str) -> Optional[Dict[str, any]]:
        """
        Extract location information from text
        
        Args:
            text: Report text
            
        Returns:
            Dictionary with location info or None
        """
        # Look for address patterns
        address_pattern = r'\d+\s+[A-Za-z\s]+(?:Street|St|Ave|Avenue|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        
        # Look for intersection patterns
        intersection_pattern = r'([A-Za-z\s]+)\s+(?:and|&|at)\s+([A-Za-z\s]+)'
        intersection_match = re.search(intersection_pattern, text, re.IGNORECASE)
        
        # Look for landmark references
        landmarks = ["school", "park", "library", "hospital", "station", "mall", "center"]
        landmark_match = None
        for landmark in landmarks:
            if landmark in text.lower():
                landmark_match = landmark
                break
        
        location_info = {}
        
        if address_match:
            location_info["address"] = address_match.group()
        
        if intersection_match:
            location_info["intersection"] = f"{intersection_match.group(1)} & {intersection_match.group(2)}"
        
        if landmark_match:
            location_info["landmark"] = landmark_match
        
        return location_info if location_info else None
    
    def extract_issue_type(self, text: str) -> str:
        """
        Determine issue type from text
        
        Args:
            text: Report text
            
        Returns:
            Issue type string
        """
        text_lower = text.lower()
        
        scores = {}
        for issue_type, keywords in self.issue_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[issue_type] = score
        
        # Return issue type with highest score
        if scores:
            return max(scores, key=scores.get)
        
        return "general"
    
    def extract_urgency(self, text: str) -> str:
        """
        Determine urgency level from text
        
        Args:
            text: Report text
            
        Returns:
            Urgency level: high, medium, or low
        """
        text_lower = text.lower()
        
        for urgency, keywords in self.urgency_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return urgency
        
        return "medium"
    
    def extract_coordinates(self, text: str) -> Optional[tuple]:
        """
        Extract coordinates from text if present
        
        Args:
            text: Report text
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        # Look for coordinate patterns
        coord_pattern = r'(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)'
        match = re.search(coord_pattern, text)
        
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                # Validate coordinate ranges
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            except ValueError:
                pass
        
        return None
    
    def process_report(self, report_text: str, report_id: str) -> CitizenReport:
        """
        Process citizen report text into structured data
        
        Args:
            report_text: Raw report text
            report_id: Report identifier
            
        Returns:
            CitizenReport object
        """
        # Extract components
        location = self.extract_location(report_text)
        coordinates = self.extract_coordinates(report_text)
        issue_type = self.extract_issue_type(report_text)
        urgency = self.extract_urgency(report_text)
        
        # Determine geohash
        if coordinates:
            geohash = encode_geohash(coordinates[0], coordinates[1], precision=6)
        else:
            # Use placeholder if no coordinates
            geohash = "unknown"
        
        report = CitizenReport(
            report_id=report_id,
            geohash=geohash,
            timestamp=datetime.utcnow(),
            report_type=issue_type,
            description=report_text,
            urgency=urgency,
            contact_info=None,
            status="pending",
            duplicate_of=None
        )
        
        logger.debug(f"Processed report {report_id}: {issue_type} (urgency: {urgency})")
        return report
    
    def detect_duplicates(self, reports: List[CitizenReport]) -> Dict[str, str]:
        """
        Detect duplicate reports and group them
        
        Args:
            reports: List of CitizenReport objects
            
        Returns:
            Dictionary mapping report_id to duplicate_of report_id
        """
        duplicates = {}
        
        # Simple duplicate detection based on geohash and issue type
        # In production, this would use more sophisticated similarity matching
        report_groups = {}
        
        for report in reports:
            key = f"{report.geohash}_{report.report_type}"
            if key not in report_groups:
                report_groups[key] = []
            report_groups[key].append(report)
        
        # Mark duplicates (keep the oldest as primary)
        for key, group in report_groups.items():
            if len(group) > 1:
                # Sort by timestamp
                group.sort(key=lambda r: r.timestamp)
                primary = group[0]
                
                for duplicate in group[1:]:
                    duplicates[duplicate.report_id] = primary.report_id
        
        logger.info(f"Detected {len(duplicates)} duplicate reports")
        return duplicates
