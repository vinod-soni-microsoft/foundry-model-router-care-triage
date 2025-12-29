"""
Router Observability Module
Tracks and logs model routing decisions, telemetry, and performance metrics.
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
log_file = Path(__file__).parent / "router.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RouterObservability:
    """Tracks and logs routing decisions and telemetry."""
    
    @staticmethod
    def log_routing_decision(
        intent: str,
        mode: str,
        model_chosen: str,
        tokens: Optional[Dict[str, int]],
        latency_ms: float,
        rationale: str,
        has_phi: bool = False,
        has_image: bool = False,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a routing decision with full telemetry.
        
        Args:
            intent: Detected intent (admin/clinical/vision)
            mode: Routing mode (balanced/cost/quality)
            model_chosen: The model that was selected
            tokens: Token usage dict with prompt_tokens, completion_tokens, total_tokens
            latency_ms: Request latency in milliseconds
            rationale: Explanation of routing decision
            has_phi: Whether PHI was detected/redacted
            has_image: Whether request included image
            additional_context: Optional additional metadata
        
        Returns:
            Telemetry dict for API response
        """
        telemetry = {
            "timestamp": datetime.utcnow().isoformat(),
            "intent": intent,
            "routing_mode": mode,
            "model_chosen": model_chosen,
            "tokens": tokens or {},
            "latency_ms": round(latency_ms, 2),
            "rationale": rationale,
            "has_phi": has_phi,
            "has_image": has_image
        }
        
        if additional_context:
            telemetry["additional_context"] = additional_context
        
        # Log to file and console
        logger.info(f"ROUTING_DECISION: {json.dumps(telemetry, indent=2)}")
        
        return telemetry
    
    @staticmethod
    def log_error(
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log an error with context."""
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        logger.error(f"ERROR: {json.dumps(error_data, indent=2)}")
    
    @staticmethod
    def log_phi_detection(
        original_message: str,
        redacted_message: str,
        phi_types_detected: list
    ):
        """Log PHI detection and redaction."""
        phi_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "phi_types_detected": phi_types_detected,
            "redaction_applied": True,
            "original_length": len(original_message),
            "redacted_length": len(redacted_message)
        }
        logger.warning(f"PHI_DETECTED: {json.dumps(phi_log, indent=2)}")
