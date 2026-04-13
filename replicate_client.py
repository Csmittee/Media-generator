"""Replicate API wrapper for image-to-image generation"""

import replicate
import time
from typing import Optional, Callable, Dict

class ReplicateClient:
    def __init__(self, api_token: str):
        self.client = replicate.Client(api_token=api_token)
    
    def generate_image(
        self, 
        model_id: str, 
        prompt: str, 
        image_url: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        try:
            if progress_callback:
                progress_callback(f"🚀 Calling {model_id} on Replicate...")
            
            start_time = time.time()
            
            # Choose the correct image input key for each model
            image_key = self._get_image_key(model_id)
            
            input_params: Dict = {
                "prompt": prompt,
                image_key: image_url,
                "guidance": 2.5,
                "num_inference_steps": 30,
                "output_format": "jpg",
                "output_quality": 85,
            }
            
            # Some models prefer aspect_ratio instead of fixed 16:9
            if "nano-banana" in model_id.lower():
                input_params["aspect_ratio"] = "match_input_image"
            else:
                input_params["aspect_ratio"] = "16:9"
            
            output = self.client.run(
                model_id,
                input=input_params
            )
            
            elapsed = time.time() - start_time
            if progress_callback:
                progress_callback(f"✅ Generated in {elapsed:.1f} seconds")
            
            # Handle different output formats
            if isinstance(output, list) and output:
                return output[0]
            elif hasattr(output, 'url'):
                return output.url
            else:
                return str(output)
                
        except Exception as e:
            error_msg = str(e)
            if progress_callback:
                progress_callback(f"❌ Error: {error_msg[:150]}...")
            print(f"Replicate error: {error_msg}")  # For debugging in logs
            return None
    
    def _get_image_key(self, model_id: str) -> str:
        """Return the correct image parameter name for each model"""
        model_lower = model_id.lower()
        
        if "flux-kontext" in model_lower:
            return "img_cond_path"          # Flux Kontext family
        elif "nano-banana" in model_lower or "gpt-image" in model_lower:
            return "image"                  # Google & OpenAI style
        elif "seedream" in model_lower:
            return "image"                  # ByteDance Seedream
        else:
            return "image"                  # Default - most safe
