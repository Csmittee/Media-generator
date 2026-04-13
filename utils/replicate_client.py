"""Replicate API wrapper for image generation"""

import replicate
import time
from typing import Optional, Dict, Any

class ReplicateClient:
    def __init__(self, api_token: str):
        self.client = replicate.Client(api_token=api_token)
    
    def generate_image(
        self, 
        model_id: str, 
        prompt: str, 
        image_url: str,
        progress_callback=None
    ) -> Optional[str]:
        """
        Generate an image using Replicate's image-to-image model
        
        Args:
            model_id: Replicate model identifier
            prompt: Text prompt for generation
            image_url: URL of the reference image (your claw machine)
            progress_callback: Function to call with status updates
        
        Returns:
            URL of generated image or None if failed
        """
        try:
            if progress_callback:
                progress_callback(f"🚀 Calling {model_id} on Replicate...")
            
            start_time = time.time()
            
            # Run the model
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
            
            # Replicate returns a URL or list of URLs
            if isinstance(output, list):
                return output[0] if output else None
            elif isinstance(output, str):
                return output
            elif hasattr(output, 'url'):
                return output.url
            else:
                return str(output)
                
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Error: {str(e)}")
            return None
