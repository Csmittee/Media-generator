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
                progress_callback(f"🚀 Calling {model_id}...")

            start_time = time.time()

            # === Model-specific image parameter mapping ===
            model_lower = model_id.lower()
            
            if "flux-kontext" in model_lower:
                image_key = "img_cond_path"          # Flux Kontext needs this
            elif "nano-banana" in model_lower:
                image_key = "image_input"            # Nano Banana Pro needs this (list)
                input_data = {
                    "prompt": prompt,
                    image_key: [image_url],          # Must be a list for Nano Banana
                    "aspect_ratio": "match_input_image",
                    "output_format": "jpg",
                    "output_quality": 85,
                }
            else:
                image_key = "image"
                input_data = {
                    "prompt": prompt,
                    image_key: image_url,
                    "aspect_ratio": "16:9",
                    "output_format": "jpg",
                    "output_quality": 85,
                }

            # For Flux models (if not already handled above)
            if "flux" in model_lower and "image_key" not in locals():
                input_data = {
                    "prompt": prompt,
                    "img_cond_path": image_url,
                    "aspect_ratio": "match_input_image",
                    "output_format": "jpg",
                    "output_quality": 85,
                }

            output = self.client.run(model_id, input=input_data)

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
                progress_callback(f"❌ Replicate Error: {error_msg[:220]}...")
            print(f"Full Replicate error: {error_msg}")
            return None
