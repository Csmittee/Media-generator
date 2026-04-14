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

            # Correct image key for Flux Kontext models
            model_lower = model_id.lower()
            if "flux-kontext" in model_lower or "flux" in model_lower:
                image_key = "input_image"      # This is the key Flux Kontext needs
            else:
                image_key = "image"

            input_data = {
                "prompt": prompt,
                image_key: image_url,
                "guidance": 2.5,
                "num_inference_steps": 30,
                "output_format": "jpg",
                "output_quality": 85,
            }

            # Flux models prefer matching the input image aspect ratio
            if "flux" in model_lower:
                input_data["aspect_ratio"] = "match_input_image"

            output = self.client.run(model_id, input=input_data)

            elapsed = time.time() - start_time
            if progress_callback:
                progress_callback(f"✅ Generated in {elapsed:.1f} seconds")

            # Handle output formats
            if isinstance(output, list) and output:
                return str(output[0])
            elif hasattr(output, 'url'):
                return output.url
            return str(output)

        except Exception as e:
            error_msg = str(e)
            if progress_callback:
                progress_callback(f"❌ Replicate Error: {error_msg[:220]}...")
            print(f"Full Replicate error: {error_msg}")   # Check logs if needed
            return None
