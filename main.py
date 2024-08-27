import base64
import requests
import streamlit as st
from openai import OpenAI
from pathlib import Path

client = OpenAI(api_key = "OPENAI_API_KEY")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

st.set_page_config(page_title="Eye Talker", page_icon="👁️")

st.sidebar.header("Instructions")
st.sidebar.write("1. Upload an image file (jpg, jpeg, png).")
st.sidebar.write("2. Click 'Generate Text Response' to get a description of the image.")
st.sidebar.write("3. Click 'Generate Audio Response' to hear the description.")
st.sidebar.write("4. Download the audio file if needed.")

if "text_response" not in st.session_state:
    st.session_state.text_response = None
if "audio_file_path" not in st.session_state:
    st.session_state.audio_file_path = None

st.title("👁️ Eye Talker")
st.write("Upload an image, and the AI will describe it for you!")

image_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if image_file:
    st.image(image_file, caption="Uploaded Image", use_column_width=False, width=300)

    base64_image = encode_image(image_file)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {client.api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    if st.button('Generate Text Response'):
        with st.spinner('Analyzing the image...'):
            text_response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if text_response.status_code == 200:
            st.session_state.text_response = text_response.json()["choices"][0]["message"]["content"]
            st.success("Text response generated successfully!")
        else:
            st.error("There was an error with the API request. Please try again.")

    if st.session_state.text_response:
        st.text_area("AI Response", st.session_state.text_response, key="text_response_area")

    if st.session_state.text_response and st.button('Generate Audio Response'):
        with st.spinner('Generating audio response...'):
            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=st.session_state.text_response
            )
            response.stream_to_file(speech_file_path)
            st.session_state.audio_file_path = speech_file_path
            st.success("Audio response generated successfully!")

    if st.session_state.audio_file_path:
        st.audio(str(st.session_state.audio_file_path), format="audio/mp3")
        st.download_button("Download Audio", data=open(st.session_state.audio_file_path, "rb").read(), file_name="speech.mp3")

else:
    st.info("Please upload an image to get started.")
