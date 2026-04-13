"""Replicate API wrapper for image-to-image generation"""

import replicate
import time
from typing import Optional, Callable

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
            
            # Choose correct image key based on model
            model_lower = model_id.lower()
            if "flux-kontext" in model_lower:
                image_key = "input_image"          # Newer Flux Kontext uses this
            elif "nano-banana" in model_lower or "gpt-image" in model_lower:
                image_key = "image"
            else:
                image_key = "image"                # Safe default
            
            input_data = {
                "prompt": prompt,
                image_key: image_url,
                "guidance": 2.5,
                "num_inference_steps": 30,
                "output_format": "jpg",
                "output_quality": 85,
            }
            
            # Some models support aspect_ratio
            if "flux" in model_lower:
                input_data["aspect_ratio"] = "match_input_image"
            else:
                input_data["aspect_ratio"] = "16:9"
            
            output = self.client.run(
                model_id,
                input=input_data
            )
            
            elapsed = time.time() - start_time
            if progress_callback:
                progress_callback(f"✅ Generated in {elapsed:.1f} seconds")
            
            # Handle different output types
            if isinstance(output, list) and output:
                return str(output[0])
            elif hasattr(output, 'url'):
                return output.url
            return str(output)
            
        except Exception as e:
            error_msg = str(e)
            if progress_callback:
                progress_callback(f"❌ Replicate Error: {error_msg[:200]}...")
            print(f"Full Replicate error: {error_msg}")  # visible in logs
            return None
