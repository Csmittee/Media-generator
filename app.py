"""General AI Image Generator Dashboard"""

import streamlit as st
from dotenv import load_dotenv
import os
from pathlib import Path

# =============================================
# Robust path setup for Streamlit Cloud
# =============================================
ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT_DIR))

# Load environment variables
load_dotenv()

# Import utils (this is the most reliable way)
from utils.model_config import MODELS, SIZE_PRESETS
from utils.replicate_client import ReplicateClient
from utils.cloudinary_upload import CloudinaryUploader

# =============================================
# Page Configuration
# =============================================
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "status" not in st.session_state:
    st.session_state.status = ""

# Title
st.title("🎨 AI Image Generator")
st.caption("Image-to-Image generation with social media presets • Powered by Replicate + Cloudinary")

# =============================================
# Sidebar Configuration
# =============================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    cloud_key = os.getenv("CLOUDINARY_API_KEY")
    cloud_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    if not all([replicate_token, cloud_name, cloud_key, cloud_secret]):
        st.error("⚠️ Missing API keys! Please add them in Streamlit Cloud → Settings → Secrets")
        st.stop()
    
    # Model Selection
    model_names = list(MODELS.keys())
    selected_model = st.selectbox(
        "🎨 Select AI Model",
        model_names,
        format_func=lambda x: MODELS[x]["name"]
    )
    model_info = MODELS[selected_model]
    st.caption(f"📌 {model_info.get('best_for', 'High quality generation')}")
    
    # Size Preset
    selected_size = st.selectbox(
        "📐 Output Size (Social Media)", 
        list(SIZE_PRESETS.keys())
    )
    
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.generated_image = None
        st.session_state.status = ""
        st.rerun()

# =============================================
# Main Area
# =============================================
st.subheader("📷 Step 1: Reference Image")
ref_image_url = st.text_input(
    "Paste Cloudinary URL of your reference image:",
    placeholder="https://res.cloudinary.com/.../your-image.jpg",
    help="Upload your reference image to Cloudinary first, then paste the direct URL here"
)

st.subheader("💬 Step 2: Describe Your Vision")

# Tall classic chat container (like ChatGPT / Gemini)
chat_container = st.container(height=520, border=True)

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
            if "image_url" in msg and msg["image_url"]:
                st.image(msg["image_url"], use_container_width=True)

status_placeholder = st.empty()

def update_status(msg: str) -> None:
    st.session_state.status = msg
    status_placeholder.info(msg)

# Chat input
prompt = st.chat_input(
    "Describe the background, style, lighting, atmosphere, mood...",
    key="main_prompt"
)

# =============================================
# Generation Logic
# =============================================
if prompt and ref_image_url:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with chat_container:
        st.chat_message("user").write(prompt)
    
    st.session_state.generated_image = None
    
    # Initialize clients
    replicate_client = ReplicateClient(api_token=replicate_token)
    cloudinary_client = CloudinaryUploader(
        cloud_name=cloud_name,
        api_key=cloud_key,
        api_secret=cloud_secret
    )
    
    update_status(f"🎨 Generating with {MODELS[selected_model]['name']}...")
    
    generated_url = replicate_client.generate_image(
        model_id=MODELS[selected_model]["replicate_id"],
        prompt=prompt,
        image_url=ref_image_url,
        progress_callback=update_status
    )
    
    if generated_url:
        update_status("📤 Uploading to Cloudinary...")
        upload_result = cloudinary_client.upload_image(
            image_url=generated_url,
            preset_name=selected_size,
            progress_callback=update_status
        )
        
        if upload_result:
            final_url = upload_result["secure_url"]
            st.session_state.generated_image = final_url
            
            response_text = (
                f"✅ Generated using **{MODELS[selected_model]['name']}**\n\n"
                f"📏 Size: {selected_size}\n\n"
                f"🔗 [View on Cloudinary]({final_url})"
            )
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "image_url": final_url
            })
            
            with chat_container:
                st.chat_message("assistant").write(response_text)
                st.image(final_url, use_container_width=True)
            
            update_status("✅ Generation complete!")
            st.code(final_url, language="text")
            st.caption("📋 Copy this URL and paste into social media")
        else:
            update_status("❌ Failed to upload to Cloudinary")
    else:
        update_status("❌ Failed to generate image with Replicate")

# Show current status
if st.session_state.status:
    status_placeholder.info(st.session_state.status)

st.divider()
st.caption("🎨 AI Image Generator | Powered by Replicate + Cloudinary | Python 3.12")
