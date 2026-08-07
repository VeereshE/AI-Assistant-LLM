import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import httpx
import os
import re

load_dotenv()

INITIAL_ASSISTANT_MESSAGE = "Hi, I'm AI Assistant. How can I help you today?"


def sanitize_reply(text: str) -> str:
    # Remove any leaked internal reasoning blocks.
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()


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
    page_title="Your Smart AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css("styles.css")



with st.sidebar:

    if st.button("+ Start New Chat"):
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

    st.markdown("""
   <h1 style="margin-top:0; text-align:center;"> 🤖 Your AI Assistant </h1>

    <p style="color:#c9d1d9; line-height:1.6; margin-bottom:18px;">
        Your all-in-one AI companion for coding, learning, writing, and
        problem-solving.
    </p>

    <div style="display:flex; flex-direction:column; gap:10px; color:#ffffff;">
        <div>⚡ <strong>Fast Responses</strong></div>
        <div>🧠 <strong>Smart Reasoning</strong></div>
        <div>💻 <strong>Coding Support</strong></div>
        <div>✍️ <strong>Content Creation</strong></div>
    </div>

    <br>

    <strong style="color:white;">Type your message...</strong>

    <p style="margin-top:10px; line-height:1.6;">
        Ask anything—from coding and debugging to writing, research,
        and creative ideas.
    </p>
    """, unsafe_allow_html=True)

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

# Prompt suggestions in array
prompt_suggestions = [
    "How do I fix a bug in my code?",
    "Explain this error message.",
    "What is the best way to optimize this function?",
    "How can I improve the performance of my application?",
]
selected_prompt = None
has_user_messages = any(msg.get("role") == "user" for msg in st.session_state.messages)
if not has_user_messages:
    st.markdown("#### Prompt Suggestions")

    for suggestion in prompt_suggestions:
        if st.button(suggestion, key=f"suggestion_{suggestion}"):
            selected_prompt = suggestion

prompt = st.chat_input("Type your message...")
if not prompt and selected_prompt:
    prompt = selected_prompt

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

                        # Latest user message
                        user_message = st.session_state.messages[-1]["content"].lower()

                        reasoning_keywords = ["error","issue", "bug","fix", "debug", "resolve","problem","exception","traceback","stack trace","not working","failed","crash","why","how to fix","module not found","typeerror","valueerror","attributeerror","indexerror","keyerror","importerror","syntaxerror","nameerror","zerodivisionerror","recursionerror","memoryerror","overflowerror","assertionerror","connectionerror","timeouterror"]

                        # Select model
                        if any(keyword in user_message for keyword in reasoning_keywords):
                            model = "qwen/qwen3.6-27b"
                            extra_args = {}
                        else:
                            model = "llama-3.3-70b-versatile"
                            extra_args = {}

                        response = client.chat.completions.create(
                            model=model,
                            messages=st.session_state.messages,
                            stream=False,
                            **extra_args
                        )

                        assistant_reply = response.choices[0].message.content

                        reply = sanitize_reply(assistant_reply)

                        # print(f"reply: {reply}")

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
