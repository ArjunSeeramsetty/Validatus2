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
    """Gemini LLM client with Secret Manager integration"""
    
    def __init__(self):
        self._model = None
        self._initialized = False
        self.model_name = "gemini-2.5-pro"  # Use gemini-2.5-pro (latest model)
        self.temperature = 0.1
        self.max_tokens = 2048
        
    def _initialize_client(self):
        """Initialize Gemini client with API key from environment or Secret Manager"""
        if self._initialized:
            return
        
        try:
            # Try environment variable first
            api_key = os.getenv("GEMINI_API_KEY")
            
            # If not in environment, try Secret Manager (production)
            if not api_key and os.getenv("CLOUD_RUN_SERVICE"):
                logger.info("Loading Gemini API key from Secret Manager...")
                try:
                    client = secretmanager.SecretManagerServiceClient()
                    project_id = os.getenv("GCP_PROJECT_ID", "validatus-platform")
                    secret_name = f"projects/{project_id}/secrets/gemini-api-key/versions/latest"
                    response = client.access_secret_version(request={"name": secret_name})
                    api_key = response.payload.data.decode("UTF-8").strip()
                    logger.info("✅ Gemini API key loaded from Secret Manager")
                except Exception as e:
                    logger.error(f"Failed to load Gemini API key from Secret Manager: {e}")
            
            if not api_key:
                logger.warning("⚠️ GEMINI_API_KEY not found - LLM scoring will not be available")
                return
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    candidate_count=1
                )
            )
            
            self._initialized = True
            logger.info(f"✅ Gemini client initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._initialized = False
    
    async def generate_content(self, prompt: str, retry_count: int = 3) -> Optional[str]:
        """
        Generate content using Gemini model with retry logic
        
        Args:
            prompt: The analysis prompt for the LLM
            retry_count: Number of retries on failure
            
        Returns:
            Generated text or None if failed
        """
        if not self._initialized:
            self._initialize_client()
        
        if not self._model:
            logger.warning("Gemini model not available, skipping LLM generation")
            return None
        
        for attempt in range(retry_count):
            try:
                # Run synchronous Gemini API call in executor to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self._model.generate_content(prompt)
                )
                
                if response and response.text:
                    logger.debug(f"✅ Gemini generated {len(response.text)} chars")
                    return response.text
                else:
                    logger.warning("Gemini returned empty response")
                    
            except Exception as e:
                logger.error(f"Gemini generation failed (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
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
        """Check if Gemini client is initialized and available"""
        if not self._initialized:
            self._initialize_client()
        return self._initialized and self._model is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current client status"""
        return {
            "initialized": self._initialized,
            "available": self.is_available(),
            "model": self.model_name if self._model else None,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

# Global Gemini client instance
try:
    gemini_client = GeminiClient()
except Exception as e:
    logger.error(f"Failed to create Gemini client: {e}")
    gemini_client = None

