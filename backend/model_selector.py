"""
Model Selection Module
Determines the appropriate model deployment based on intent, mode, and requirements.
"""
from typing import Dict, Tuple


class ModelSelector:
    """Selects appropriate model based on routing requirements."""
    
    # Model deployment configurations
    # These would be configured based on your actual Foundry/Azure OpenAI deployments
    MODELS = {
        "router": {
            "deployment": "model-router",  # Foundry Model Router deployment
            "use_case": "general",
            "supports_vision": False
        },
        "admin": {
            "deployment": "gpt-35-turbo",  # Fast, cost-effective for admin
            "use_case": "administrative",
            "supports_vision": False
        },
        "clinical": {
            "deployment": "gpt-4",  # Higher quality for clinical
            "use_case": "clinical",
            "supports_vision": False
        },
        "vision": {
            "deployment": "gpt-4-vision",  # Vision-capable model
            "use_case": "vision",
            "supports_vision": True
        }
    }
    
    @classmethod
    def select_model(
        cls,
        intent: str,
        mode: str,
        has_image: bool,
        use_router: bool = True
    ) -> Tuple[str, str, str]:
        """
        Select appropriate model based on requirements.
        
        Args:
            intent: Detected intent (admin/clinical/vision)
            mode: Routing mode (balanced/cost/quality)
            has_image: Whether request includes image
            use_router: Whether to use Foundry Model Router (default: True)
        
        Returns:
            Tuple of (deployment_name, model_type, rationale)
        """
        # Vision always requires vision-capable model
        if has_image or intent == "vision":
            return (
                cls.MODELS["vision"]["deployment"],
                "vision",
                "Image present - routing to vision-capable model"
            )
        
        # Use router for text-based requests if enabled
        if use_router and not has_image:
            if mode == "cost":
                rationale = "Cost-optimized routing via Model Router"
            elif mode == "quality":
                rationale = "Quality-optimized routing via Model Router"
            else:  # balanced
                rationale = "Balanced routing via Model Router"
            
            return (
                cls.MODELS["router"]["deployment"],
                "router",
                rationale
            )
        
        # Fallback to specific deployments based on intent
        if intent == "admin":
            return (
                cls.MODELS["admin"]["deployment"],
                "admin",
                "Administrative query - using fast, cost-effective model"
            )
        elif intent == "clinical":
            return (
                cls.MODELS["clinical"]["deployment"],
                "clinical",
                "Clinical query - using high-quality model"
            )
        
        # Default fallback
        return (
            cls.MODELS["router"]["deployment"],
            "router",
            "Default routing via Model Router"
        )
    
    @classmethod
    def get_routing_preferences(cls, mode: str) -> Dict:
        """
        Get routing preferences for Model Router based on mode.
        
        Args:
            mode: Routing mode (balanced/cost/quality)
        
        Returns:
            Dict with routing preferences
        """
        if mode == "cost":
            return {
                "routing_mode": "cost_optimized",
                "allow_fallback": True,
                "prefer_fast": True
            }
        elif mode == "quality":
            return {
                "routing_mode": "quality_optimized",
                "allow_fallback": False,
                "prefer_fast": False
            }
        else:  # balanced
            return {
                "routing_mode": "balanced",
                "allow_fallback": True,
                "prefer_fast": False
            }
