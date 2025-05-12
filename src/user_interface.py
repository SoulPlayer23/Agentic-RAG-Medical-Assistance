import streamlit as st
import asyncio
import uuid
from datetime import datetime
from html import escape

from app import orchestrator_agent, UserContext
from agents import InputGuardrailTripwireTriggered, Runner

from models.tool_models import Diagnosis, PatientResponse, PubMedResponse, ReportAnalysis

# Page configuration
st.set_page_config(
    page_title="MediCortex AI",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.html(
f"""
    <style>
    /* Main background */
    .stApp {{
        background-color: #0a0a0a;
    }}
    
    /* Sidebar */
    .st-emotion-cache-6qob1r {{
        background-color: #1a1a1a;
        border-right: 1px solid #2d2d2d;
    }}
    
    /* Chat messages */
    .chat-message {{
        padding: 1rem 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        max-width: 80%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }}
    .chat-message.user {{
        background-color: #1e3a8a;
        color: #e0f2fe;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }}
    .chat-message.assistant {{
        background-color: #2d2d2d;
        border: 1px solid #3f3f3f;
        color: #e5e5e5;
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }}
    /* Timestamp */
    .timestamp {{
        font-size: 0.75rem;
        color: #a3a3a3;
        margin-top: 0.5rem;
    }}
    /* Input box */
    .stChatInput {{
        background-color: #1a1a1a;
        color: #e5e5e5;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }}
    /* Sidebar widgets */
    .st-emotion-cache-1y4p8pa {{
        padding: 1rem;
        color: #e5e5e5;
    }}
    /* Title */
    h1 {{
        color: #93c5fd;
        font-size: 2rem !important;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 0.5rem;
    }}
    /* Preferences section */
    .st-emotion-cache-1v0mbdj {{
        border: 1px solid #3f3f3f;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    
    /* Dark mode form elements */
    .stDateInput, .stSelectbox, .stFileUploader {{
        border-color: #3f3f3f !important;
        color: #e5e5e5 !important;
    }}
    
    /* Button styling */
    .stButton>button {{
        background-color: #2563eb;
        color: white !important;
        border: none;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        background-color: #1d4ed8 !important;
        transform: translateY(-1px);
    }}
    
    /* Divider color */
    hr {{
        border-color: #3f3f3f !important;
    }}

    /* Patient Details Section */
    .patient-section {{
        background: #1a1a1a;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}

    .patient-content {{
        color: #a3a3a3;
        line-height: 1.6;
    }}

    .patient-line {{
        margin-bottom: 0.8rem;
        white-space: pre-wrap;
    }}

    .subsection-title {{
        color: #e5e5e5;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
    }}

    .data-list {{
        padding-left: 1.5rem;
        margin-bottom: 1rem;
    }}

    .data-item {{
        margin-bottom: 0.5rem;
        list-style-type: disc;
        color: #a3a3a3;
    }}

    /* Diagnosis Section */
    .diagnosis-section {{
        background: #1a1a1a;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}

    .diagnosis-content {{
        color: #a3a3a3;
        line-height: 1.6;
    }}

    .diagnosis-line {{
        margin-bottom: 0.8rem;
        white-space: pre-wrap;
    }}

    .recommendation-title {{
        color: #e5e5e5;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }}

    .recommendation-list {{
        padding-left: 1.5rem;
    }}

    .recommendation-item {{
        margin-bottom: 0.5rem;
        list-style-type: disc;
        color: #a3a3a3;
    }}

    /* PubMed Papers Section */
    .pubmed-section {{
        background: #1a1a1a;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}

    .papers-container {{
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
    }}

    .paper-card {{
        background: #262626;
        border-radius: 8px;
        padding: 1.2rem;
        border-left: 4px solid #3b82f6;
    }}

    .paper-header {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.8rem;
    }}

    .paper-number {{
        background: #3b82f6;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        flex-shrink: 0;
    }}

    .paper-title {{
        color: #e5e5e5;
        margin: 0;
        font-size: 1.1rem;
    }}

    .paper-abstract {{
        color: #a3a3a3;
        line-height: 1.6;
        margin: 0;
        white-space: pre-wrap;
    }}

    /* Report/Scan Analysis Section */
    .report-section {{
        background: #1a1a1a;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}

    .report-content {{
        color: #a3a3a3;
        line-height: 1.6;
    }}

    .report-analysis {{
        margin-bottom: 1rem;
        white-space: pre-wrap;
    }}

    .recommendation-title {{
        color: #e5e5e5;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }}

    .recommendation-list {{
        padding-left: 1.5rem;
    }}

    .recommendation-item {{
        margin-bottom: 0.5rem;
        list-style-type: disc;
        color: #a3a3a3;
    }}
    </style>
    """)

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
    html = ""
    
    if isinstance(output, PatientResponse):  # Patient Retrieval
        html = f"""
        <div class="patient-section">
            <h3 class="section-title">👤 Patient Details: {output.patient_name}</h3>
            <div class="patient-content">
                <p class="patient-line"><strong>Patient ID:</strong> {output.patient_id}</p>
                <p class="patient-line"><strong>Name:</strong> {output.patient_name}</p>
                <p class="patient-line"><strong>Age:</strong> {str(output.age)} days</p>
                <p class="patient-line"><strong>Gender:</strong> {output.gender}</p>

                <h4 class="subsection-title">Medical History:</h4>
                <ul class="data-list">
        """
        for history in output.medical_history:
            html += f"<li class='data-item'>{history}</li>"
        html += """
                </ul>
                <h4 class="subsection-title">Lab Reports:</h4>
                <ul class="data-list">
        """
        for report in output.lab_reports:
            html += f"<li class='data-item'>{report}</li>"
        html += f"""
                </ul>
                <h4 class="subsection-title">Diagnosis:</h4> 
                <p class="patient-line"><strong>{output.diagnosis}</p>

                <h4 class="subsection-title">Recommendations:</h4>
                <ul class="data-list">
        """
        for recommendation in output.recommendations:
            html += f"<li class='data-item'>{recommendation}</li>"
        html += """
                    </ul>
                </div>
            </div>
        """
        return html

        
    elif isinstance(output, Diagnosis):  # Diagnosis
        html = f"""
        <div class="diagnosis-section">
        <h3 class="section-title">🩺 Diagnosis</h3>
        <div class="diagnosis-content">
            <p class="diagnosis-line"><strong>Symptoms:</strong> {output.symptoms}</p>
            <p class="diagnosis-line"><strong>Diagnosis:</strong> {output.diagnosis}</p>
            <p class="diagnosis-line"><strong>Confidence:</strong> {output.confidence}</p>

            <h4 class="recommendation-title">Recommendations:</h4>
            <ul class="recommendation-list">
        """
        for recommendation in output.recommendations:
            html += f"<li class='recommendation-item'>{recommendation}</li>"
        html += """
            </ul>
        </div>
        </div>
        """
        return html
        
    elif isinstance(output, list) and all(isinstance(p, PubMedResponse) for p in output): 
        html = """
        <div class="pubmed-section">
        <h3 class="section-title">📄 Relevant PubMed Papers</h3>
        <div class="papers-container">
        """
        for idx, paper in enumerate(output, 1):
            html += f"""
            <div class="paper-card">
                <div class="paper-header">
                    <span class="paper-number">#{idx}</span>
                    <h4 class="paper-title">{paper.title}</h4>
                </div>
                <div class="paper-body">
                    <p class="paper-abstract"><strong>Abstract:</strong> {paper.abstract}</p>
                </div>
            </div>
            """
        
        html += """
            </div>
        </div>
        """
        return html
    
    elif isinstance(output, ReportAnalysis):  # Report Analysis
        html = f"""
        <div class="report-section">
        <h3 class="section-title">📋 Report/Scan Analysis</h3>
        <div class="report-content">
            <p class="report-analysis"><strong>Analysis:</strong> {output.analysis}</p>
            
            <h4 class="recommendation-title">Recommendations:</h4>
            <ul class="recommendation-list">
            """
        for recommendation in output.recommendations:
            html += f"<li class='recommendation-item'>{recommendation}</li>"
        html += """
            </ul>
        </div>
        </div>
        """
        
        return html
    
    else:
        html = f"{output.get('response', 'N/A')}"
    
    # Default
    return html

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
    st.title("⚙️ Preferences")
    
    st.subheader("Query Preferences")
    preferred_number_papers = st.selectbox(
        "Preferred Number of Papers",
        options=["1", "2", "3", "4", "5"]
    )

    st.subheader("Date Range")
    from_date = st.date_input(
        "From Date",
        value=datetime.now().date()
    )
    to_date = st.date_input(
        "To Date",
        value=datetime.now().date()
    )
    
    attachment = st.file_uploader(
        "Report/Scans",
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
        help="Upload any relevant reports or scans."
    )
    
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
            st.html(f"""
            <div class="chat-message user">
                <div class="content">
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """)
        else:
            st.html(f"""
            <div class="chat-message assistant">
                <div class="content">
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """)

# User input
user_input = st.chat_input("Ask medical questions...")
if user_input:
    st.session_state.user_context.preferred_number_of_papers = preferred_number_papers
    st.session_state.user_context.attachment_type = attachment.type if attachment else None
    st.session_state.user_context.attachment_name = attachment.name if attachment else None
    st.session_state.user_context.attachment = attachment
    st.session_state.user_context.from_date = from_date
    st.session_state.user_context.to_date = to_date
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