"""
Foundry Client Module
Handles communication with Microsoft Foundry Model Router and Azure OpenAI deployments.
"""
import os
import time
from typing import Dict, List, Optional, Any, Tuple
import httpx
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class FoundryClient:
    """Client for Microsoft Foundry Model Router and Azure OpenAI."""
    
    def __init__(self):
        """Initialize Foundry and Azure OpenAI clients."""
        # Foundry Model Router configuration
        self.foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT", "")
        self.foundry_api_key = os.getenv("FOUNDRY_API_KEY", "")
        self.foundry_deployment = os.getenv("FOUNDRY_DEPLOYMENT_NAME", "model-router")
        
        # Azure OpenAI configuration (fallback)
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Initialize Azure OpenAI client
        if self.azure_endpoint:
            # Use Azure AD authentication (DefaultAzureCredential)
            # Falls back to API key if credential fails
            try:
                token_provider = get_bearer_token_provider(
                    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
                )
                self.azure_client = AzureOpenAI(
                    api_version=self.azure_api_version,
                    azure_endpoint=self.azure_endpoint,
                    azure_ad_token_provider=token_provider
                )
            except Exception:
                # Fallback to API key if Azure AD fails
                if self.azure_api_key:
                    self.azure_client = AzureOpenAI(
                        api_key=self.azure_api_key,
                        api_version=self.azure_api_version,
                        azure_endpoint=self.azure_endpoint
                    )
                else:
                    self.azure_client = None
        else:
            self.azure_client = None
    
    def call_router(
        self,
        messages: List[Dict[str, Any]],
        mode: str = "balanced",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Call Foundry Model Router via Azure OpenAI client.
        Model Router is deployed as an Azure OpenAI deployment.
        
        Args:
            messages: List of message dicts with role and content
            mode: Routing mode (balanced/cost/quality)
            max_tokens: Maximum tokens for completion
            temperature: Sampling temperature
        
        Returns:
            Tuple of (response_text, telemetry_dict)
        """
        if not self.azure_client:
            raise ValueError("Azure OpenAI client not configured")
            
        start_time = time.time()
        
        # Map mode to temperature/parameters that influence Model Router's decision
        # Model Router automatically selects models based on request characteristics
        if mode == "quality":
            # Higher temperature for quality mode to allow more creative/detailed responses
            adjusted_temperature = min(temperature + 0.2, 1.0)
            adjusted_max_tokens = min(max_tokens + 500, 4000)
        elif mode == "cost":
            # Lower parameters for cost-optimized mode
            adjusted_temperature = max(temperature - 0.2, 0.0)
            adjusted_max_tokens = max(max_tokens - 200, 100)
        else:  # balanced
            adjusted_temperature = temperature
            adjusted_max_tokens = max_tokens
        
        print(f"[DEBUG] Model Router request - Mode: {mode}, Temperature: {adjusted_temperature}, MaxTokens: {adjusted_max_tokens}")
        
        try:
            # Call the model-router deployment using Azure OpenAI client
            # Model Router automatically routes based on request characteristics
            response = self.azure_client.chat.completions.create(
                model=self.foundry_deployment,  # "model-router"
                messages=messages,
                max_tokens=adjusted_max_tokens,
                temperature=adjusted_temperature
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response and telemetry
            response_text = response.choices[0].message.content
            
            # Extract usage and model info
            usage = response.usage
            model_chosen = response.model
            
            telemetry = {
                "model_chosen": model_chosen,
                "tokens": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "latency_ms": latency_ms,
                "endpoint": "model_router"
            }
            
            return response_text, telemetry
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise Exception(f"Model Router call failed: {str(e)}") from e
    
    def call_vision_model(
        self,
        message: str,
        image_url: str,
        deployment_name: str = None,
        max_tokens: int = 1000,
        mode: str = "balanced"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Call Model Router for vision requests.
        Model Router automatically routes to appropriate vision-capable models (gpt-5, gpt-4.1, etc.)
        
        Args:
            message: Text prompt
            image_url: Image URL or base64 data URL  
            deployment_name: Unused (kept for compatibility)
            max_tokens: Maximum tokens
            mode: Routing mode for Model Router
        
        Returns:
            Tuple of (response_text, telemetry_dict)
        """
        # Log image data for debugging
        print(f"[DEBUG] Vision request - Image URL length: {len(image_url)}")
        if image_url.startswith('data:'):
            # Extract image format and preview base64 start
            parts = image_url.split(',', 1)
            if len(parts) == 2:
                format_part = parts[0]
                base64_data = parts[1]
                print(f"[DEBUG] Image format: {format_part}")
                print(f"[DEBUG] Base64 data length: {len(base64_data)}")
                print(f"[DEBUG] Base64 preview (first 50 chars): {base64_data[:50]}")
        
        # Format messages with image content
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
        
        # Use Model Router for vision - it will route to appropriate vision-capable model
        print(f"[DEBUG] Calling Model Router with vision content, mode={mode}")
        response_text, telemetry = self.call_router(
            messages=messages,
            mode=mode,
            max_tokens=max_tokens,
            temperature=0.5
        )
        
        # Update telemetry to indicate vision request
        telemetry["endpoint"] = "model_router_vision"
        print(f"[DEBUG] Vision response received from model: {telemetry.get('model_chosen', 'unknown')}")
        
        return response_text, telemetry
