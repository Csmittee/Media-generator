"""Cloudinary upload with social media presets"""

import cloudinary
import cloudinary.uploader
from typing import Optional, Dict, Any, Callable

class CloudinaryUploader:
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        self.folder_name = "AI-image-gen"
    
    def upload_image(
        self, 
        image_url: str, 
        preset_name: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            if progress_callback:
                progress_callback(f"📤 Uploading to Cloudinary folder: {self.folder_name}")

            # Direct import (files are now in root)
            from model_config import SIZE_PRESETS
            
            preset = SIZE_PRESETS.get(preset_name, SIZE_PRESETS["Original (no resize)"])
            
            transformation = []
            
            if preset.get("width") and preset.get("height"):
                transformation.append({
                    "width": preset["width"],
                    "height": preset["height"],
                    "crop": preset["crop"]
                })
                transformation.append({"quality": "auto"})
                transformation.append({"fetch_format": "auto"})
                
                if progress_callback:
                    progress_callback(f"📐 Resizing to {preset['width']}x{preset['height']}")
            else:
                transformation.append({"quality": "auto"})
                transformation.append({"fetch_format": "auto"})
            
            result = cloudinary.uploader.upload(
                image_url,
                folder=self.folder_name,
                transformation=transformation,
                use_filename=True,
                unique_filename=True
            )
            
            if progress_callback:
                progress_callback("✅ Upload complete!")
                progress_callback(f"🔗 URL: {result['secure_url'][:60]}...")
            
            return result
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Cloudinary error: {str(e)}")
            print(f"Cloudinary full error: {e}")
            return None
