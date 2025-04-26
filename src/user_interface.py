import streamlit as st
import asyncio
import uuid
from datetime import datetime

# Import the travel agent from v5
from app import orchestrator_agent, UserContext
from agents import InputGuardrailTripwireTriggered, Runner

# Page configuration
st.set_page_config(
    page_title="MediCortex AI",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message {
        flex: 1;
        color: #000000;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history and user context
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_context" not in st.session_state:
    st.session_state.user_context = UserContext(
        user_id=str(uuid.uuid4())
    )

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

# Function to format agent responses based on output type
def format_agent_response(output):
    # Check if output is a Pydantic model and convert to dict
    if hasattr(output, "model_dump"):
        output = output.model_dump()
    
    if isinstance(output, dict):
        # Handle structured outputs
        if "patient_id" in output:  # Patient Retrieval
            html = f"""
            <h3>Patient Details: {output.get('patient_name', ' ')}</h3>
            <p><strong>Patient ID:</strong> {output.get('patient_id', 'N/A')}</p>
            <p><strong>Name:</strong> {output.get('patient_name', 'N/A')}</p>
            <p><strong>Age:</strong> {output.get('age', 'N/A')} days</p>
            <p><strong>Gender:</strong> ${output.get('budget', 'N/A')}</p>
            
            <h4>Medical history:</h4>
            <ul>
            """
            for history in output.get('medical_history', []):
                html += f"<li>{history}</li>"
            html += "</ul>"
            
            html += f"<<h4>Lab reports:</h4>"
            html += "<ul>"
            for report in output.get('lab_reports', []):
                html += f"<li>{report}</li>"
            html += "</ul>"
            
            html += f"<p><strong>Diagnosis:</strong> {output.get('diagnosis', '')}</p>"

            html += f"<<h4>Recommendations:</h4>"
            html += "<ul>"
            for recommendation in output.get('recommendations', []):
                html += f"<li>{recommendation}</li>"
            html += "</ul>"

            return html
            
        elif "symptoms" in output:  # Diagnosis
            html = f"""
            <h3>Diagnosis</h3>
            <p><strong>Symptoms:</strong> {output.get('symptoms', 'N/A')}</p>
            <p><strong>Diagnosis:</strong> {output.get('diagnosis', 'N/A')}</p>
            <p><strong>Confidence:</strong> {output.get('confidence', 'N/A')}</p>

            <h4>Recommendations:</h4>
            <ul>
            """

            for recommendation in output.get('recommendations', []):
                html += f"<li>{recommendation}</li>"
            html += "</ul>"

            return html
            
        elif "citations" in output:  # PubMed Retrieval
            html = f"""
            <h3>PubMed Papers</h3>
            <p><strong>Title:</strong> {output.get('title', 'N/A')}</p>
            <p><strong>Abstract:</strong> {output.get('abstract', 'N/A')}</p>
            
            <h4>Citations:</h4>
            <ul>
            """
            for citation in output.get('citations', []):
                html += f"<li>{citation}</li>"
            html += "</ul>"
            
            return html
    
    # Default: return as string
    return str(output)

# Function to handle user input
def handle_user_message(user_input: str):
    # Add user message to chat history immediately
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    
    # Set the message for processing in the next rerun
    st.session_state.processing_message = user_input

# Sidebar for user preferences
with st.sidebar:
    st.title("Query Preferences")
    
    st.subheader("About You")
    traveler_name = st.text_input("Your Name", value="User")
    
    st.subheader("Query Preferences")
    preferred_number_papers = st.multiselect(
        "Prefferred Number of Papers",
        options=["1", "2", "3", "4", "5"]
    )
    
    attachment = st.file_uploader(
        "Report/Scans",
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
        help="Upload any relevant reports or scans."
    )
    
    if st.button("Save Preferences"):
        st.session_state.user_context.preferred_number_of_papers = preferred_number_papers
        st.session_state.user_context.attachment = attachment
        st.success("Preferences saved!")
    
    st.divider()
    
    if st.button("Start New Conversation"):
        st.session_state.chat_history = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.success("New conversation started!")

# Main chat interface
st.title("⚕️ Medical Assistant Agent")
st.caption("Ask me for diagnosis, medical research papers, patient details, and more!")
st.divider()

# Display chat messages
for message in st.session_state.chat_history:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state.user_context.user_id}" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# User input
user_input = st.chat_input("Ask medical questions...")
if user_input:
    handle_user_message(user_input)
    st.rerun()

# Process message if needed
if st.session_state.processing_message:
    user_input = st.session_state.processing_message
    st.session_state.processing_message = None
    
    # Process the message asynchronously
    with st.spinner("Thinking..."):
        try:
            # Prepare input for the agent using chat history
            if len(st.session_state.chat_history) > 1:
                # Convert chat history to input list format for the agent
                input_list = []
                for msg in st.session_state.chat_history:
                    input_list.append({"role": msg["role"], "content": msg["content"]})
            else:
                # First message
                input_list = user_input
            
            # Run the agent with the input
            result = asyncio.run(Runner.run(
                orchestrator_agent, 
                input_list, 
                context=st.session_state.user_context
            ))
            
            # Format the response based on output type
            response_content = format_agent_response(result.final_output)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            
        except Exception as e:
            if type(e) == InputGuardrailTripwireTriggered:
                error_message = "This query is not related to medical topics. Reasoning:" + e.guardrail_result.output.output_info.reasoning
            else:
                error_message = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
        
        # Force a rerun to display the AI response
        st.rerun()

# Footer
st.divider()
st.caption("Powered by OpenAI Agents SDK | Built with Streamlit")