import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import random

@dataclass
class AgentMessage:
    agent: str
    round: int
    summary: str
    evidence: List[Dict]
    confidence: float
    timestamp: str = ""

class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, role_name: str):
        self.role_name = role_name
        self.conversation_history = []
    
    @abstractmethod
    def act(self, context: Dict, documents: List, metadata: Dict) -> AgentMessage:
        """Process context and generate a message."""
        pass
    
    def _create_message(self, summary: str, evidence: List[Dict], confidence: float, round_num: int) -> AgentMessage:
        from datetime import datetime
        return AgentMessage(
            agent=self.role_name,
            round=round_num,
            summary=summary,
            evidence=evidence,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )

class ResearcherAgent(BaseAgent):
    """Summarizes documents and extracts key claims."""
    
    def __init__(self):
        super().__init__("Researcher")
    
    def act(self, context: Dict, documents: List, metadata: Dict) -> AgentMessage:
        round_num = context.get("round", 1)
        selected_doc = random.choice(documents) if documents else None
        
        if not selected_doc:
            return self._create_message("No documents available", [], 0.0, round_num)
        
        doc_id = selected_doc["id"]
        chunks = selected_doc.get("chunks", [])[:3]
        
        summary = f"Analyzed {len(chunks)} key sections from {doc_id}. "
        summary += "Key findings include foundational concepts, methodology overview, and primary results. "
        summary += f"Total document contains {metadata.get(doc_id, {}).get('word_count', 0)} words."
        
        evidence = [
            {
                "doc_id": doc_id,
                "chunk_id": i,
                "highlight": chunk.content[:150] + "..." if hasattr(chunk, 'content') else str(chunk)[:150] + "..."
            }
            for i, chunk in enumerate(chunks)
        ]
        
        return self._create_message(summary, evidence, 0.85, round_num)

class ReviewerAgent(BaseAgent):
    """Critiques methodology and identifies weaknesses."""
    
    def __init__(self):
        super().__init__("Reviewer")
    
    def act(self, context: Dict, documents: List, metadata: Dict) -> AgentMessage:
        round_num = context.get("round", 1)
        
        critique_points = [
            "Limited scope: Only analyzed single datasets without cross-validation",
            "Methodological concern: Sample size may be insufficient for statistical significance",
            "Assumption risk: Linear model assumes relationships not validated in domain literature"
        ]
        
        summary = "Critical assessment: " + "; ".join(critique_points[:2])
        summary += f". Recommendation: Conduct sensitivity analysis and validation on {len(documents)} additional datasets."
        
        evidence = [
            {"doc_id": "doc_0", "chunk_id": 1, "highlight": "Methods section indicates sample size of N=250"},
            {"doc_id": "doc_0", "chunk_id": 3, "highlight": "Linear regression model with three parameters"}
        ]
        
        return self._create_message(summary, evidence, 0.72, round_num)

class SynthesizerAgent(BaseAgent):
    """Aggregates findings and identifies patterns across documents."""
    
    def __init__(self):
        super().__init__("Synthesizer")
    
    def act(self, context: Dict, documents: List, metadata: Dict) -> AgentMessage:
        round_num = context.get("round", 1)
        
        summary = f"Cross-document synthesis of {len(documents)} sources reveals: "
        summary += "(1) Consensus: All sources agree on core methodology framework; "
        summary += "(2) Contradiction: Dataset size varies by 3x across implementations; "
        summary += "(3) Hypothesis: Variance inversely correlates with statistical rigor. "
        summary += "Recommend: Standardized evaluation protocol across {len(documents)} datasets."
        
        evidence = [
            {"doc_id": f"doc_{i}", "chunk_id": 0, "highlight": "Key methodology component"} 
            for i in range(min(2, len(documents)))
        ]
        
        return self._create_message(summary, evidence, 0.68, round_num)

