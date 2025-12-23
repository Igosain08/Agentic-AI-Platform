"""
Simple Streamlit demo for Agentic AI Platform.
This makes deployment super easy on Streamlit Cloud!
"""

import streamlit as st
import httpx
import os
from typing import Optional

# Configure page
st.set_page_config(
    page_title="Agentic AI Platform",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agentic AI Platform")
st.markdown("**Production-ready multi-agent AI system with MCP integration**")
st.caption("⚡ Optimized configuration: Temperature 0.7 (P99 latency: 25.3s) | MLflow tracking enabled")

# API URL - defaults to Railway backend, but can be set via environment variable
API_URL = os.getenv("API_URL", "https://web-production-770e.up.railway.app")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_url = st.text_input("API URL", value=API_URL, help="URL of the FastAPI backend")
    
    st.markdown("---")
    st.markdown("### 📚 About")
    st.markdown("""
    This platform demonstrates:
    - Multi-agent orchestration
    - MCP (Model Context Protocol) integration
    - Natural language database queries
    - Production-ready architecture
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown("""
    - [GitHub Repository](https://github.com/Igosain08/Agentic-AI-Platform)
    - [API Documentation]({}/docs)
    """.format(api_url))

# Main interface
st.header("💬 Chat with the Agent")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    import uuid
    st.session_state.thread_id = str(uuid.uuid4())

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about the database..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = httpx.post(
                    f"{api_url}/api/v1/query",
                    json={
                        "message": prompt,
                        "thread_id": st.session_state.thread_id
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Display response
                st.markdown(data["response"])
                
                # Show metadata
                with st.expander("📊 Metadata"):
                    st.json(data.get("metadata", {}))
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["response"]
                })
                
            except httpx.RequestError as e:
                st.error(f"❌ Connection error: {str(e)}")
                st.info("💡 Make sure the API is running at the configured URL")
            except httpx.HTTPStatusError as e:
                st.error(f"❌ API error: {e.response.status_code}")
                st.json(e.response.json())
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Example queries
st.markdown("---")
st.header("💡 Example Queries")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📦 List buckets"):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("🏨 Top hotels"):
        st.session_state.messages = []
        st.rerun()

with col3:
    if st.button("🔄 New conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Built with ❤️ using LangGraph, LangChain, FastAPI, and Streamlit</p>
    <p>Powered by Model Context Protocol (MCP) and Couchbase</p>
</div>
""", unsafe_allow_html=True)

