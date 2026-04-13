"""Model configurations for Replicate"""

MODELS = {
    "flux-kontext": {
        "name": "Flux Kontext (Best for product preservation)",
        "replicate_id": "prunaai/flux-kontext-dev",
        "version": "latest",
        "cost_per_sec": 0.0014,
        "avg_time_sec": 8,
        "best_for": "Keeping the reference image structure accurately"
    },
    "nano-banana-pro": {
        "name": "Nano Banana Pro (Best text rendering)",
        "replicate_id": "google/nano-banana-pro",
        "version": "latest",
        "cost_per_sec": 0.0022,
        "avg_time_sec": 10,
        "best_for": "Magazine-quality text in any language"
    },
    "seedream-4": {
        "name": "Seedream 4 (Most realistic backgrounds)",
        "replicate_id": "bytedance/seedream-4",
        "version": "latest",
        "cost_per_sec": 0.0014,
        "avg_time_sec": 14,
        "best_for": "Natural lighting and scene integration"
    },
    "gpt-image-1": {
        "name": "GPT-image-1 (Cheapest & creative)",
        "replicate_id": "openai/gpt-image-1",
        "version": "latest",
        "cost_per_sec": 0.00025,
        "avg_time_sec": 40,
        "best_for": "Budget experiments and creative variations"
    }
}

# Size presets for social media
SIZE_PRESETS = {
    "Instagram Square (1080x1080)": {"width": 1080, "height": 1080, "crop": "fill"},
    "Facebook Post (1200x630)": {"width": 1200, "height": 630, "crop": "fill"},
    "Line OA (1040x1040)": {"width": 1040, "height": 1040, "crop": "fill"},
    "Original (no resize)": {"width": None, "height": None, "crop": None}
}
