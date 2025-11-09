import json
from typing import List, Dict, Optional
import hashlib

def format_citations(evidence_list: List[Dict]) -> str:
    """Format evidence into readable citations."""
    citations = []
    for ev in evidence_list:
        doc_id = ev.get("doc_id", "unknown")
        chunk_id = ev.get("chunk_id", 0)
        citations.append(f"[{doc_id}:{chunk_id}]")
    return " ".join(citations)

def create_agent_graph(messages: List[Dict]) -> Dict:
    """Create graph structure from agent messages."""
    nodes = []
    edges = []
    
    seen_agents = set()
    for msg in messages:
        agent = msg.get("agent", "unknown")
        round_num = msg.get("round", 0)
        node_id = f"{agent}_r{round_num}"
        
        if node_id not in seen_agents:
            nodes.append({
                "id": node_id,
                "label": f"{agent} (Round {round_num})",
                "agent": agent,
                "round": round_num,
                "confidence": msg.get("confidence", 0)
            })
            seen_agents.add(node_id)
    
    # Create sequential edges
    for i in range(len(nodes) - 1):
        edges.append({
            "source": nodes[i]["id"],
            "target": nodes[i + 1]["id"],
            "label": "message_flow"
        })
    
    return {"nodes": nodes, "edges": edges}

def render_agent_graph(graph: Dict):
    """Render graph visualization (basic text representation)."""
    import streamlit as st
    
    st.write("**Agent Communication Graph:**")
    st.write(f"Nodes: {len(graph.get('nodes', []))} | Edges: {len(graph.get('edges', []))}")
    
    # Simple text-based visualization
    for node in graph.get("nodes", []):
        st.write(f"• {node['label']} (confidence: {node.get('confidence', 0):.1%})")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks

def extract_key_phrases(text: str, num_phrases: int = 5) -> List[str]:
    """Extract key phrases from text."""
    import re
    
    # Simple heuristic: extract noun phrases
    phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    return list(set(phrases))[:num_phrases]

def similarity_score(text1: str, text2: str) -> float:
    """Calculate simple text similarity."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0

def generate_evidence_hash(evidence: Dict) -> str:
    """Create unique identifier for evidence."""
    content = json.dumps(evidence, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()[:8]
