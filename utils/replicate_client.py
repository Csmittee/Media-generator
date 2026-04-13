"""Replicate API wrapper for image generation"""

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
            
            output = self.client.run(
                model_id,
                input={
                    "prompt": prompt,
                    "img_cond_path": image_url,
                    "guidance": 2.5,
                    "num_inference_steps": 30,
                    "aspect_ratio": "16:9",
                    "output_format": "jpg",
                    "output_quality": 85
                }
            )
            
            elapsed = time.time() - start_time
            if progress_callback:
                progress_callback(f"✅ Generated in {elapsed:.1f} seconds")
            
            if isinstance(output, list):
                return output[0] if output else None
            return output.url if hasattr(output, 'url') else str(output)
                
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Error: {str(e)}")
            return None