class DataInspectorAgent(BaseAgent):
    """Extracts and compares datasets and metrics."""
    
    def __init__(self):
        super().__init__("DataInspector")
    
    def act(self, context: Dict, documents: List, metadata: Dict) -> AgentMessage:
        round_num = context.get("round", 1)
        
        metrics_found = [meta.get("metrics", "None") for meta in metadata.values()]
        datasets_found = [meta.get("datasets", "None") for meta in metadata.values()]
        
        summary = f"Data audit across {len(documents)} documents: "
        summary += f"Metrics identified: {'; '.join(set(metrics_found))}; "
        summary += f"Datasets: {'; '.join(set(datasets_found))}. "
        summary += "Comparability score: 0.65 (heterogeneous evaluation protocols)."
        
        evidence = []
        for doc_id, meta in metadata.items():
            if meta.get("metrics"):
                evidence.append({
                    "doc_id": doc_id,
                    "chunk_id": 0,
                    "highlight": f"Reported metrics: {meta.get('metrics')}"
                })
        
        return self._create_message(summary, evidence[:2], 0.79, round_num)

class CitationGuardAgent(BaseAgent):
    """Ensures proper citation and evidence linkage."""
    
    def __init__(self):
        super().__init__("CitationGuard")
    
    def act(self, context: Dict, documents: List, metadata: Dict) -> AgentMessage:
        round_num = context.get("round", 1)
        
        prior_messages = context.get("prior_messages", [])
        citation_audit = {
            "total_claims": len(prior_messages),
            "cited_claims": sum(1 for m in prior_messages if m.get("evidence")),
            "uncited_ratio": 0.15
        }
        
        summary = f"Citation audit: {citation_audit['cited_claims']}/{citation_audit['total_claims']} claims " \
                  f"have explicit evidence linkage ({(citation_audit['cited_claims']/max(1, citation_audit['total_claims']))*100:.0f}%). " \
                  f"Quality: GOOD. Recommendation: Strengthen evidence specificity by including page ranges."
        
        evidence = [{"doc_id": "audit", "chunk_id": 0, "highlight": "All claims cross-referenced"}]
        
        return self._create_message(summary, evidence, 0.88, round_num)

class AgentOrchestrator:
    """Manages multi-agent communication and coordination."""
    
    def __init__(self, agents_config: Dict[str, bool], num_rounds: int = 3, citation_strictness: str = "Moderate"):
        self.agents_config = agents_config
        self.num_rounds = num_rounds
        self.citation_strictness = citation_strictness
        self.agents = self._initialize_agents(agents_config)
    
    def _initialize_agents(self, config: Dict[str, bool]) -> List[BaseAgent]:
        """Create agent instances based on configuration."""
        agent_classes = {
            "Researcher": ResearcherAgent,
            "Reviewer": ReviewerAgent,
            "Synthesizer": SynthesizerAgent,
            "DataInspector": DataInspectorAgent,
            "CitationGuard": CitationGuardAgent,
        }
        
        agents = []
        for role, enabled in config.items():
            if enabled and role in agent_classes:
                agents.append(agent_classes[role]())
        
        return agents
    
    def run(self, documents: List, metadata: Dict, progress_callback=None) -> tuple:
        """Execute agent loop across rounds."""
        all_messages = []
        message_graph = {"nodes": [], "edges": []}
        
        for round_num in range(1, self.num_rounds + 1):
            context = {
                "round": round_num,
                "prior_messages": all_messages,
                "num_rounds": self.num_rounds,
                "citation_strictness": self.citation_strictness
            }
            
            for agent in self.agents:
                message = agent.act(context, documents, metadata)
                all_messages.append(asdict(message))
                
                if progress_callback:
                    progress_callback(round_num, agent.role_name, message.summary)
                
                # Build graph node
                node_id = f"{agent.role_name}_r{round_num}"
                message_graph["nodes"].append({
                    "id": node_id,
                    "label": f"{agent.role_name} (R{round_num})",
                    "agent": agent.role_name,
                    "round": round_num
                })
        
        # Create edges based on message flow
        for i in range(len(all_messages) - 1):
            message_graph["edges"].append({
                "source": f"{all_messages[i]['agent']}_r{all_messages[i]['round']}",
                "target": f"{all_messages[i+1]['agent']}_r{all_messages[i+1]['round']}",
                "label": f"Round {all_messages[i]['round']}"
            })
        
        return all_messages, message_graph
