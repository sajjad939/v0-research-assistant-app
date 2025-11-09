import pytest
from agents import ResearcherAgent, ReviewerAgent, SynthesizerAgent, AgentOrchestrator

def test_researcher_agent():
    """Test Researcher agent output."""
    agent = ResearcherAgent()
    
    context = {"round": 1}
    documents = [{"id": "doc_0", "chunks": ["chunk1", "chunk2"]}]
    metadata = {"doc_0": {"word_count": 5000}}
    
    message = agent.act(context, documents, metadata)
    
    assert message.agent == "Researcher"
    assert message.confidence > 0
    assert len(message.evidence) > 0

def test_reviewer_agent():
    """Test Reviewer agent output."""
    agent = ReviewerAgent()
    
    context = {"round": 1}
    messages = agent.act(context, [], {})
    
    assert messages.agent == "Reviewer"
    assert "critique" in messages.summary.lower() or "concern" in messages.summary.lower()

def test_agent_orchestrator():
    """Test orchestrator coordination."""
    config = {
        "Researcher": True,
        "Reviewer": True,
        "Synthesizer": True,
        "DataInspector": False,
        "CitationGuard": False
    }
    
    orchestrator = AgentOrchestrator(agents_config=config, num_rounds=2)
    documents = [{"id": "doc_0", "chunks": ["test"]}]
    metadata = {"doc_0": {"word_count": 1000}}
    
    messages, graph = orchestrator.run(documents, metadata)
    
    assert len(messages) > 0
    assert len(graph["nodes"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
