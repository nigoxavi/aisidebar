import streamlit as st
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os

# ---------------- PAGE DESIGN ----------------

st.markdown("""
<h1 style="
    text-align:center;
    background: linear-gradient(to left, orange);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size:60px;
">
San GenAI
</h1>
""", unsafe_allow_html=True)

st.write(
    "San GenAI is an independent educational AI project for learning purpose. Responses may contain inaccuracies."
)

# ---------------- LOAD ENV ----------------

load_dotenv()

# ---------------- MONGODB CONNECTION ----------------

MONGO_URI = st.secrets["MONGO_URI"]

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=30000
    )

    # Test MongoDB connection
    client.admin.command("ping")

    db = client["aidatabase1"]
    collection = db["search_history"]

    # st.success("MongoDB Connected Successfully!")

except Exception as e:
    st.error("MongoDB Connection Failed")
    st.exception(e)
    st.stop()

# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

# ---------------- SIDEBAR ----------------

st.sidebar.title("Search History")

all_chats = collection.find().sort("_id", -1)

for idx, chat in enumerate(all_chats):

    question = chat.get("question", "No Question")
    answer = chat.get("answer", "No Answer")

    # UNIQUE BUTTON KEY
    if st.sidebar.button(
        question,
        key=f"chat_button_{chat['_id']}"
    ):

        st.session_state.selected_chat = {
            "question": question,
            "answer": answer
        }

# ---------------- SHOW SELECTED CHAT ----------------

if st.session_state.selected_chat:

    st.chat_message("user").write(
        st.session_state.selected_chat["question"]
    )

    st.chat_message("assistant").write(
        st.session_state.selected_chat["answer"]
    )

# ---------------- GROQ API ----------------

api_key = st.secrets["GROQ_API_KEY"]

# ---------------- LLM ----------------

llm = ChatGroq(
    api_key=api_key,
    model="llama-3.3-70b-versatile"
)

# ---------------- DISPLAY CURRENT SESSION ----------------

for msg in st.session_state.messages:

    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)

    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# ---------------- USER INPUT ----------------

user_input = st.chat_input("Ask anything...")

# ---------------- PROCESS INPUT ----------------

if user_input:

    # Show user message
    st.chat_message("user").write(user_input)

    # Save user message
    st.session_state.messages.append(
        HumanMessage(content=user_input)
    )

    with st.spinner("Thinking..."):

        try:

            # LLM RESPONSE
            response = llm.invoke(
                st.session_state.messages
            )

            ai_reply = response.content

            # Show assistant response
            st.chat_message("assistant").write(ai_reply)

            # Save assistant response
            st.session_state.messages.append(
                AIMessage(content=ai_reply)
            )

            # SAVE TO MONGODB
            collection.insert_one({
                "question": user_input,
                "answer": ai_reply
            })

        except Exception as e:

            st.error(f"Error: {e}")
 
#..........bring delete button in the botton............
st.sidebar.markdown("<br>" * 25, unsafe_allow_html=True)

# CLEAR HISTORY BUTTON AT BOTTOM
if st.sidebar.button(
    "🗑️ Clear All History",
    key="clear_history"
):

    try:

        # Delete all MongoDB documents
        collection.delete_many({})

        # Clear selected chat
        st.session_state.selected_chat = None

        # Clear current session messages
        st.session_state.messages = []

        st.sidebar.success("History Cleared Successfully")

        # Refresh app
        st.rerun()

    except Exception as e:

        st.sidebar.error(f"Error: {e}")


