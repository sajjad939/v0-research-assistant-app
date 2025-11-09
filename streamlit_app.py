import streamlit as st
import pandas as pd
from datetime import datetime
import json
from typing import Optional
from ingestion import DocumentProcessor
from agents import AgentOrchestrator
from utils import format_citations, create_agent_graph, render_agent_graph
from reports import ReportGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { max-width: 1400px; margin: 0 auto; }
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    .message-box { 
        padding: 1rem; 
        border-radius: 0.5rem; 
        margin: 0.5rem 0; 
        border-left: 4px solid;
    }
    .researcher { border-left-color: #3498db; background-color: #ecf0f1; }
    .reviewer { border-left-color: #e74c3c; background-color: #fadbd8; }
    .synthesizer { border-left-color: #2ecc71; background-color: #d5f4e6; }
    .inspector { border-left-color: #f39c12; background-color: #fdebd0; }
    .guard { border-left-color: #9b59b6; background-color: #ebdef0; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "documents" not in st.session_state:
    st.session_state.documents = []
    st.session_state.doc_metadata = {}
    st.session_state.embeddings = {}
    st.session_state.agent_messages = []
    st.session_state.final_report = None
    st.session_state.agent_graph = None
    st.session_state.current_round = 0

st.title("🔬 Multi-Agent Research Assistant")
st.markdown("Collaboratively analyze research documents using specialized AI agents")

# Sidebar: Configuration & Upload
with st.sidebar:
    st.header("Configuration")
    
    num_agents = st.slider("Number of Agents", min_value=2, max_value=6, value=4, 
                          help="Select 2-6 agents for the analysis")
    
    num_rounds = st.slider("Analysis Rounds", min_value=1, max_value=6, value=3,
                          help="Number of iterative reasoning rounds")
    
    st.divider()
    st.subheader("Agent Roles")
    agents_enabled = {
        "Researcher": st.checkbox("Researcher (summarizes & extracts claims)", value=True, disabled=True),
        "Reviewer": st.checkbox("Reviewer (critiques & identifies weaknesses)", value=True),
        "Synthesizer": st.checkbox("Synthesizer (aggregates & finds consensus)", value=True),
        "DataInspector": st.checkbox("DataInspector (extracts metrics & datasets)", value=num_agents > 3),
        "CitationGuard": st.checkbox("CitationGuard (ensures proper citations)", value=num_agents > 4),
    }
    
    citation_strictness = st.select_slider(
        "Citation Strictness",
        options=["Lenient", "Moderate", "Strict", "Very Strict"],
        value="Moderate"
    )
    
    st.divider()
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload research documents (PDF, TXT, or paste text)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="Upload 1-20 research documents"
    )
    
    if st.button("Process Uploads", key="process_btn"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                processor = DocumentProcessor()
                progress_bar = st.progress(0)
                
                for idx, file in enumerate(uploaded_files):
                    try:
                        doc_id = f"doc_{len(st.session_state.documents)}"
                        content = file.read().decode('utf-8') if file.type == "text/plain" else processor.read_pdf(file)
                        
                        metadata = processor.parse_metadata(content, file.name)
                        chunks = processor.extract_chunks(content)
                        
                        st.session_state.documents.append({
                            "id": doc_id,
                            "filename": file.name,
                            "content": content,
                            "chunks": chunks
                        })
                        st.session_state.doc_metadata[doc_id] = metadata
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")
                
                st.success(f"✓ Processed {len(st.session_state.documents)} documents")
    
    if st.button("Clear All", key="clear_btn"):
        st.session_state.documents = []
        st.session_state.doc_metadata = {}
        st.session_state.agent_messages = []
        st.session_state.final_report = None
        st.session_state.agent_graph = None
        st.rerun()

# Main content area
col1, col2, col3 = st.columns([1, 2, 1.5])

# Left column: Document metadata
with col1:
    st.subheader("📄 Documents")
    
    if st.session_state.documents:
        for doc in st.session_state.documents:
            with st.expander(f"📋 {doc['filename']}", expanded=False):
                doc_id = doc['id']
                meta = st.session_state.doc_metadata.get(doc_id, {})
                
                st.caption("**Metadata**")
                for key, value in meta.items():
                    if key != "raw_text":
                        st.write(f"- **{key}**: {value}")
                
                st.caption(f"**Content Preview** ({len(doc['chunks'])} chunks)")
                st.text(doc["content"][:300] + "..." if len(doc["content"]) > 300 else doc["content"])
    else:
        st.info("No documents uploaded yet. Use the upload widget to add research papers.")

# Center column: Agent runner & conversation
with col2:
    st.subheader("🤖 Agent Analysis")
    
    if st.session_state.documents:
        col_run, col_export = st.columns(2)
        
        with col_run:
            if st.button("🚀 Run Agent Analysis", key="run_analysis"):
                with st.spinner("Running agents..."):
                    orchestrator = AgentOrchestrator(
                        agents_config=agents_enabled,
                        num_rounds=num_rounds,
                        citation_strictness=citation_strictness
                    )
                    
                    progress_container = st.container()
                    
                    def progress_callback(round_num, agent_name, message):
                        with progress_container:
                            st.write(f"Round {round_num}: {agent_name} analyzing...")
                    
                    messages, graph = orchestrator.run(
                        documents=st.session_state.documents,
                        metadata=st.session_state.doc_metadata,
                        progress_callback=progress_callback
                    )
                    
                    st.session_state.agent_messages = messages
                    st.session_state.agent_graph = graph
                    st.session_state.current_round = num_rounds
                    
                    # Generate final report
                    report_gen = ReportGenerator()
                    st.session_state.final_report = report_gen.generate(
                        messages=messages,
                        documents=st.session_state.documents,
                        metadata=st.session_state.doc_metadata
                    )
                    
                    st.success("✓ Agent analysis complete!")
        
        with col_export:
            if st.session_state.final_report:
                report_format = st.selectbox("Export format", ["Markdown", "JSON"])
                if st.button("📥 Export Report"):
                    if report_format == "Markdown":
                        st.download_button(
                            label="Download Markdown",
                            data=st.session_state.final_report.get("markdown", ""),
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                    else:
                        st.download_button(
                            label="Download JSON",
                            data=json.dumps(st.session_state.final_report, indent=2),
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
    else:
        st.info("Upload documents to begin agent analysis")
    
    # Conversation stream
    st.divider()
    st.subheader("💬 Conversation Stream")
    
    if st.session_state.agent_messages:
        for msg in st.session_state.agent_messages:
            agent_role = msg.get("agent", "unknown").lower()
            css_class = agent_role if agent_role in ["researcher", "reviewer", "synthesizer", "inspector", "guard"] else "default"
            
            with st.container(border=True):
                col_role, col_round, col_conf = st.columns([2, 1, 1])
                with col_role:
                    st.write(f"**{msg.get('agent', 'Unknown')}**")
                with col_round:
                    st.caption(f"Round {msg.get('round', 0)}")
                with col_conf:
                    st.caption(f"Confidence: {msg.get('confidence', 0):.1%}")
                
                st.write(msg.get("summary", ""))
                
                if msg.get("evidence"):
                    with st.expander("📌 Evidence"):
                        for ev in msg["evidence"]:
                            st.write(f"**{ev.get('doc_id')}** (chunk {ev.get('chunk_id')})")
                            st.text(f"\"{ev.get('highlight')}\"")
    else:
        st.info("Run analysis to see agent conversations")

# Right column: Final report & visualization
with col3:
    st.subheader("📊 Final Report")
    
    if st.session_state.final_report:
        report = st.session_state.final_report
        
        st.write("### Key Findings")
        st.write(report.get("summary", "No summary available"))
        
        st.write("### Hypotheses")
        for hyp in report.get("hypotheses", []):
            st.write(f"- {hyp}")
        
        st.write("### Reasoning Chain")
        with st.expander("View agent interaction graph"):
            if st.session_state.agent_graph:
                st.write("Agent communication flow and influence graph")
                render_agent_graph(st.session_state.agent_graph)
    else:
        st.info("Final report will appear here after analysis")
    
    st.divider()
    st.subheader("⚠️ Ethics Notice")
    st.info(
        "**Important**: LLM systems may hallucinate or misinterpret evidence. "
        "All claims in this report should be verified against the original documents. "
        "Use this tool to augment human analysis, not replace it."
    )
