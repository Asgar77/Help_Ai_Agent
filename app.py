import streamlit as st
from qa_agent import QAAgent

# ✅ Streamlit UI Header
st.title("Help Website Q&A Agent")
st.caption("Process help documentation and ask AI-powered questions!")

# ✅ User Input for Website URL
url = st.text_input("Enter Help Website URL")

# ✅ Session State Initialization
if 'agent' not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ✅ Process Documentation Button
if st.button("Process Documentation") and url:
    with st.spinner("Processing documentation..."):
        agent = QAAgent(url)
        success = agent.process_documentation()
        if success:
            st.session_state.agent = agent
            st.success(f"Documentation from {url} processed successfully!")
        else:
            st.error("Failed to process documentation.")

# ✅ Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_question := st.chat_input("Ask a question about the documentation"):
    with st.chat_message("user"):
        st.markdown(user_question)

    st.session_state.messages.append({"role": "user", "content": user_question})

    if not st.session_state.agent:
        response = "Please process a help website first."
    else:
        with st.spinner("Generating answer..."):
            response = st.session_state.agent.answer_question(user_question)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
