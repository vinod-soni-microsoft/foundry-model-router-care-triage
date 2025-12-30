"""
Care Triage FastAPI Application
Backend API for intelligent healthcare triage using Foundry Model Router.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import base64
import asyncio
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from intent_detector import IntentDetector
from phi_redactor import PHIRedactor
from guardrails import Guardrails
from foundry_client import FoundryClient
from router_observability import RouterObservability
from ai.rag_pipeline import RAGPipeline

app = FastAPI(
    title="Care Triage API",
    description="Intelligent healthcare triage assistant using Foundry Model Router",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
foundry_client = FoundryClient()
rag_pipeline = RAGPipeline()
observability = RouterObservability()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    mode: str = "balanced"  # balanced | cost | quality
    image: Optional[str] = None  # Base64 encoded image


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    telemetry: Dict[str, Any]
    citations: Optional[Dict] = None
    warning: Optional[str] = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Care Triage API",
        "version": "1.0.0"
    }


@app.get("/test")
async def test():
    """Test endpoint to verify OpenAI connection."""
    try:
        messages = [{"role": "user", "content": "Say 'test successful' in 3 words."}]
        response_text, telemetry = foundry_client.call_router(messages=messages, mode="balanced", max_tokens=50, temperature=0.7)
        return {"status": "success", "response": response_text, "telemetry": telemetry}
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for triage assistant.
    
    Processes user messages through:
    1. PHI redaction
    2. Safety guardrails
    3. Intent detection (for logging and disclaimers)
    4. Response generation via Model Router (with RAG for clinical queries)
    5. Observability logging
    
    Model Router automatically handles:
    - Cost/balanced/quality optimization based on mode
    - Vision-capable model selection when images are present
    - Intelligent routing to appropriate underlying models
    """
    try:
        original_message = request.message
        mode = request.mode
        has_image = request.image is not None
        
        # Step 1: PHI Redaction
        redacted_message, has_phi, phi_types = PHIRedactor.redact_phi(original_message)
        
        if has_phi:
            observability.log_phi_detection(
                original_message,
                redacted_message,
                phi_types
            )
        
        # Step 2: Safety Guardrails
        is_safe, warning_message, safety_metadata = Guardrails.check_safety(redacted_message)
        
        if not is_safe:
            observability.log_error(
                "safety_violation",
                "Request blocked by guardrails",
                {"risk_level": safety_metadata.get("risk_level")}
            )
            raise HTTPException(status_code=400, detail=warning_message)
        
        # Step 3: Intent Detection (for logging and disclaimers only)
        intent, intent_reason = IntentDetector.detect_intent(redacted_message, has_image)
        
        # Step 4: Generate Response (Model Router handles all routing automatically)
        response_text = ""
        telemetry = {}
        citations = None
        
        if has_image and request.image:
            # Vision path - Model Router detects image and routes to vision-capable model
            response_text, telemetry = await handle_vision_request(
                message=redacted_message,
                image_data=request.image,
                mode=mode
            )
        elif intent == "clinical":
            # Clinical path with RAG - Model Router handles quality optimization
            response_text, telemetry, citations = await handle_clinical_request(
                message=redacted_message,
                mode=mode
            )
        else:
            # Admin or general path - Model Router handles cost/balanced optimization
            response_text, telemetry = await handle_general_request(
                message=redacted_message,
                mode=mode
            )
        
        # Add disclaimers
        response_text = Guardrails.add_disclaimer(response_text, intent)
        
        # Step 5: Log telemetry
        full_telemetry = observability.log_routing_decision(
            intent=intent,
            mode=mode,
            model_chosen=telemetry.get("model_chosen", "model-router"),
            tokens=telemetry.get("tokens"),
            latency_ms=telemetry.get("latency_ms", 0),
            rationale=f"Model Router with {mode} mode optimization",
            has_phi=has_phi,
            has_image=has_image,
            additional_context={
                "intent_reason": intent_reason,
                "safety_metadata": safety_metadata
            }
        )
        
        return ChatResponse(
            response=response_text,
            telemetry=full_telemetry,
            citations=citations,
            warning=warning_message if warning_message else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {str(e)}")
        print(f"TRACEBACK: {error_details}")
        observability.log_error("api_error", str(e), {"request": request.dict()})
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def handle_vision_request(
    message: str,
    image_data: str,
    mode: str
) -> tuple:
    """Handle vision model requests with image analysis using Model Router."""
    # Prepare vision prompt
    vision_prompt = f"""Analyze this medical image and provide an educational description.

User Question: {message}

Please provide:
1. A detailed description of what you observe
2. Educational information about relevant anatomy or conditions
3. Appropriate confidence levels and limitations
4. Safety language emphasizing this is not a diagnostic tool

Remember: This is for educational purposes only, not for diagnosis."""
    
    try:
        # Model Router automatically detects image and routes to vision-capable model
        response_text, telemetry = foundry_client.call_vision_model(
            message=vision_prompt,
            image_url=image_data,
            mode=mode
        )
        return response_text, telemetry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision model error: {str(e)}")


async def handle_clinical_request(
    message: str,
    mode: str
) -> tuple:
    """Handle clinical requests with RAG using Model Router."""
    citations = None
    
    # Attempt RAG retrieval
    if rag_pipeline.enabled:
        documents = rag_pipeline.retrieve_documents(message, top_k=3)
        print(f"[DEBUG] Retrieved {len(documents)} documents from Azure AI Search")
        augmented_prompt = rag_pipeline.build_rag_prompt(message, documents)
    else:
        print("[DEBUG] RAG pipeline not enabled, using fallback prompt")
        documents = []
        augmented_prompt = rag_pipeline._build_fallback_prompt(message)
    
    # Call Model Router (it handles quality optimization automatically)
    messages = [{"role": "user", "content": augmented_prompt}]
    
    try:
        response_text, telemetry = foundry_client.call_router(
            messages=messages,
            mode=mode,
            max_tokens=2000,  # Increased from 1000 to prevent truncation
            temperature=0.7
        )
        
        print(f"[DEBUG] Response length: {len(response_text)} chars, {telemetry.get('tokens', {}).get('completion_tokens', 0)} tokens")
        
        # Extract citations if RAG was used
        if documents:
            citations = rag_pipeline.extract_citations(response_text, documents)
            print(f"[DEBUG] Extracted {len(citations)} citations from response")
        
        return response_text, telemetry, citations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clinical model error: {str(e)}")


async def handle_general_request(
    message: str,
    mode: str
) -> tuple:
    """Handle general/admin requests using Model Router."""
    messages = [{"role": "user", "content": message}]
    
    try:
        # Model Router handles cost/balanced optimization automatically
        response_text, telemetry = foundry_client.call_router(
            messages=messages,
            mode=mode,
            max_tokens=800,
            temperature=0.7
        )
        
        return response_text, telemetry
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
