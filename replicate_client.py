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

            model_lower = model_id.lower()
            input_data = {"prompt": prompt}

            # === Model-specific image parameter ===
            if "flux-kontext" in model_lower:
                input_data["img_cond_path"] = image_url          # Flux Kontext
                input_data["aspect_ratio"] = "match_input_image"
            elif "nano-banana" in model_lower:
                input_data["image_input"] = [image_url]          # Nano Banana expects a list
                input_data["aspect_ratio"] = "match_input_image"
            else:
                input_data["image"] = image_url                  # Default for others
                input_data["aspect_ratio"] = "16:9"

            input_data.update({
                "output_format": "jpg",
                "output_quality": 85,
            })

            output = self.client.run(model_id, input=input_data)

            elapsed = time.time() - start_time
            if progress_callback:
                progress_callback(f"✅ Generated in {elapsed:.1f} seconds")

            if isinstance(output, list) and output:
                return str(output[0])
            elif hasattr(output, 'url'):
                return output.url
            return str(output)

        except Exception as e:
            error_msg = str(e)
            if progress_callback:
                progress_callback(f"❌ Replicate Error: {error_msg[:220]}...")
            print(f"Full error: {error_msg}")
            return None
