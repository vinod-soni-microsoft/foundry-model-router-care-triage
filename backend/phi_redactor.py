"""
PHI Redaction Module
Detects and redacts Protected Health Information (PHI) from user messages.
"""
import re
from typing import Tuple, List


class PHIRedactor:
    """Detects and redacts PHI from text."""
    
    # Patterns for PHI detection
    PATTERNS = {
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "mrn": r'\b(?:MRN|medical record number)[\s:]?\d{6,10}\b',
        "date_of_birth": r'\b(?:DOB|date of birth)[\s:]?\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        "address": r'\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr|boulevard|blvd)\b',
    }
    
    # Common name patterns (simplified - in production use NER)
    NAME_PATTERNS = [
        r'\b(?:my name is|I am|I\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
        r'\bpatient:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
    ]
    
    @classmethod
    def redact_phi(cls, text: str) -> Tuple[str, bool, List[str]]:
        """
        Redact PHI from text.
        
        Args:
            text: Input text potentially containing PHI
        
        Returns:
            Tuple of (redacted_text, has_phi, phi_types_detected)
        """
        redacted_text = text
        phi_types_detected = []
        
        # Redact each PHI pattern
        for phi_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, redacted_text, re.IGNORECASE)
            if matches:
                phi_types_detected.append(phi_type)
                redacted_text = re.sub(
                    pattern,
                    f"[REDACTED_{phi_type.upper()}]",
                    redacted_text,
                    flags=re.IGNORECASE
                )
        
        # Redact names
        for name_pattern in cls.NAME_PATTERNS:
            matches = re.findall(name_pattern, redacted_text, re.IGNORECASE)
            if matches:
                phi_types_detected.append("name")
                redacted_text = re.sub(
                    name_pattern,
                    lambda m: m.group(0).replace(m.group(1), "[REDACTED_NAME]"),
                    redacted_text,
                    flags=re.IGNORECASE
                )
        
        has_phi = len(phi_types_detected) > 0
        
        return redacted_text, has_phi, phi_types_detected
