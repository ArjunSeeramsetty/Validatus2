"""
Gemini AI Client for Validatus v2.0
Handles LLM-based strategic layer analysis
"""
import logging
import os
import asyncio
from typing import Optional, Dict, Any
from google.cloud import secretmanager
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini LLM client with Secret Manager integration and multi-model rotation"""
    
    def __init__(self):
        self._models = {}  # Dictionary of initialized models
        self._initialized = False
        
        # Multi-model configuration for rate limit mitigation
        # ✅ Confirmed available: gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite
        # Layer distribution: 1-70 → gemini-2.5-pro, 71-140 → gemini-2.5-flash, 141-210 → gemini-2.5-flash-lite
        self.model_configs = [
            {"name": "gemini-2.5-pro", "priority": 1, "max_tokens": 8192},           # Layers 1-70: Most capable
            {"name": "gemini-2.5-flash", "priority": 2, "max_tokens": 8192},         # Layers 71-140: Fast, balanced
            {"name": "gemini-2.5-flash-lite", "priority": 3, "max_tokens": 8192},    # Layers 141-210: Fastest
        ]
        
        self.current_model_index = 0  # For round-robin rotation
        self.temperature = 0.1
        
    def _initialize_client(self):
        """Initialize Gemini client with multiple models for rate limit mitigation"""
        if self._initialized:
            return
        
        try:
            # Try environment variable first  
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                # Strip ALL whitespace including \r\n\t
                api_key = api_key.strip().replace('\r', '').replace('\n', '').replace('\t', '').strip()
            
            # If not in environment, try Secret Manager (production)
            if not api_key and os.getenv("CLOUD_RUN_SERVICE"):
                logger.info("Loading Gemini API key from Secret Manager...")
                try:
                    client = secretmanager.SecretManagerServiceClient()
                    project_id = os.getenv("GCP_PROJECT_ID", "validatus-platform")
                    secret_name = f"projects/{project_id}/secrets/gemini-api-key/versions/latest"
                    response = client.access_secret_version(request={"name": secret_name})
                    # Strip ALL whitespace including \r\n\t and spaces
                    api_key = response.payload.data.decode("UTF-8").strip().replace('\r', '').replace('\n', '').replace('\t', '').strip()
                    logger.info(f"✅ Gemini API key loaded from Secret Manager (length: {len(api_key)})")
                except Exception as e:
                    logger.error(f"Failed to load Gemini API key from Secret Manager: {e}")
            
            if not api_key:
                logger.warning("⚠️ GEMINI_API_KEY not found - LLM scoring will not be available")
                return
            
            # Configure Gemini API
            # Important: Use transport='rest' to avoid metadata service issues in Cloud Run
            genai.configure(
                api_key=api_key,
                transport='rest'  # Force REST transport instead of gRPC to avoid metadata service
            )
            
            # Initialize all available models for rotation
            initialized_count = 0
            for config in self.model_configs:
                try:
                    model = genai.GenerativeModel(
                        model_name=config["name"],
                        generation_config=genai.GenerationConfig(
                            temperature=self.temperature,
                            max_output_tokens=config["max_tokens"],
                            candidate_count=1
                        )
                    )
                    self._models[config["name"]] = {
                        "model": model,
                        "config": config,
                        "failure_count": 0
                    }
                    initialized_count += 1
                    logger.info(f"✅ Initialized model: {config['name']}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize {config['name']}: {e}")
            
            # Fallback to alternative models if primary 2.5 models aren't available
            if initialized_count == 0:
                logger.warning("⚠️ Primary Gemini 2.5 models not available, trying fallback models...")
                fallback_configs = [
                    {"name": "gemini-2.0-flash", "priority": 1, "max_tokens": 8192},        # Gemini 2.0 stable
                    {"name": "gemini-2.0-flash-lite", "priority": 2, "max_tokens": 8192},   # Gemini 2.0 lite
                    {"name": "gemini-2.0-flash-exp", "priority": 3, "max_tokens": 8192},    # Gemini 2.0 experimental
                ]
                
                for config in fallback_configs:
                    try:
                        model = genai.GenerativeModel(
                            model_name=config["name"],
                            generation_config=genai.GenerationConfig(
                                temperature=self.temperature,
                                max_output_tokens=config["max_tokens"],
                                candidate_count=1
                            )
                        )
                        self._models[config["name"]] = {
                            "model": model,
                            "config": config,
                            "failure_count": 0
                        }
                        initialized_count += 1
                        logger.info(f"✅ Initialized fallback model: {config['name']}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to initialize fallback {config['name']}: {e}")
            
            if initialized_count > 0:
                self._initialized = True
                logger.info(f"✅ Gemini client initialized with {initialized_count} models for rate limit mitigation")
            else:
                logger.error("❌ No Gemini models could be initialized (including fallbacks)")
                self._initialized = False
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._initialized = False
    
    def _get_next_model(self):
        """Get next available model using round-robin rotation"""
        if not self._models:
            return None
        
        # Get list of model names sorted by failure count (prefer models with fewer failures)
        sorted_models = sorted(
            self._models.items(),
            key=lambda x: (x[1]["failure_count"], x[1]["config"]["priority"])
        )
        
        # Round-robin through sorted models
        self.current_model_index = (self.current_model_index + 1) % len(sorted_models)
        model_name = sorted_models[self.current_model_index][0]
        
        return self._models[model_name]
    
    async def generate_content(self, prompt: str, retry_count: int = 3, timeout: int = 120) -> Optional[str]:
        """
        Generate content using multi-model rotation for rate limit mitigation
        
        Args:
            prompt: The analysis prompt for the LLM
            retry_count: Number of retries on failure (across all models)
            timeout: Timeout in seconds for the API call
            
        Returns:
            Generated text or None if failed
        """
        if not self._initialized:
            self._initialize_client()
        
        if not self._models:
            logger.warning("No Gemini models available, skipping LLM generation")
            return None
        
        models_tried = set()
        
        for attempt in range(retry_count):
            # Get next model for rotation
            model_data = self._get_next_model()
            if not model_data:
                logger.error("No available models for content generation")
                return None
            
            model = model_data["model"]
            model_name = model_data["config"]["name"]
            models_tried.add(model_name)
            
            try:
                # Run synchronous Gemini API call in executor with timeout
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda m=model: m.generate_content(prompt)
                    ),
                    timeout=timeout
                )
                
                if response and response.text:
                    logger.debug(f"✅ Gemini ({model_name}) generated {len(response.text)} chars")
                    # Reset failure count on success
                    model_data["failure_count"] = max(0, model_data["failure_count"] - 1)
                    return response.text
                else:
                    logger.warning(f"Gemini ({model_name}) returned empty response")
                    model_data["failure_count"] += 1
                    
            except asyncio.TimeoutError:
                logger.error(f"Gemini ({model_name}) timeout (attempt {attempt + 1}/{retry_count}): {timeout}s exceeded")
                model_data["failure_count"] += 1
                if attempt < retry_count - 1 and len(models_tried) < len(self._models):
                    await asyncio.sleep(1)  # Short delay before trying next model
            except Exception as e:
                error_str = str(e)
                
                # Check for rate limit errors
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    logger.warning(f"Gemini ({model_name}) rate limited, rotating to next model")
                    model_data["failure_count"] += 2  # Penalize rate-limited models more
                    await asyncio.sleep(0.5)  # Brief pause before next model
                else:
                    logger.error(f"Gemini ({model_name}) failed (attempt {attempt + 1}/{retry_count}): {e}")
                    model_data["failure_count"] += 1
                    if attempt < retry_count - 1:
                        await asyncio.sleep(2 ** min(attempt, 3))  # Exponential backoff (capped at 8s)
        
        logger.error(f"All {retry_count} attempts failed across {len(models_tried)} models: {models_tried}")
        return None
    
    async def generate_structured_analysis(self, prompt: str, expected_structure: Dict) -> Optional[Dict]:
        """
        Generate content and attempt to parse into structured format
        
        Args:
            prompt: The analysis prompt
            expected_structure: Dict describing expected output structure
            
        Returns:
            Parsed structured data or None
        """
        content = await self.generate_content(prompt)
        
        if not content:
            return None
        
        try:
            # Try to parse JSON response if expected
            import json
            import re
            
            # Look for JSON block in response
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
                return parsed
            
            # Try parsing entire response as JSON
            try:
                parsed = json.loads(content)
                return parsed
            except:
                # Return raw content if not JSON
                return {"raw_text": content}
                
        except Exception as e:
            logger.error(f"Failed to parse structured response: {e}")
            return {"raw_text": content}
    
    def is_available(self) -> bool:
        """Check if Gemini client is initialized and has available models"""
        if not self._initialized:
            self._initialize_client()
        return self._initialized and len(self._models) > 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current client status with multi-model information"""
        models_status = []
        for model_name, model_data in self._models.items():
            models_status.append({
                "name": model_name,
                "priority": model_data["config"]["priority"],
                "max_tokens": model_data["config"]["max_tokens"],
                "failure_count": model_data["failure_count"],
                "status": "healthy" if model_data["failure_count"] < 5 else "degraded"
            })
        
        return {
            "initialized": self._initialized,
            "available": self.is_available(),
            "models_count": len(self._models),
            "models": models_status,
            "temperature": self.temperature,
            "rotation_strategy": "round-robin with failure tracking"
        }

# Global Gemini client instance
try:
    gemini_client = GeminiClient()
except Exception as e:
    logger.error(f"Failed to create Gemini client: {e}")
    gemini_client = None

