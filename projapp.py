import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os

load_dotenv()  # Loads .env file
api_key = st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    api_key=api_key,
    model="llama-3.3-70b-versatile"
)

st.title("Gen AI by San Xavi")

# Store chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat historys
for msg in st.session_state["messages"]:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    else:
        st.chat_message("assistant").write(msg.content)

# User input
user_input = st.chat_input("San Xavi asking ...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state["messages"].append(HumanMessage(content=user_input))
    with st.spinner("Thinking..."):
        try:
            response = llm.invoke(st.session_state["messages"])
            ai_reply = getattr(response, "content", str(response))
            st.chat_message("assistant").write(ai_reply)
            st.session_state["messages"].append(AIMessage(content=ai_reply))
        except Exception as e:
            st.error(f"Error: {e}")