"""General AI Image Generator Dashboard"""

import streamlit as st
from dotenv import load_dotenv
import os
from pathlib import Path

# Robust path setup
ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT_DIR))

load_dotenv()

from model_config import MODELS, SIZE_PRESETS
from replicate_client import ReplicateClient
from cloudinary_upload import CloudinaryUploader

st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "status" not in st.session_state:
    st.session_state.status = ""
if "last_generated_url" not in st.session_state:   # ← New: for manual download
    st.session_state.last_generated_url = None

st.title("🎨 AI Image Generator")
st.caption("Image-to-Image generation • Replicate + Cloudinary")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    cloud_key = os.getenv("CLOUDINARY_API_KEY")
    cloud_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    if not all([replicate_token, cloud_name, cloud_key, cloud_secret]):
        st.error("⚠️ Missing API keys!")
        st.stop()
    
    model_names = list(MODELS.keys())
    selected_model = st.selectbox(
        "🎨 Select AI Model",
        model_names,
        format_func=lambda x: MODELS[x]["name"]
    )
    st.caption(f"📌 {MODELS[selected_model].get('best_for', '')}")
    
    selected_size = st.selectbox("📐 Output Size", list(SIZE_PRESETS.keys()))
    
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.generated_image = None
        st.session_state.last_generated_url = None
        st.session_state.status = ""
        st.rerun()

st.subheader("📷 Step 1: Reference Image")
ref_image_url = st.text_input(
    "Paste Cloudinary URL of your reference image:",
    placeholder="https://res.cloudinary.com/.../your-image.jpg"
)

st.subheader("💬 Step 2: Describe Your Vision")

chat_container = st.container(height=520, border=True)

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
            if msg.get("image_url"):
                st.image(msg["image_url"], use_container_width=True)

status_placeholder = st.empty()

def update_status(msg: str):
    st.session_state.status = msg
    status_placeholder.info(msg)

prompt = st.chat_input("Describe the background, style, lighting, atmosphere, mood...")

if prompt and ref_image_url:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        st.chat_message("user").write(prompt)

    replicate_client = ReplicateClient(api_token=replicate_token)
    cloudinary_client = CloudinaryUploader(
        cloud_name=cloud_name, api_key=cloud_key, api_secret=cloud_secret
    )

    update_status(f"🎨 Generating with {MODELS[selected_model]['name']}...")

    generated_url = replicate_client.generate_image(
        model_id=MODELS[selected_model]["replicate_id"],
        prompt=prompt,
        image_url=ref_image_url,
        progress_callback=update_status
    )

    if generated_url:
        st.session_state.last_generated_url = generated_url   # ← Save for manual download

        update_status("📤 Uploading to Cloudinary...")
        upload_result = cloudinary_client.upload_image(
            image_url=generated_url,
            preset_name=selected_size,
            progress_callback=update_status
        )
        
        if upload_result:
            final_url = upload_result["secure_url"]
            response_text = f"✅ Generated using **{MODELS[selected_model]['name']}**\n\n📏 Size: {selected_size}\n\n🔗 [View on Cloudinary]({final_url})"
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "image_url": final_url
            })
            
            with chat_container:
                st.chat_message("assistant").write(response_text)
                st.image(final_url, use_container_width=True)
            
            update_status("✅ Complete!")
            st.code(final_url, language="text")
        else:
            # Upload failed but generation succeeded → show manual download
            update_status("⚠️ Upload to Cloudinary failed, but image was generated!")
            st.error("Cloudinary upload failed. Use the button below to download the image manually.")
            
            # Show the generated image + download button
            st.image(generated_url, use_container_width=True)
            st.download_button(
                label="⬇️ Download Generated Image",
                data=requests.get(generated_url).content,
                file_name="generated_image.jpg",
                mime="image/jpeg"
            )
    else:
        update_status("❌ Generation failed")

if st.session_state.status:
    status_placeholder.info(st.session_state.status)

st.divider()
st.caption("🎨 AI Image Generator | Python 3.12")
