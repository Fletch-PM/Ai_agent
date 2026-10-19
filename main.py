import base64

import streamlit as st

from app.agent.graph import app as agent_flow
from app.tools.voice.voice import speech_to_text, text_to_speech


st.set_page_config(page_title="JARVIS", page_icon="J")

st.session_state.setdefault("messages", [])
st.session_state.setdefault("stt_enabled", True)
st.session_state.setdefault("tts_enabled", True)

with st.sidebar:
    st.subheader("Voice controls")
    st.checkbox("Enable speech-to-text", key="stt_enabled")
    st.checkbox("Enable text-to-speech", key="tts_enabled")


def play_tts(audio):
    audio_data = base64.b64encode(audio).decode("ascii")
    st.html(
        f'<audio autoplay style="display:none" '
        f'src="data:audio/mpeg;base64,{audio_data}"></audio>'
    )


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def respond_to(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = agent_flow.invoke({"user_input": user_input, "messages": []})
            answer = result["messages"][0].content
        st.markdown(answer)

        if st.session_state.tts_enabled:
            audio = text_to_speech(answer)
            if audio:
                play_tts(audio)

    st.session_state.messages.append({"role": "assistant", "content": answer})


prompt = st.chat_input(
    "Write a message or use the microphone...",
    accept_audio=st.session_state.stt_enabled,
)

if prompt:
    if isinstance(prompt, str):
        user_input = prompt.strip()
        audio_input = None
    else:
        user_input = prompt.text.strip() if prompt.text else ""
        audio_input = prompt.audio

    if st.session_state.stt_enabled and audio_input:
        with st.spinner("Transcribing..."):
            spoken_text = speech_to_text(audio_input)
        user_input = spoken_text.strip() if spoken_text else user_input

    if user_input:
        respond_to(user_input)
    else:
        st.warning("I could not hear a message. Please try again.")
