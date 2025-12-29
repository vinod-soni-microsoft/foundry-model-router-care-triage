"""
Intent Detection Module
Classifies user messages into Admin, Clinical, or Vision intents.
"""
import re
from typing import Tuple


class IntentDetector:
    """Detects user intent from messages."""
    
    # Keywords for intent classification
    ADMIN_KEYWORDS = [
        "appointment", "schedule", "billing", "insurance", "cost", "price",
        "hours", "location", "doctor availability", "reschedule", "cancel",
        "registration", "forms", "paperwork", "contact", "office"
    ]
    
    CLINICAL_KEYWORDS = [
        "symptom", "diagnosis", "treatment", "medication", "prescription",
        "pain", "fever", "cough", "headache", "nausea", "infection",
        "disease", "condition", "procedure", "surgery", "test", "lab",
        "vitals", "blood pressure", "heart rate", "medical history"
    ]
    
    VISION_KEYWORDS = [
        "image", "photo", "picture", "scan", "x-ray", "mri", "ct scan",
        "look at this", "see this", "analyze", "examine"
    ]
    
    @classmethod
    def detect_intent(cls, message: str, has_image: bool = False) -> Tuple[str, str]:
        """
        Detect the intent from user message.
        
        Args:
            message: User message text
            has_image: Whether an image is included
        
        Returns:
            Tuple of (intent, confidence_reason)
        """
        message_lower = message.lower()
        
        # Vision intent if image is present
        if has_image:
            return "vision", "Image attached - routed to vision model"
        
        # Check for vision keywords
        vision_score = sum(1 for keyword in cls.VISION_KEYWORDS if keyword in message_lower)
        if vision_score > 0:
            return "vision", f"Vision keywords detected (score: {vision_score})"
        
        # Check for clinical keywords
        clinical_score = sum(1 for keyword in cls.CLINICAL_KEYWORDS if keyword in message_lower)
        
        # Check for admin keywords
        admin_score = sum(1 for keyword in cls.ADMIN_KEYWORDS if keyword in message_lower)
        
        # Classify based on highest score
        if clinical_score > admin_score:
            return "clinical", f"Clinical keywords detected (score: {clinical_score})"
        elif admin_score > 0:
            return "admin", f"Administrative keywords detected (score: {admin_score})"
        else:
            # Default to clinical for safety
            return "clinical", "Default to clinical for healthcare context"
