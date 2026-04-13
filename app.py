"""Claw Machine Content Factory Dashboard - AI Image Generator"""

import streamlit as st
from dotenv import load_dotenv
import os
from utils.model_config import MODELS, SIZE_PRESETS
from utils.replicate_client import ReplicateClient
from utils.cloudinary_uploader import CloudinaryUploader

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Claw Machine Content Factory",
    page_icon="🎮",
    layout="wide"
)

# Initialize session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "status" not in st.session_state:
    st.session_state.status = ""

# Title
st.title("🎮 Claw Machine Content Factory")
st.caption("Generate promotional images for Laos, Myanmar, and neighboring countries")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check for API keys
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    cloud_key = os.getenv("CLOUDINARY_API_KEY")
    cloud_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    if not all([replicate_token, cloud_name, cloud_key, cloud_secret]):
        st.error("⚠️ Missing API keys! Please set up your .env file")
        st.stop()
    
    # Model selection
    model_names = list(MODELS.keys())
    selected_model = st.selectbox(
        "🎨 Select AI Model",
        model_names,
        format_func=lambda x: MODELS[x]["name"]
    )
    
    # Show model info
    model_info = MODELS[selected_model]
    st.caption(f"📌 {model_info['best_for']}")
    
    # Size preset
    size_options = list(SIZE_PRESETS.keys())
    selected_size = st.selectbox("📐 Output Size (Social Media)", size_options)
    
    # Reset button
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.generated_image = None
        st.session_state.status = ""
        st.rerun()

# Main area - Reference image input
st.subheader("📷 Step 1: Your Claw Machine Photo")
ref_image_url = st.text_input(
    "Paste Cloudinary URL of your claw machine photo:",
    placeholder="https://res.cloudinary.com/your-cloud/image/upload/v123/claw-machine.jpg",
    help="Upload your claw machine photo to Cloudinary first, then paste the URL here"
)

# Main area - Chat interface
st.subheader("💬 Step 2: Describe Your Vision")

# Display chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
            if "image_url" in msg and msg["image_url"]:
                st.image(msg["image_url"], use_container_width=True)

# Status display
status_placeholder = st.empty()

# Prompt input
prompt = st.chat_input("Describe the background, lighting, atmosphere...")

if prompt and ref_image_url:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Clear previous generated image
    st.session_state.generated_image = None
    
    # Status updates
    def update_status(msg):
        st.session_state.status = msg
        status_placeholder.info(msg)
    
    # Initialize clients
    replicate_client = ReplicateClient(api_token=replicate_token)
    cloudinary_client = CloudinaryUploader(
        cloud_name=cloud_name,
        api_key=cloud_key,
        api_secret=cloud_secret
    )
    
    # Step 1: Generate with Replicate
    update_status(f"🎨 Generating with {MODELS[selected_model]['name']}...")
    generated_url = replicate_client.generate_image(
        model_id=MODELS[selected_model]["replicate_id"],
        prompt=prompt,
        image_url=ref_image_url,
        progress_callback=update_status
    )
    
    if generated_url:
        # Step 2: Upload to Cloudinary with resize
        update_status("📤 Uploading to Cloudinary...")
        upload_result = cloudinary_client.upload_image(
            image_url=generated_url,
            preset_name=selected_size,
            progress_callback=update_status
        )
        
        if upload_result:
            final_url = upload_result['secure_url']
            st.session_state.generated_image = final_url
            
            # Add assistant response with image
            response_text = f"✅ Generated using **{MODELS[selected_model]['name']}**\n\n📏 Size: {selected_size}\n\n🔗 [View on Cloudinary]({final_url})"
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text,
                "image_url": final_url
            })
            
            # Display in current session
            st.chat_message("assistant").write(response_text)
            st.image(final_url, use_container_width=True)
            
            update_status("✅ Complete! Ready to copy URL and post to Buffer/Line/Facebook")
            
            # Provide copyable URL
            st.code(final_url, language="text")
            st.caption("📋 Copy this URL and paste directly into Buffer, Line OA, or Facebook")
        else:
            update_status("❌ Failed to upload to Cloudinary")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ Failed to upload image to Cloudinary. Please check your credentials."
            })
    else:
        update_status("❌ Failed to generate image with Replicate")
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❌ Failed to generate image. Please check your Replicate API token and try again."
        })

# Display current status
if st.session_state.status:
    status_placeholder.info(st.session_state.status)

# Footer
st.divider()
st.caption("🎮 Claw Machine Content Factory | Powered by Replicate + Cloudinary | Images saved to Cloudinary folder: AI-image-gen")
