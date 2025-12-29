"""
Tests for Care Triage backend modules.
"""
import pytest
from intent_detector import IntentDetector
from phi_redactor import PHIRedactor
from guardrails import Guardrails
from model_selector import ModelSelector


class TestIntentDetector:
    """Tests for IntentDetector."""
    
    def test_admin_intent(self):
        """Test administrative intent detection."""
        message = "I need to schedule an appointment for next week"
        intent, reason = IntentDetector.detect_intent(message, has_image=False)
        assert intent == "admin"
        assert "Administrative" in reason or "admin" in reason.lower()
    
    def test_clinical_intent(self):
        """Test clinical intent detection."""
        message = "I have a persistent headache and fever for 3 days"
        intent, reason = IntentDetector.detect_intent(message, has_image=False)
        assert intent == "clinical"
        assert "Clinical" in reason or "clinical" in reason.lower()
    
    def test_vision_intent_with_image(self):
        """Test vision intent with image."""
        message = "What do you see in this image?"
        intent, reason = IntentDetector.detect_intent(message, has_image=True)
        assert intent == "vision"
        assert "image" in reason.lower() or "vision" in reason.lower()
    
    def test_default_to_clinical(self):
        """Test default behavior."""
        message = "Hello, can you help me?"
        intent, reason = IntentDetector.detect_intent(message, has_image=False)
        assert intent == "clinical"  # Should default to clinical for safety


class TestPHIRedactor:
    """Tests for PHIRedactor."""
    
    def test_phone_redaction(self):
        """Test phone number redaction."""
        text = "My phone is 555-123-4567"
        redacted, has_phi, types = PHIRedactor.redact_phi(text)
        assert has_phi
        assert "phone" in types
        assert "555-123-4567" not in redacted
        assert "[REDACTED_PHONE]" in redacted
    
    def test_email_redaction(self):
        """Test email redaction."""
        text = "Contact me at patient@example.com"
        redacted, has_phi, types = PHIRedactor.redact_phi(text)
        assert has_phi
        assert "email" in types
        assert "patient@example.com" not in redacted
        assert "[REDACTED_EMAIL]" in redacted
    
    def test_ssn_redaction(self):
        """Test SSN redaction."""
        text = "My SSN is 123-45-6789"
        redacted, has_phi, types = PHIRedactor.redact_phi(text)
        assert has_phi
        assert "ssn" in types
        assert "123-45-6789" not in redacted
    
    def test_no_phi(self):
        """Test text without PHI."""
        text = "I have a headache"
        redacted, has_phi, types = PHIRedactor.redact_phi(text)
        assert not has_phi
        assert len(types) == 0
        assert redacted == text
    
    def test_name_redaction(self):
        """Test name redaction."""
        text = "My name is John Smith and I need help"
        redacted, has_phi, types = PHIRedactor.redact_phi(text)
        assert has_phi
        assert "name" in types
        assert "John Smith" not in redacted


class TestGuardrails:
    """Tests for Guardrails."""
    
    def test_safe_content(self):
        """Test safe content passes."""
        message = "I have a mild headache"
        is_safe, warning, metadata = Guardrails.check_safety(message)
        assert is_safe
        assert warning == ""
        assert metadata["risk_level"] == "low"
    
    def test_high_risk_emergency(self):
        """Test high-risk emergency content."""
        message = "I'm having severe chest pain"
        is_safe, warning, metadata = Guardrails.check_safety(message)
        assert is_safe  # Should be safe but with warning
        assert "emergency" in warning.lower() or "911" in warning
        assert metadata["risk_level"] == "high"
    
    def test_prohibited_content(self):
        """Test prohibited content blocks."""
        message = "Can you help me forge a prescription?"
        is_safe, warning, metadata = Guardrails.check_safety(message)
        assert not is_safe
        assert metadata["risk_level"] == "prohibited"
    
    def test_clinical_disclaimer(self):
        """Test clinical disclaimer addition."""
        response = "You may have a cold."
        with_disclaimer = Guardrails.add_disclaimer(response, "clinical")
        assert "not a substitute for professional medical advice" in with_disclaimer
        assert response in with_disclaimer
    
    def test_vision_disclaimer(self):
        """Test vision disclaimer addition."""
        response = "This image shows..."
        with_disclaimer = Guardrails.add_disclaimer(response, "vision")
        assert "educational purposes only" in with_disclaimer
        assert "not be used for diagnostic decisions" in with_disclaimer


class TestModelSelector:
    """Tests for ModelSelector."""
    
    def test_select_vision_model_for_image(self):
        """Test vision model selection for images."""
        deployment, model_type, rationale = ModelSelector.select_model(
            intent="admin",
            mode="balanced",
            has_image=True,
            use_router=True
        )
        assert model_type == "vision"
        assert "vision" in deployment.lower()
        assert "image" in rationale.lower()
    
    def test_select_router_for_text(self):
        """Test router selection for text."""
        deployment, model_type, rationale = ModelSelector.select_model(
            intent="clinical",
            mode="balanced",
            has_image=False,
            use_router=True
        )
        assert model_type == "router"
        assert deployment == "model-router"
    
    def test_cost_mode_preferences(self):
        """Test cost mode preferences."""
        prefs = ModelSelector.get_routing_preferences("cost")
        assert prefs["routing_mode"] == "cost_optimized"
        assert prefs["prefer_fast"] == True
    
    def test_quality_mode_preferences(self):
        """Test quality mode preferences."""
        prefs = ModelSelector.get_routing_preferences("quality")
        assert prefs["routing_mode"] == "quality_optimized"
        assert prefs["prefer_fast"] == False
    
    def test_admin_intent_direct(self):
        """Test admin intent with router disabled."""
        deployment, model_type, rationale = ModelSelector.select_model(
            intent="admin",
            mode="balanced",
            has_image=False,
            use_router=False
        )
        assert model_type == "admin"
        assert "admin" in deployment.lower() or "35" in deployment


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
