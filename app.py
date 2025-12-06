import streamlit as st
import time
import requests
import uuid
import json

# Configuration
BASE_URL = "https://backend-zenark.onrender.com"
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyMzQ1Njc4OTAifQ.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"

def init_session():
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Initialize chat history for each mode if not exists
    if 'zen_chat_history' not in st.session_state:
        st.session_state.zen_chat_history = [
            {"role": "assistant", "content": "Hello! I'm here to listen. How are you feeling right now?"}
        ]
    if 'study_buddy_history' not in st.session_state:
        st.session_state.study_buddy_history = [
            {"role": "assistant", "content": "Hi there! I'm your Study Buddy. What exam or subject are you preparing for today?"}
        ]

def call_api(endpoint, payload=None, method="POST", params=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "POST":
            response = requests.post(url, json=payload, params=params)
        elif method == "GET":
            response = requests.get(url, params=params)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": response.text if 'response' in locals() else "No response"}

def sidebar_tools():
    st.sidebar.title("Settings & Tools")
    st.sidebar.info(f"Session ID: {st.session_state.session_id}")

    # Health Check
    if st.sidebar.button("Check Backend Health"):
        with st.sidebar.status("Checking health..."):
            result = call_api("/health", method="GET")
            if "error" in result:
                st.sidebar.error(f"Health Check Failed: {result['error']}")
            else:
                st.sidebar.success("Backend is Healthy!")

    st.sidebar.divider()

    # Generate Report
    if st.sidebar.button("Generate Report"):
        payload = {
            "token": TEST_TOKEN
            # "session_id": st.session_state.session_id # Not needed per backend update
        }
        with st.sidebar.status("Generating report..."):
            result = call_api("/generate_report", payload=payload)
            st.sidebar.json(result)

    # Save Chat
    if st.sidebar.button("Save Chat"):
        # Combine histories or pick current? Let's save Zen Chat for now or both?
        # The API expects "conversation" list.
        # Let's save the current active history if possible, else Zen Chat default
        current_history = []
        if st.session_state.page == 'zen_chat':
            current_history = st.session_state.zen_chat_history
        elif st.session_state.page == 'study_buddy':
            current_history = st.session_state.study_buddy_history
        
        payload = {
            "conversation": current_history,
            "name": f"Chat_{int(time.time())}",
            "session_id": st.session_state.session_id,
            "token": TEST_TOKEN
        }
        with st.sidebar.status("Saving chat..."):
            result = call_api("/save_chat", payload=payload)
            st.sidebar.json(result)

    # Score Conversation
    if st.sidebar.button("Score Conversation"):
        with st.sidebar.status("Scoring conversation..."):
            # API requires session_id AND token
            payload = {
                "session_id": st.session_state.session_id,
                "token": TEST_TOKEN
            }
            result = call_api("/score_conversation", payload=payload) 
            st.sidebar.json(result)

    st.sidebar.divider()
    
    # Router Memory
    student_id = st.sidebar.text_input("Student ID", value="student_1")
    if st.sidebar.button("Get Router Memory"):
        endpoint = f"/router-memory/{st.session_state.session_id}/{student_id}"
        with st.sidebar.status("Fetching memory..."):
            result = call_api(endpoint, method="GET")
            st.sidebar.json(result)

def main():
    st.set_page_config(page_title="AI Response Testing", page_icon="🤖", layout="wide")
    init_session()
    sidebar_tools()

    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'zen_chat':
        show_chat_interface("Zen Chat", "zen_chat_history", "/chat", "message")
    elif st.session_state.page == 'study_buddy':
        show_chat_interface("Study Buddy", "study_buddy_history", "/exam_buddy", "question")

def show_home():
    st.title("AI Response Testing")
    st.write("Select a mode to test AI responses:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Zen Chat", use_container_width=True):
            st.session_state.page = 'zen_chat'
            st.rerun()

    with col2:
        if st.button("Study Buddy", use_container_width=True):
            st.session_state.page = 'study_buddy'
            st.rerun()

def show_chat_interface(title, history_key, endpoint, payload_key):
    st.title(title)
    
    if st.button("← Back to Home"):
        st.session_state.page = 'home'
        st.rerun()

    # Display chat messages
    for message in st.session_state[history_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input(f"Message {title}..."):
        # Add user message to history
        st.session_state[history_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call Backend
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            payload = {
                payload_key: prompt,
                "session_id": st.session_state.session_id,
                # "token": TEST_TOKEN # Token might not be needed for exam_buddy based on user example, but keeping if safe? 
                # User example didn't show token for exam_buddy, but let's try without first or with?
                # The curl example didn't have token. Let's try without token for exam_buddy if it fails?
                # Actually, let's include it if it doesn't hurt, or maybe exclude it?
                # User said: "The endpoint will be live... Working Example... { question, session_id, context }"
                # No token in example. But /chat needed it.
                # Let's assume it might not need it, OR it accepts it.
                # Let's stick to the example.
            }
            # If it's chat, we know we need token.
            if endpoint == "/chat":
                payload["token"] = TEST_TOKEN
                payload["text"] = prompt # Legacy support just in case
            
            # For exam_buddy, user didn't explicitly say NO token, but didn't include it.
            # But previous 500s might have been due to missing 'question'.
            # Let's try sending token anyway, usually harmless.
            # Wait, user example for curl: -d '{"question":"...","session_id":"..."}'
            # NO TOKEN in curl example.
            
            response_data = call_api(endpoint, payload=payload)
            
            if "error" in response_data:
                full_response = f"Error: {response_data['error']}\nDetails: {response_data.get('details', '')}"
                message_placeholder.markdown(full_response)
            else:
                # Try to extract the response text. 
                # Adjust this based on actual API response structure.
                if isinstance(response_data, str):
                    full_response = response_data
                elif isinstance(response_data, dict):
                    full_response = response_data.get("response") or response_data.get("message") or response_data.get("answer") or str(response_data)
                else:
                    full_response = str(response_data)

                # Typing effect
                displayed_response = ""
                for chunk in full_response.split(" "):
                    displayed_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(displayed_response + "▌")
                message_placeholder.markdown(full_response)
        
        # Add assistant response to history
        st.session_state[history_key].append({"role": "assistant", "content": full_response})

    st.divider()
    
    # End Chat Flow
    if st.button("End Chat & Analyze"):
        with st.spinner("Saving conversation..."):
            # Save Chat
            current_history = st.session_state[history_key]
            payload = {
                "conversation": current_history,
                "name": f"Chat_{int(time.time())}",
                "session_id": st.session_state.session_id,
                "token": TEST_TOKEN
            }
            save_result = call_api("/save_chat", payload=payload)
            
            if "error" in save_result:
                st.error(f"Failed to save chat: {save_result['error']}")
            else:
                st.success("Conversation saved successfully!")
                st.session_state.chat_ended = True

    if st.session_state.get("chat_ended", False):
        st.write("### Analysis Options")
        
        if st.button("Generate Report", use_container_width=True):
            with st.spinner("Generating report..."):
                # Report payload (Token only per latest backend update)
                report_payload = {"token": TEST_TOKEN}
                report_result = call_api("/generate_report", payload=report_payload)
                
                if "error" in report_result:
                    st.error(f"Error generating report: {report_result['error']}")
                else:
                    # Clean Report UI
                    st.markdown("---")
                    st.subheader("📊 Conversation Report")
                    
                    # Extract fields
                    summary = report_result.get("summary", "No summary available")
                    score = report_result.get("score", "N/A")
                    agents_report = report_result.get("report", {}).get("report", [])
                    
                    # Display Summary & Score
                    st.info(f"**Summary:** {summary}")
                    st.metric("Distress Score", score)
                    
                    # Display Agent Analysis
                    st.write("#### 🕵️ Agent Analysis")
                    for agent in agents_report:
                        with st.expander(f"{agent.get('name', 'Unknown Agent')}", expanded=True):
                            st.write(agent.get('content', 'No content available'))

if __name__ == "__main__":
    main()
