import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

INITIAL_ASSISTANT_MESSAGE = "Hi, I'm AI Assistant. How can I help you today?"


def load_css(file_name: str) -> None:
    with open(file_name, encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def render_chat_message(role: str, content: str) -> None:
    avatar = "🤖" if role == "assistant" else "👤"
    left_margin, content_col, right_margin = st.columns([0.7, 2.4, 0.7])
    with content_col:
        if role == "user":
            left_space, message_col = st.columns([0.5, 1])
        else:
            message_col, right_space = st.columns([1, 0.35])

        with message_col:
            with st.chat_message(role, avatar=avatar):
                st.markdown(content)

st.set_page_config(
    page_title="AI ChatBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css("styles.css")



with st.sidebar:
    st.markdown("""
    <div class="sidebar-card">
        <p class="sidebar-title">Pulse Console</p>
        <p class="sidebar-subtitle">Groq-powered assistant with a cleaner control panel.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🗑 Clear Conversation"):
        st.session_state.messages = [
            {
                "role":"system",
                "content":"You are a helpful assistant."
            },
            {
                "role":"assistant",
                "content":INITIAL_ASSISTANT_MESSAGE
            }
        ]
        st.rerun()

    st.divider()

    st.metric("Model","Llama 3.3 70B")
    st.metric("Provider","Groq")
    st.metric("Status","🟢 Online")


st.markdown("""
    <div class="fixed-title-bar">
        <div class="title">
        AI Assistant 👋🏻
        </div>
    </div>
    <div class="title-spacer"></div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages=[
        {
            "role":"system",
            "content":"You are a helpful assistant."
        },
        {
            "role":"assistant",
            "content":INITIAL_ASSISTANT_MESSAGE
        }
    ]

for message in st.session_state.messages:

    if message["role"]=="system":
        continue

    render_chat_message(message["role"], message["content"])

prompt=st.chat_input("Type your message...")

if prompt:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )

    render_chat_message("user", prompt)

    left_margin, content_col, right_margin = st.columns([0.7, 2.4, 0.7])
    with content_col:
        assistant_col, assistant_spacer = st.columns([1.45, 0.95])
        with assistant_col:
            with st.chat_message("assistant",avatar="🤖"):

                with st.spinner("Thinking..."):

                    api_key=os.getenv("GROQ_API_KEY")

                    if not api_key:
                        st.error("Missing GROQ_API_KEY")
                        st.stop()

                    try:

                        client=Groq(
                            api_key=api_key,
                            http_client=httpx.Client(verify=False)
                        )

                        response=client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=st.session_state.messages
                        )

                        reply=response.choices[0].message.content

                    except Exception as e:
                        reply=f"❌ {e}"

                st.markdown(reply)

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":reply
        }
    )

    st.rerun()
