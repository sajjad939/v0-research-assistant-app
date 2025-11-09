# Multi-Agent Research Assistant

A Streamlit application that uses multiple specialized AI agents to collaboratively analyze research documents and generate verified insight reports with explicit citations.

## Features

- **Document Ingestion**: Upload PDF, TXT files or paste research content
- **Intelligent Parsing**: Automatic extraction of metadata (title, authors, year, datasets, metrics)
- **Multi-Agent Analysis**: 2-6 specialized agents with distinct roles:
  - **Researcher**: Summarizes and extracts key claims
  - **Reviewer**: Critiques methodology and identifies weaknesses
  - **Synthesizer**: Aggregates findings and identifies consensus/contradictions
  - **DataInspector** (optional): Compares metrics and datasets
  - **CitationGuard** (optional): Ensures verifiable citations
- **Iterative Reasoning**: Configurable analysis rounds (1-6) for refined conclusions
- **Citation Tracking**: All claims linked to specific document chunks with confidence scores
- **Agent Graph Visualization**: See how agents influenced each other through reasoning
- **Export Formats**: Generate reports as Markdown or JSON

## Installation

### Local Development

1. Clone the repository:
\`\`\`bash
git clone <repository-url>
cd multi-agent-research-assistant
\`\`\`

2. Create virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Set up environment variables (optional):
\`\`\`bash
# For OpenAI API support (future enhancement)
export OPENAI_API_KEY="sk-..."
\`\`\`

5. Run locally:
\`\`\`bash
streamlit run streamlit_app.py
\`\`\`

The app will open at `http://localhost:8501`

## Usage

### Basic Workflow

1. **Upload Documents**
   - Click "Upload Documents" in the sidebar
   - Select 1-20 PDF or TXT files
   - Click "Process Uploads" to parse and extract metadata

2. **Configure Analysis**
   - Set number of agents (2-6)
   - Choose analysis rounds (1-6)
   - Enable/disable specific agent roles
   - Adjust citation strictness level

3. **Run Analysis**
   - Click "Run Agent Analysis" in the center column
   - Monitor progress as agents analyze documents
   - View real-time conversation stream

4. **Review Results**
   - Read final report in right column
   - Expand evidence sections for citations
   - View agent interaction graph
   - Export as Markdown or JSON

### Configuration

#### Number of Agents
- **2 agents**: Basic (Researcher + Reviewer)
- **3 agents**: Add Synthesizer
- **4 agents**: Add DataInspector
- **5-6 agents**: Add CitationGuard and optional moderator

#### Analysis Rounds
- More rounds = deeper analysis but longer processing
- Recommended: 3-4 rounds for comprehensive insights

#### Citation Strictness
- **Lenient**: Allows inferred claims
- **Moderate**: Balanced approach (default)
- **Strict**: Requires explicit evidence
- **Very Strict**: Only direct quotes

## API Architecture

### Core Modules

#### `ingestion.py`
\`\`\`python
DocumentProcessor:
  - read_pdf(file_obj) -> str
  - extract_chunks(text, chunk_size=1000) -> List[DocumentChunk]
  - parse_metadata(text, filename) -> Dict
\`\`\`

#### `agents.py`
\`\`\`python
BaseAgent (ABC):
  - act(context, documents, metadata) -> AgentMessage
  
Concrete agents: ResearcherAgent, ReviewerAgent, SynthesizerAgent, 
  DataInspectorAgent, CitationGuardAgent

AgentOrchestrator:
  - run(documents, metadata) -> (List[Dict], Dict)
\`\`\`

#### `reports.py`
\`\`\`python
ReportGenerator:
  - generate(messages, documents, metadata) -> Dict
\`\`\`

#### `utils.py`
Utilities for citation formatting, graph construction, text processing

### Data Structures

**AgentMessage**
\`\`\`python
{
    "agent": "Researcher",
    "round": 2,
    "summary": "Analysis summary...",
    "evidence": [
        {
            "doc_id": "paper-03",
            "chunk_id": 5,
            "highlight": "Relevant text..."
        }
    ],
    "confidence": 0.85
}
\`\`\`

**DocumentChunk**
\`\`\`python
{
    "content": "Chunk text...",
    "chunk_id": 0,
    "page_num": 1,
    "start_char": 0
}
\`\`\`

## Testing

Run tests locally:
\`\`\`bash
pytest tests/ -v
\`\`\`

Test coverage includes:
- Document parsing and chunking
- Agent message generation
- Orchestration coordination
- Mock LLM functionality

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (https://streamlit.io/cloud)

### Deployment Steps

1. Push code to GitHub:
\`\`\`bash
git add .
git commit -m "Deploy multi-agent research assistant"
git push origin main
\`\`\`

2. Connect to Streamlit Cloud:
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your GitHub repository
   - Choose `streamlit_app.py` as the main file

3. Set environment variables:
   - In Streamlit Cloud dashboard, go to Settings
   - Add secrets for `OPENAI_API_KEY` if needed

4. Deploy:
   - Click "Deploy"
   - Your app will be live at `https://share.streamlit.io/[username]/[repo-name]`

## Advanced Usage

### Using Custom LLM Models

The agents use a mock LLM system. To integrate OpenAI or other providers:

1. Add API key to environment variables
2. Update agent prompts in `agents.py`
3. Implement LLM calls in `act()` methods

### Batch Processing

For analyzing multiple document sets:
\`\`\`python
for dataset in datasets:
    orchestrator = AgentOrchestrator(...)
    messages, graph = orchestrator.run(dataset['documents'], dataset['metadata'])
    # Process results
\`\`\`

### Custom Agent Roles

Create new agent by extending `BaseAgent`:
\`\`\`python
class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("CustomRole")
    
    def act(self, context, documents, metadata):
        # Your analysis logic
        return self._create_message(summary, evidence, confidence, context["round"])
\`\`\`

## Troubleshooting

**Q: Documents aren't being parsed**
A: Ensure PDFs are text-based (not scanned images). For scanned PDFs, use OCR first.

**Q: Agent analysis is slow**
A: Reduce number of documents or analysis rounds. Process high-volume documents in batches.

**Q: Missing citations in output**
A: Increase citation strictness level. Ensure documents contain sufficient metadata.

**Q: Agents repeating same claims**
A: Reduce analysis rounds or adjust agent prompts for diversity.

## Performance Considerations

- **Memory**: In-memory session storage supports up to 20 medium documents
- **Processing**: ~2-3 seconds per agent per round
- **Scalability**: For 50+ documents, consider database backend

## Future Enhancements

- OpenAI/Anthropic LLM integration
- Knowledge graph export (RDF/JSON-LD)
- Obsidian/Notion export
- Advanced visualization with D3.js
- Batch processing queue
- User authentication and history

## Ethics & Limitations

**Important**: This system uses AI agents that may:
- Generate plausible but incorrect information
- Misinterpret or hallucinate evidence
- Have biases from training data

**Recommendations**:
- Always verify claims against original documents
- Use as research augmentation tool, not replacement
- Be cautious with high-stakes decisions
- Cite original sources in final outputs

## License

MIT License

## Support

For issues or questions:
1. Check the README FAQ section
2. Review test cases for usage examples
3. Check GitHub issues
4. Open new issue with detailed description

## Citation

If you use this tool in research, please cite:
\`\`\`
Multi-Agent Research Assistant (2024)
https://github.com/[username]/multi-agent-research-assistant
