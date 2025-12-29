"""
Guardrails Module
Implements safety checks and content moderation for healthcare context.
"""
from typing import Dict, Tuple


class Guardrails:
    """Implements safety and content guardrails."""
    
    # High-risk keywords requiring special handling
    HIGH_RISK_KEYWORDS = [
        "suicide", "kill myself", "end my life", "self-harm",
        "overdose", "emergency", "chest pain", "can't breathe",
        "severe bleeding", "unconscious", "stroke"
    ]
    
    # Prohibited topics
    PROHIBITED_KEYWORDS = [
        "illegal drugs", "fake prescription", "forge",
        "abuse medication", "sell prescription"
    ]
    
    @classmethod
    def check_safety(cls, message: str) -> Tuple[bool, str, Dict]:
        """
        Check message for safety concerns.
        
        Args:
            message: User message to check
        
        Returns:
            Tuple of (is_safe, warning_message, metadata)
        """
        message_lower = message.lower()
        metadata = {"risk_level": "low"}
        
        # Check for prohibited content
        for keyword in cls.PROHIBITED_KEYWORDS:
            if keyword in message_lower:
                return False, "This request cannot be processed due to prohibited content.", {
                    "risk_level": "prohibited",
                    "reason": "prohibited_content"
                }
        
        # Check for high-risk keywords
        for keyword in cls.HIGH_RISK_KEYWORDS:
            if keyword in message_lower:
                emergency_message = (
                    "⚠️ **Emergency Detected**: If this is a medical emergency, "
                    "please call 911 or visit your nearest emergency room immediately. "
                    "This is a demonstration tool and cannot provide emergency care."
                )
                return True, emergency_message, {
                    "risk_level": "high",
                    "requires_emergency_warning": True
                }
        
        return True, "", metadata
    
    @classmethod
    def add_disclaimer(cls, response: str, intent: str) -> str:
        """
        Add appropriate disclaimers to responses.
        
        Args:
            response: Generated response
            intent: Detected intent
        
        Returns:
            Response with disclaimer
        """
        if intent == "clinical":
            disclaimer = (
                "\n\n---\n"
                "*This is a demonstration tool and not a substitute for professional medical advice, "
                "diagnosis, or treatment. Always seek the advice of your physician or qualified "
                "health provider with any questions regarding a medical condition.*"
            )
            return response + disclaimer
        elif intent == "vision":
            disclaimer = (
                "\n\n---\n"
                "*This image analysis is for educational purposes only and should not be used "
                "for diagnostic decisions. Consult a qualified healthcare professional for "
                "medical image interpretation.*"
            )
            return response + disclaimer
        
        return response
