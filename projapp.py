import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os

st.markdown("""
<h1 style="
    text-align:center;
    background: linear-gradient(to left,  orange);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size:60px;
">
San GenAI
</h1>
""", unsafe_allow_html=True)
#st.title("San GenAI")
st.write("San GenAI is an independent educational AI project for learning purpose. Responses may contain inaccuracies")


# ---------------- PAGE ----------------
#st.set_page_config(page_title="San GenAI History")

# ---------------- MONGODB ----------------
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["aidatabase1"]
collection = db["search_history"]

# ---------------- SIDEBAR ----------------
st.sidebar.title("Search History")

# -------- NEW CHAT BUTTON --------
#if st.sidebar.button("➕ New Chat"):
#    st.rerun()

# -------- FETCH OLD SEARCHES --------
all_chats = collection.find().sort("_id", -1)

# -------- SHOW HISTORY --------

for chat in all_chats:
    if st.sidebar.button(chat["question"]):
        st.session_state.selected_question = chat["question"]
        st.session_state.selected_answer = chat["answer"]

# -------- DISPLAY OLD CHAT --------

if "selected_question" in st.session_state:

    st.chat_message("user").write(
        st.session_state.selected_question
    )

    st.chat_message("assistant").write(
        st.session_state.selected_answer
    )

# ------------Project main Code-------------
load_dotenv()  # Loads .env file
api_key = st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    api_key=api_key,
    model="llama-3.3-70b-versatile"
)

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
user_input = st.chat_input("Ask anything ...")

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

# ---------------- SAVE TO DATABASE ----------------
if user_input:
    # Show user message
    st.chat_message("user").write(user_input)
    # Example AI response
    response = f"AI Response: {user_input}"
    # Show AI response
    st.chat_message("assistant").write(response)
    # Save in MongoDB
    collection.insert_one({
        "question": user_input,
        "answer": response
    })


