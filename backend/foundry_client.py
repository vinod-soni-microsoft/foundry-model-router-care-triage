"""
Foundry Client Module
Handles communication with Microsoft Foundry Model Router and Azure OpenAI deployments.
"""
import os
import time
from typing import Dict, List, Optional, Any, Tuple
import httpx
from openai import AzureOpenAI


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
        if self.azure_endpoint and self.azure_api_key:
            self.azure_client = AzureOpenAI(
                api_key=self.azure_api_key,
                api_version=self.azure_api_version,
                azure_endpoint=self.azure_endpoint
            )
        else:
            self.azure_client = None
    
    async def call_router(
        self,
        messages: List[Dict[str, Any]],
        mode: str = "balanced",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Call Foundry Model Router via Chat Completions API.
        
        Args:
            messages: List of message dicts with role and content
            mode: Routing mode (balanced/cost/quality)
            max_tokens: Maximum tokens for completion
            temperature: Sampling temperature
        
        Returns:
            Tuple of (response_text, telemetry_dict)
        """
        start_time = time.time()
        
        try:
            # Prepare request to Foundry Model Router
            headers = {
                "Content-Type": "application/json",
                "api-key": self.foundry_api_key
            }
            
            # Build request payload
            payload = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # Add routing preferences based on mode
            if mode == "cost":
                payload["model"] = "cost-optimized"
            elif mode == "quality":
                payload["model"] = "quality-optimized"
            else:  # balanced
                payload["model"] = "balanced"
            
            # Make request
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.foundry_endpoint}/openai/deployments/{self.foundry_deployment}/chat/completions",
                    headers=headers,
                    json=payload,
                    params={"api-version": "2024-02-15-preview"}
                )
                response.raise_for_status()
                result = response.json()
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response and telemetry
            response_text = result["choices"][0]["message"]["content"]
            
            # Extract usage and model info
            usage = result.get("usage", {})
            model_chosen = result.get("model", "unknown")
            
            telemetry = {
                "model_chosen": model_chosen,
                "tokens": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                "latency_ms": latency_ms,
                "endpoint": "foundry_router"
            }
            
            return response_text, telemetry
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise Exception(f"Foundry Router call failed: {str(e)}") from e
    
    def call_azure_openai(
        self,
        messages: List[Dict[str, Any]],
        deployment_name: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Call Azure OpenAI deployment directly.
        
        Args:
            messages: List of message dicts
            deployment_name: Azure OpenAI deployment name
            max_tokens: Maximum tokens
            temperature: Sampling temperature
        
        Returns:
            Tuple of (response_text, telemetry_dict)
        """
        if not self.azure_client:
            raise ValueError("Azure OpenAI client not configured")
        
        start_time = time.time()
        
        try:
            response = self.azure_client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            response_text = response.choices[0].message.content
            
            telemetry = {
                "model_chosen": deployment_name,
                "tokens": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "latency_ms": latency_ms,
                "endpoint": "azure_openai_direct"
            }
            
            return response_text, telemetry
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise Exception(f"Azure OpenAI call failed: {str(e)}") from e
    
    def call_vision_model(
        self,
        message: str,
        image_url: str,
        deployment_name: str = "gpt-4-vision",
        max_tokens: int = 1000
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Call vision-capable model with image.
        
        Args:
            message: Text prompt
            image_url: Image URL or base64 data URL
            deployment_name: Vision model deployment name
            max_tokens: Maximum tokens
        
        Returns:
            Tuple of (response_text, telemetry_dict)
        """
        if not self.azure_client:
            raise ValueError("Azure OpenAI client not configured")
        
        start_time = time.time()
        
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
            
            response = self.azure_client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.5
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            response_text = response.choices[0].message.content
            
            telemetry = {
                "model_chosen": deployment_name,
                "tokens": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "latency_ms": latency_ms,
                "endpoint": "azure_openai_vision"
            }
            
            return response_text, telemetry
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise Exception(f"Vision model call failed: {str(e)}") from e
